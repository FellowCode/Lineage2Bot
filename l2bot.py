from functions import get_screen, find_template, get_screen_cv, load_img_cv, img_to_cv, invert_top_pos, color_equal, \
    get_windows_hwnd
from time import sleep
import time
from colors import GraciaColors
from multiprocessing import Process, Value, Array
import os
from threading import Thread, Timer
import serial
import win32gui

from windows_settings import WindowInfo
import win32com.client

shell = win32com.client.Dispatch("WScript.Shell")


class ValuesMonitor(Thread):
    work = True

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.pause = False

    def run(self):
        while self.work:
            if not self.pause:
                self.app.l2_window.update()
                self.app.update_values()
            else:
                sleep(0.3)

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
        self.msg = None
        self.connect()
        self.daemon = True

    def run(self):
        while self.work:
            if self.msg:
                self.serial.write(self.msg)
                self.msg = None
            sleep(0.01)

    def send(self, msg):
        self.msg = str(str(msg) + '\n').encode()

    def connect(self):
        self.serial = serial.Serial(self.com, 115200, timeout=0)

    def stop(self):
        self.work = False
        self.serial.close()


class LineageWindow:
    from threading import Timer

    def __init__(self, window_settings, app, window_i=0):
        self.window_settings = window_settings
        self.window_i = window_i
        self.app = app
        self.hwnd = get_windows_hwnd(self.window_settings['name'])[0]
        self.using_skill = False
        self.target_change = False

    def click_btn(self, btn_code):
        print('click_btn', self.window_i, btn_code)
        self.set_fg_window()
        self.app.serial_sender.send(btn_code)
        sleep(0.1)

    def set_fg_window(self):
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(self.hwnd)
        sleep(0.1)

    def update_window_settings(self, windows_settings):
        self.window_settings = windows_settings[self.window_i]

    def triggers_exec(self, hp, mp, target_hp, last_target_hp, party_hps, party_mps):
        if self.window_i > 0:
            party_hps.insert(0, hp)
            party_mps.insert(0, mp)
            hp = party_hps.pop(self.window_i), hp
            mp = party_mps.pop(self.window_i), mp
        for trigger_name in WindowInfo.ordering:
            triggers = self.window_settings['triggers'][trigger_name]
            for trigger in triggers:
                if trigger_name == 'hp_lt' and trigger['percent'] > hp and trigger.get('ready', True) and not self.using_skill:
                    self.click_btn(trigger['btn'])
                    self.use_cooldown_skill(trigger)
                    print('trigger', 'hp_lt')
                if trigger_name == 'mp_lt' and trigger['percent'] > mp and trigger.get('ready', True) and not self.using_skill:
                    self.click_btn(trigger['btn'])
                    self.use_cooldown_skill(trigger)
                    print('trigger', 'mp_lt')
                if trigger_name == 'hp_party_lt' and trigger['percent'] > min(party_hps) and trigger.get('ready', True) and not self.using_skill:
                    p_index = self.get_party_index(party_hps)
                    self.click_btn(14+p_index)
                    self.click_btn(trigger['btn'])
                    self.use_cooldown_skill(trigger)
                    print('trigger', 'hp_party_lt')
                if trigger_name == 'mp_party_lt' and trigger['percent'] > min(party_mps) and trigger.get('ready', True) and not self.using_skill:
                    p_index = self.get_party_index(party_mps)
                    self.click_btn(14+p_index)
                    self.click_btn(trigger['btn'])
                    self.use_cooldown_skill(trigger)
                    print('trigger', 'mp_party_lt')
                if trigger_name == 'mob_dead' and target_hp == 0 and last_target_hp > 0 and trigger.get('ready', True) and not self.using_skill:
                    self.click_btn(trigger['btn'])
                    self.use_cooldown_skill(trigger)
                    print('trigger', 'mob_dead')
                if trigger_name == 'no_target' and target_hp == 0 and last_target_hp == 0 and trigger.get('ready', True) and not self.using_skill:
                    self.click_btn(trigger['btn'])
                    self.use_cooldown_skill(trigger)
                    print('trigger', 'no_target')
                if trigger_name == 'target_hp' and target_hp > trigger['percent'] and trigger.get('ready', True) and not self.using_skill and self.target_change:
                    self.click_btn(trigger['btn'])
                    self.use_cooldown_skill(trigger)
                    self.target_change = False
                    print('trigger', 'target_hp')
                if trigger_name == 'buff' and trigger.get('ready', True) and not self.using_skill:
                    self.click_btn(trigger['btn'])
                    self.use_cooldown_skill(trigger)
                    print('trigger', 'buff')

    def use_skill(self, trigger):
        def used(self):
            self.using_skill = False

        if trigger.get('use_time', 0) > 0:
            self.using_skill = True
            Timer(trigger.get('use_time', 0), lambda a=self: used(a)).start()

    def use_cooldown_skill(self, trigger):
        self.use_skill(trigger)

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


class MainLineageWindow(LineageWindow):
    stat_pos = (0, 0)
    target_pos = (0, 0)
    screen = None
    hp = mp = target_hp = -1

    def __init__(self, app):

        self.support_windows = []

        self.update_windows_settings()

        for i in range(1, 9, 1):
            if self.windows_settings[i]['active'] == 1:
                self.support_windows.append(LineageWindow(self.windows_settings[i], app, window_i=i))
        super().__init__(self.windows_settings[0], app)
        self.last_target_hp = 0
        self.update_window_info()
        self.thp_100_count = 0


    def update_window_info(self):
        rect = win32gui.GetWindowRect(self.hwnd)
        x = rect[0] + 8
        y = rect[1] + 32
        w = rect[2] - x - 8
        h = rect[3] - y - 8
        self.pos = (x, y)
        self.size = (w, h)
        self.box = (self.pos[0], self.pos[1], self.pos[0] + self.size[0], self.pos[1] + self.size[1])

    def update_windows_settings(self):
        self.windows_settings = WindowInfo()
        self.window_settings = self.windows_settings[0]
        for sup_wind in self.support_windows:
            sup_wind.update_window_settings(self.windows_settings)

    def update_screen(self):
        self.update_window_info()
        self.set_fg_window()
        self.screen = get_screen().crop(self.box)

    def save_screen(self):
        self.update_screen()
        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        self.screen.save('tmp\\l2.jpg', 'JPEG', quality=100)

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

    def calibration(self):
        self.save_screen()

        start_time = time.time()

        stat_pos = Array('i', range(2))
        target_pos = Array('i', range(2))
        party_pos = Array('i', range(2))
        screen_cv = img_to_cv(self.screen)
        processes = []
        processes.append(Process(target=self.get_template_pos, args=(stat_pos, screen_cv, 'templates\\hp.jpg')))
        processes.append(Process(target=self.get_template_pos, args=(target_pos, screen_cv, 'templates\\target.jpg')))
        processes.append(Process(target=self.get_template_pos, args=(party_pos, screen_cv, 'templates\\party.jpg')))

        for proc in processes:
            proc.start()
        for proc in processes:
            proc.join()

        if stat_pos[0] != -1:
            self.stat_pos = [stat_pos[0], stat_pos[1]]

        if target_pos[0] != -1:
            self.target_pos = [target_pos[0], target_pos[1]]

        if party_pos[0] != -1:
            self.party_pos = [party_pos[0], party_pos[1]]

        hp_start_pos = (self.stat_pos[0] + 50, self.stat_pos[1])

        self.hp_line = self.get_value_line(hp_start_pos, 100, GraciaColors.hp)
        self.mp_line = self.get_value_line(hp_start_pos, 100, GraciaColors.mp)

        if hasattr(self, 'target_pos'):
            target_start_pos = (self.target_pos[0] + 40, self.target_pos[1])
            self.target_hp_line = self.get_value_line(target_start_pos, 100, GraciaColors.target_hp)

        if hasattr(self, 'party_pos'):
            party_start_pos = (self.party_pos[0] + 40, self.party_pos[1])
            self.party_hp_lines = [self.get_value_line(party_start_pos, 100, GraciaColors.target_hp)]
            self.party_mp_lines = [self.get_value_line(party_start_pos, 100, GraciaColors.mp)]
            while True:
                party_start_pos = (party_start_pos[0], self.party_hp_lines[-1][1] + 20)
                self.party_hp_lines.append(self.get_value_line(party_start_pos, 100, GraciaColors.target_hp))
                self.party_mp_lines.append(self.get_value_line(party_start_pos, 100, GraciaColors.mp))
                if not self.party_hp_lines[-1] or not self.party_mp_lines[-1]:
                    del self.party_hp_lines[-1]
                    del self.party_mp_lines[-1]
                    break
            print(self.party_mp_lines)

        print('calibration time:', time.time() - start_time)

    def update(self):
        """ Bot Loop """
        self.update_screen()
        if hasattr(self, 'hp_line'):
            self.hp = self.get_percent_value(self.hp_line, GraciaColors.hp)
        if hasattr(self, 'mp_line'):
            self.mp = self.get_percent_value(self.mp_line, GraciaColors.mp)
        if hasattr(self, 'target_hp_line'):
            self.target_hp = self.get_percent_value(self.target_hp_line, GraciaColors.target_hp, digits_on_line=False)
        self.party_hps = []
        if hasattr(self, 'party_hp_lines'):
            for line in self.party_hp_lines:
                self.party_hps.append(self.get_percent_value(line, GraciaColors.target_hp, digits_on_line=False))
        self.party_mps = []
        if hasattr(self, 'party_mp_lines'):
            for line in self.party_mp_lines:
                self.party_mps.append(self.get_percent_value(line, GraciaColors.mp, digits_on_line=False))

        if self.target_hp == 100:
            self.thp_100_count += 1
        if self.thp_100_count == 5:
            self.target_hp = 0
            self.last_target_hp = 0
        if self.target_hp < 100:
            self.thp_100_count = 0

        if self.target_hp == 0:
            self.target_change = True

        self.triggers_exec(self.hp, self.mp, self.target_hp, self.last_target_hp, self.party_hps, self.party_mps)

        for sup_win in self.support_windows:
            sup_win.triggers_exec(self.hp, self.mp, self.target_hp, self.last_target_hp, self.party_hps, self.party_mps)

        self.last_target_hp = self.target_hp



    def get_percent_value(self, line, color, digits_on_line=True):
        left = line[0]
        top = line[1]
        width = line[2] - left
        current_right = left
        rgb_screen = self.screen.convert('RGB')

        if color_equal(rgb_screen.getpixel((left, top)), color):
            i = counter = 0
            while True:
                pixel = rgb_screen.getpixel((left + i, top))
                if color_equal(pixel, color):
                    current_right = left + i
                    counter = 0
                    if digits_on_line:
                        step = 2
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
            return int((current_right - left) / width * 100)
        else:
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
