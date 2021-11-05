import win32api

import settings
from functions import get_screen, find_template, load_img_cv, img_to_cv, color_equal, get_windows_hwnd
from time import sleep
import time
from colors import GraciaColors
from multiprocessing import Process, Array
import os
from threading import Thread, Timer
import serial
import win32gui
from windows_settings import WindowInfo
import win32com.client
import math

shell = win32com.client.Dispatch("WScript.Shell")


class ValuesMonitor:
    work = False
    pause = False

    def __init__(self, app):
        super().__init__()
        self.app = app

    def values_updater(self):
        while self.work:
            if not self.pause:
                self.app.l2_window.update_values()
                self.app.update_values()
                sleep(.02)
            else:
                sleep(.1)

    def trigger_executer(self):
        while self.work:
            if not self.pause:
                l2win = self.app.l2_window
                l2win.triggers_exec(l2win.hp, l2win.mp, l2win.target_hp, l2win.party_hps, l2win.party_mps)
                for sup_win in self.app.l2_window.support_windows:
                    sup_win.triggers_exec(l2win.hp, l2win.mp, l2win.target_hp, l2win.party_hps, l2win.party_mps)
                sleep(.02)
            else:
                sleep(.1)

    def start(self):
        self.work = True
        self.pause = False
        Thread(target=self.values_updater, daemon=True).start()
        Thread(target=self.trigger_executer, daemon=True).start()

    def stop(self):
        self.work = False


class FindTemplate(Thread):
    def __init__(self, window, var_name, template_path):
        super().__init__()
        self.window = window
        self.path = template_path
        self.var_name = 'self.window.' + var_name

    def get_template_pos(self):
        try:
            screen_cv = img_to_cv(self.window.screen)
            pos = find_template(screen_cv, load_img_cv(self.path), 0)
            i = 0
            while not pos and i < 5:
                i += 1
                pos = find_template(screen_cv, load_img_cv(self.path), i)
            return pos
        except:
            return None

    def run(self):
        print('start', self.path)
        exec(self.var_name + ' = self.get_template_pos()')
        print('end', self.path)


class SerialSender(Thread):
    def __init__(self, com):
        super().__init__()
        self.work = True
        self.serial = None
        self.com = com
        self.msg = []
        self.connect()
        self.daemon = True

    def run(self):
        while self.work:
            if len(self.msg) > 0:
                self.serial.write(self.msg.pop(0))

    def send(self, msg):
        self.msg.append(str(str(msg) + ';').encode())

    def connect(self):
        self.serial = serial.Serial(self.com, 115200, timeout=0)
        pass

    def stop(self):
        self.work = False
        self.serial.close()


class LineageWindow:

    def __init__(self, window_settings, app, window_i=0):
        self.cur_target = -1
        self.window_settings = window_settings
        self.window_i = window_i
        self.app = app
        print(self.window_settings['name'])
        self.hwnd = get_windows_hwnd(self.window_settings['name'] + settings.WINDOW_NAME_POSTFIX)[0]
        self.using_skill = False
        self.target_change = False
        self.cyclic_uid = ''

    def click_btn(self, btn_code, press=False):
        self.set_fg_window()
        if press:
            btn_code += " press"
        print('click_btn', self.window_i, btn_code)
        self.app.serial_sender.send(btn_code)
        sleep(0.01)

    def mouse_move_to(self, target_x, target_y):
        while True:
            cursor_x, cursor_y = win32api.GetCursorPos()
            x = (target_x - cursor_x)//2
            y = (target_y - cursor_y)//2
            self.app.serial_sender.send(f'mouse move {int(x)} {int(y)}')
            sleep(0.01)
            c_x, c_y = win32api.GetCursorPos()
            if abs(target_x-c_x) < 7 and abs(target_y-c_y) < 7:
                break

    def mouse_click(self):
        self.set_fg_window()
        self.app.serial_sender.send('mouse click left')

    def set_fg_window(self):
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(self.hwnd)
        sleep(0.02)

    def update_window_settings(self, windows_settings):
        self.window_settings = windows_settings[self.window_i]

    def can_use(self, trigger):
        return trigger.get('ready', True) and not self.using_skill

    def triggers_exec(self, hp, mp, target_hp, party_hps, party_mps):
        if self.window_i > 0:
            party_hps.insert(0, hp)
            party_mps.insert(0, mp)
            hp = party_hps.pop(self.window_i)
            mp = party_mps.pop(self.window_i)

        if hp == 0:
            self.update_window_info()
            btn_pos_x = self.pos[0] + self.size[0] // 2 - 44
            btn_pos_y = self.pos[1] + self.size[1] // 2 + 47
            self.mouse_move_to(btn_pos_x, btn_pos_y)
            self.mouse_click()
            sleep(.1)
            return

        party_hp = 100
        party_hp_i = 0
        party_dead_i = -1
        for i, php in enumerate(party_hps):
            if 0 < php < party_hp:
                party_hp = php
                party_hp_i = i
            if php == 0:
                party_dead_i = i

        for t_name in WindowInfo.ordering:
            triggers = self.window_settings['triggers'][t_name]
            used = False
            for t in triggers:
                if t_name == 'hp_lt' and t['percent_low'] <= hp <= t['percent_high'] and self.can_use(t):
                    self.use_cooldown_skill(t)
                    print('trigger', t_name)
                    used = True
                if t_name == 'mp_lt' and t['percent_low'] <= mp <= t['percent_high'] and self.can_use(t):
                    self.use_cooldown_skill(t)
                    print('trigger', t_name)
                    used = True
                if t_name == 'party_dead' and party_dead_i >= 0 and self.can_use(t):
                    if self.cur_target != party_dead_i + 2:
                        self.click_btn(party_dead_i + 2)
                        self.cur_target = party_dead_i + 2
                    self.use_cooldown_skill(t)
                    print('trigger', t_name)
                    used = True
                if t_name == 'hp_party' and t['percent_low'] <= party_hp <= t['percent_high'] and self.can_use(t):
                    if self.cur_target != party_hp_i + 2:
                        self.click_btn(party_hp_i + 2)
                        self.cur_target = party_hp_i + 2
                    self.use_cooldown_skill(t)
                    print('trigger', t_name)
                    used = True
                if t_name == 'target_hp' and t['percent_low'] <= target_hp <= t['percent_high'] and self.can_use(t):
                    self.use_cooldown_skill(t)
                    self.target_change = False
                    print('trigger', 'target_hp')
                    used = True
                if t_name == 'buff' and t.get('ready', True) and not self.using_skill:
                    self.use_cooldown_skill(t)
                    print('trigger', 'buff')
                    used = True
            if used:
                break

    def use_skill(self, trigger):
        def used(self):
            self.using_skill = False

        if trigger.get('use_time', 0) > 0:
            self.using_skill = True
            Timer(trigger.get('use_time', 0), lambda a=self: used(a)).start()

    def use_cooldown_skill(self, trigger):
        self.use_skill(trigger)
        if trigger.get('to_self'):
            self.click_btn('1')
            self.cur_target = 'self'
        self.click_btn(trigger['btn'], press=trigger.get('press'))
        if trigger.get('to_self') and not trigger.get('press'):
            self.click_btn('ESC')

        def used(trigger):
            trigger['ready'] = True

        if trigger.get('cooldown', 0) > 0:
            trigger['ready'] = False
            Timer(trigger.get('cooldown', 0), lambda a=trigger: used(a)).start()

    def get_party_index(self, values_list):
        while True:
            try:
                return values_list.index(min(values_list))
            except:
                pass

    @staticmethod
    def get_template_pos(template_pos, screen_cv, path):
        try:

            pos = find_template(screen_cv, load_img_cv(path), 0)
            i = 0
            while not pos and i < 1:
                i += 1
                pos = find_template(screen_cv, load_img_cv(path), i)
            template_pos[0] = pos[0]
            template_pos[1] = pos[1]
            print(pos)
        except:
            template_pos[0] = -1
            template_pos[1] = -1

    def update_window_info(self):
        rect = win32gui.GetWindowRect(self.hwnd)
        x = rect[0] + 8
        y = rect[1] + 32
        w = rect[2] - x - 8
        h = rect[3] - y - 8
        self.pos = (x, y)
        self.size = (w, h)
        self.box = (self.pos[0], self.pos[1], self.pos[0] + self.size[0], self.pos[1] + self.size[1])

    def update_screen(self):
        self.update_window_info()
        self.set_fg_window()
        self.screen = get_screen(self.box)

    def find_res_btn(self):
        self.update_screen()

        left = (self.pos[0] + self.size[0]) // 2 - 200
        top = (self.pos[1] + self.size[1]) // 2 - 100
        right = (self.pos[0] + self.size[0]) // 2 + 200
        bottom = (self.pos[1] + self.size[1]) // 2 + 100

        self.screen = self.screen.crop((left, top, right, bottom))
        screen_cv = img_to_cv(self.screen)

        self.res_btn_pos = Array('i', range(2))
        self.find_res_process = Process(target=self.get_template_pos,
                                        args=(self.res_btn_pos, screen_cv, 'templates\\hp.jpg'))
        self.find_res_process.start()


class MainLineageWindow(LineageWindow):
    stat_pos = (0, 0)
    target_pos = (0, 0)
    screen = None
    hp = mp = target_hp = -1

    def __init__(self, app):
        self.load_calibration()
        self.support_windows = []

        self.update_windows_settings()

        for i in range(1, 9, 1):
            if self.windows_settings[i]['active'] == 1:
                self.support_windows.append(LineageWindow(self.windows_settings[i], app, window_i=i))
        super().__init__(self.windows_settings[0], app)
        self.last_target_hp = 0
        self.update_window_info()
        self.thp_100_count = 0

    def update_windows_settings(self):
        self.windows_settings = WindowInfo()
        self.window_settings = self.windows_settings[0]
        for sup_wind in self.support_windows:
            sup_wind.update_window_settings(self.windows_settings)

    def save_screen(self):
        self.update_screen()
        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        self.screen.save(f"tmp\\{self.window_settings['name']}.jpg", 'JPEG', quality=100)

    def calibration(self):
        self.save_screen()

        start_time = time.time()

        stat_pos = Array('i', range(2))
        target_pos = Array('i', range(2))
        party_pos = Array('i', range(2))
        screen_cv = img_to_cv(self.screen)
        processes = []
        processes.append(Process(target=self.get_template_pos, args=(stat_pos, screen_cv, 'templates\\hp_mw.jpg')))
        processes.append(
            Process(target=self.get_template_pos, args=(target_pos, screen_cv, 'templates\\target_mw.jpg')))
        processes.append(
            Process(target=self.get_template_pos, args=(party_pos, screen_cv, 'templates\\party_mw.jpg')))

        for proc in processes:
            proc.start()
        for proc in processes:
            proc.join()

        if stat_pos[0] != -1:
            self.stat_pos = [stat_pos[0], stat_pos[1]]
        else:
            self.stat_pos = None
            self.hp_line = None
            self.mp_line = None

        if target_pos[0] != -1:
            self.target_pos = [target_pos[0], target_pos[1]]
        else:
            self.target_pos = None
            self.target_hp_line = None

        if party_pos[0] != -1:
            self.party_pos = [party_pos[0], party_pos[1]]
        else:
            self.party_pos = None
            self.party_hp_lines = []
            self.party_mp_lines = []

        hp_start_pos = (self.stat_pos[0] + settings.HP_LEFT_OFFSET, self.stat_pos[1])

        self.hp_offset_line = [hp_start_pos[0] + settings.HP_LEFT_OFFSET, hp_start_pos[1], hp_start_pos[0] + settings.HP_LEFT_OFFSET, hp_start_pos[1] + settings.HP_MAX_HEIGHT]
        self.hp_line = self.get_value_line(hp_start_pos, settings.HP_MAX_HEIGHT, settings.COLORS.hp + settings.COLORS.hp_dark)
        self.mp_line = self.get_value_line(hp_start_pos, settings.HP_MAX_HEIGHT, settings.COLORS.mp)

        if self.target_pos:
            target_start_pos = (self.target_pos[0] + 80, self.target_pos[1])
            self.target_hp_line = self.get_value_line(target_start_pos, 100, settings.COLORS.hp + settings.COLORS.hp_dark)

        if self.party_pos:
            party_start_pos = (self.party_pos[0] + 80, self.party_pos[1])
            self.party_hp_lines = [self.get_value_line(party_start_pos, 100, settings.COLORS.hp + settings.COLORS.hp_dark)]
            self.party_mp_lines = [self.get_value_line(party_start_pos, 100, settings.COLORS.mp)]
            while True:
                print(self.party_hp_lines[-1])
                party_start_pos = (party_start_pos[0], self.party_hp_lines[-1][1] + 20)
                self.party_hp_lines.append(self.get_value_line(party_start_pos, 150, GraciaColors.party_hp + GraciaColors.party_hp_dark))
                self.party_mp_lines.append(self.get_value_line(party_start_pos, 150, GraciaColors.party_mp + GraciaColors.party_mp_dark))
                if not self.party_hp_lines[-1] or not self.party_mp_lines[-1]:
                    del self.party_hp_lines[-1]
                    del self.party_mp_lines[-1]
                    break
            print(self.party_mp_lines)

        print('calibration time:', time.time() - start_time)
        self.save_calibration()

    def load_calibration(self):
        try:
            with open('save/calibration.l2b', 'r') as f:
                d = eval(f.read())
                self.hp_line = d['hp']
                self.mp_line = d['mp']
                self.target_hp_line = d['target_hp']
                self.party_hp_lines = d['party_hps']
                self.party_mp_lines = d['party_mps']
                self.party_hps = []
                self.party_mps = []
        except:
            self.hp_line = [0, 0, 0, 0]
            self.mp_line = [0, 0, 0, 0]
            self.target_hp = [0, 0, 0, 0]
            self.party_hp_lines = []
            self.party_mp_lines = []
            self.party_hps = []
            self.party_mps = []
            print('cant load calibration')

    def save_calibration(self):
        with open('save/calibration.l2b', 'w') as f:
            d = {'hp': self.hp_line, 'mp': self.mp_line, 'target_hp': self.target_hp_line,
                 'party_hps': self.party_hp_lines, 'party_mps': self.party_mp_lines}
            f.write(str(d))

    def get_percent_thread(self, variable, line, colors):
        setattr(self, variable, self.get_percent_value(line, colors))

    def get_party_percent_thread(self, variable, lines, colors):
        for line in lines:
            getattr(self, variable).append(self.get_percent_value(line, colors, digits_on_line=False))

    def update_values(self):
        """ Bot Loop """
        start = time.time()
        self.update_screen()
        print('screnshot time', time.time() - start)
        if hasattr(self, 'hp_line'):
            self.get_percent_thread('hp', self.hp_line, GraciaColors.hp)
        if hasattr(self, 'mp_line'):
            self.get_percent_thread('mp', self.mp_line, GraciaColors.mp)
        if hasattr(self, 'target_hp_line'):
            self.get_percent_thread('target_hp', self.target_hp_line, GraciaColors.hp)

        self.party_hps = []
        self.get_party_percent_thread('party_hps', self.party_hp_lines, GraciaColors.party_hp)
        self.party_mps = []
        self.get_party_percent_thread('party_mps', self.party_mp_lines, GraciaColors.party_mp)

        # if self.target_hp == 100:
        #     self.thp_100_count += 1
        # if self.thp_100_count == 5:
        #     self.target_hp = 0
        #     self.last_target_hp = 0
        # if self.target_hp < 100:
        #     self.thp_100_count = 0
        #
        # if self.target_hp == 0:
        #     self.target_change = True

        self.last_target_hp = self.target_hp


        print('update values time', time.time() - start)

    def get_percent_value(self, line, color, digits_on_line=True):
        left = line[0]
        top = line[1]
        width = line[2] - left
        current_right = left
        rgb_screen = self.screen.convert('RGB')

        if color_equal(rgb_screen.getpixel((left, top)), color):
            if not digits_on_line:
                # binary search
                tmp_width = width // 2
                center = tmp_width + left
                pixel = rgb_screen.getpixel((center, top))
                for i in range(5):
                    tmp_width //= 2
                    if color_equal(pixel, color):
                        center += tmp_width
                    else:
                        center -= tmp_width
                    pixel = rgb_screen.getpixel((center, top))
                start_pixel = rgb_screen.getpixel((center, top))
                if color_equal(pixel, color) or color_equal(start_pixel, color):
                    return math.ceil((center - left) / width * 100)
                else:
                    return 0
            else:
                i = counter = 0
                while True:
                    pixel = rgb_screen.getpixel((left + i, top))
                    if color_equal(pixel, color):
                        current_right = left + i
                        counter = 0
                        if digits_on_line:
                            step = 10
                        else:
                            step = 10
                    else:
                        if not digits_on_line and counter == 0:
                            i -= 10
                        counter += 1
                        step = 1
                    if (not digits_on_line and counter > 5) or (digits_on_line and counter > 20) or left + i >= line[2]:
                        break
                    i += step
                return math.ceil((current_right - left) / width * 100)
        else:
            print('a')
            return 0

    def get_value_line(self, start_pos, max_height, color):
        top = start_pos[1]
        rgb_screen = self.screen.convert('RGB')
        pixel = rgb_screen.getpixel(start_pos)
        start_pos = list(start_pos)

        while not color_equal(pixel, color):
            start_pos[1] += 1
            if start_pos[1] == self.size[1] - 1 or start_pos[1] > top + max_height:
                return None
            pixel = rgb_screen.getpixel((start_pos[0], start_pos[1]))
            # if start_pos[1] > top+max_height:
            #     start_pos = [start_pos[0]+1, top]
        i = 1
        top = start_pos[1]
        left = right = start_pos[0]
        counter = 0
        while True:
            pixel = rgb_screen.getpixel((start_pos[0] - i, start_pos[1]))
            if color_equal(pixel, color):
                left = start_pos[0] - i
                counter = 0
            else:
                counter += 1
            if counter > 20:
                break
            if start_pos[0] + i == self.size[0]:
                return None
            i += 1
        i = 1
        counter = 0
        while True:
            pixel = rgb_screen.getpixel((start_pos[0] + i, start_pos[1]))
            if color_equal(pixel, color):
                right = start_pos[0] + i
                counter = 0
            else:
                counter += 1
            if counter > 20:
                break
            if start_pos[0] + i == self.size[0]:
                return None
            i += 1
        return [left, top, right, top]
