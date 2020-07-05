from functions import get_screen, find_template, get_screen_cv, load_img_cv, img_to_cv, invert_top_pos, color_equal
from time import sleep
import time
from colors import GraciaColors
from multiprocessing import Process, Value, Array
import os
from threading import Thread

import win32gui


class ValuesMonitor(Thread):
    work = True

    def __init__(self, app):
        super().__init__()
        self.app = app

    def run(self):
        while self.work:
            self.app.l2_window.update()
            self.app.update_values()
            sleep(0.5)

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


class LineageWindow:
    from threading import Timer

    def __init__(self, hwnd, attack=None, heal=None, recharge=None, buff=None, buff_time=1100):
        self.hwnd = hwnd
        self.attack = attack
        self.heal = heal
        self.recharge = recharge
        self.buff = buff
        self.buff_time = buff_time
        if buff:
            self.need_buff = True
        else:
            self.need_buff = False

    def use_buff(self):
        win32gui.SetForegroundWindow(self.hwnd)
        sleep(0.1)
        self.click_btn(self.buff)

        self.need_buff = False
        t = self.Timer(self.buff_time, self.set_need_buff)
        t.start()

    def use_heal(self):
        win32gui.SetForegroundWindow(self.hwnd)
        sleep(0.1)
        self.click_btn(self.heal)

    def use_recharge(self):
        win32gui.SetForegroundWindow(self.hwnd)
        sleep(0.1)
        self.click_btn(self.recharge)

    def use_attack(self):
        win32gui.SetForegroundWindow(self.hwnd)
        sleep(0.1)
        self.click_btn(self.attack)

    def set_need_buff(self):
        self.need_buff = True

    def click_btn(self, btn):
        pass


class MainLineageWindow(LineageWindow):
    stat_pos = (0, 0)
    target_pos = (0, 0)
    screen = None
    hp = mp = target_hp = -1

    def __init__(self, hwnd):
        super().__init__(hwnd)
        self.hwnd = hwnd
        self.update_window_info()

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
        try:
            win32gui.SetForegroundWindow(self.hwnd)
        except:
            pass
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
        self.update_screen()
        if hasattr(self, 'hp_line'):
            self.hp = self.get_percent_value(self.hp_line, GraciaColors.hp)
        if hasattr(self, 'mp_line'):
            self.mp = self.get_percent_value(self.mp_line, GraciaColors.mp)
        if hasattr(self, 'target_hp_line'):
            self.target_hp = self.get_percent_value(self.target_hp_line, GraciaColors.target_hp, digits_on_line=False)

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
