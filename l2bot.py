from functions import get_screen, get_window_info, find_template, get_screen_cv, load_img_cv, img_to_cv, invert_top_pos, color_equal
from time import sleep

from threading import Thread

import win32gui

class ValuesMonitor(Thread):
    work = True
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.daemon = True

    def run(self):
        while self.work:
            self.app.l2_window.update()
            self.app.update_values()
            sleep(0.2)

    def stop(self):
        self.work = False


class LineageWindow:
    stat_pos = (0, 0)
    target_pos = (0, 0)
    screen = None
    hp = mp = target_hp = -1
    def __init__(self):
        window_info = get_window_info()[0]
        self.hwnd = window_info['hwnd']
        self.pos = (window_info['x'], window_info['y']+24)
        self.size = (window_info['width'], window_info['height']-24)
        self.box = (self.pos[0], self.pos[1], self.pos[0]+self.size[0], self.pos[1]+self.size[1])

    def update_screen(self):
        try:
            win32gui.SetForegroundWindow(self.hwnd)
        except: pass
        self.screen = get_screen().crop(self.box)

    def save_screen(self):
        self.update_screen()
        self.screen.save('tmp\\l2.jpg', 'JPEG', quality=100)

    def calibration(self):
        screen_cv = img_to_cv(self.screen)
        self.stat_pos = find_template(screen_cv, load_img_cv('templates\\hp.jpg'), 1)
        try:
            self.target_pos = find_template(screen_cv, load_img_cv('templates\\target.jpg'), 3)
        except:
            self.target_pos = None

        hp_start_pos = (self.stat_pos[0]+50, self.stat_pos[1])

        self.hp_color = (128, 51, 41)
        hp_dark_color = (53, 32, 29)
        self.mp_color = (34, 75, 137)
        mp_dark_color = (34, 45, 63)

        self.hp_line = self.get_value_line(hp_start_pos, 100, self.hp_color, hp_dark_color)
        self.mp_line = self.get_value_line(hp_start_pos, 100, self.mp_color, mp_dark_color)

        if self.target_pos:
            target_start_pos = (self.target_pos[0]+40, self.target_pos[1])
            self.target_hp_color = (104, 26, 22)
            target_hp_dark_color = (47, 26, 23)
            self.target_hp_line = self.get_value_line(target_start_pos, 60, self.target_hp_color, target_hp_dark_color)

    def update(self):
        self.update_screen()
        if hasattr(self, 'hp_line'):
            if not hasattr(self, 'hp_color'):
                rgb_screen = self.screen.convert('RGB')
                self.hp_color = rgb_screen.getpixel((self.hp_line[0], self.hp_line[1]))
            self.hp = self.get_percent_value(self.hp_line, self.hp_color)
        if hasattr(self, 'mp_line'):
            if not hasattr(self, 'mp_color'):
                rgb_screen = self.screen.convert('RGB')
                self.mp_color = rgb_screen.getpixel((self.mp_line[0], self.mp_line[1]))
            self.mp = self.get_percent_value(self.mp_line, self.mp_color)
        if hasattr(self, 'target_hp_line'):
            if not hasattr(self, 'target_hp_color'):
                rgb_screen = self.screen.convert('RGB')
                self.target_hp_color = rgb_screen.getpixel((self.target_hp_line[0], self.target_hp_line[1]))
            self.target_hp = self.get_percent_value(self.target_hp_line, self.target_hp_color)

    def get_percent_value(self, line, color):
        left = line[0]
        top = line[1]
        width = line[2] - left
        current_right = left
        rgb_screen = self.screen.convert('RGB')
        if color_equal(rgb_screen.getpixel((left, top)), color):
            color = rgb_screen.getpixel((left, top))
            i = counter = 0
            while True:
                pixel = rgb_screen.getpixel((left + i, top))
                if color_equal(pixel, color):
                    current_right = left + i
                    counter = 0
                else:
                    counter += 1
                if counter > 20 or left + i == line[2]:
                    break
                i += 1
            return int((current_right - left) / width * 100)
        else:
            return 0

    def get_value_line(self, start_pos, max_height, color, dark_color):
        top = start_pos[1]
        rgb_screen = self.screen.convert('RGB')
        pixel = rgb_screen.getpixel(start_pos)
        start_pos = list(start_pos)

        while not color_equal(pixel, color) and not color_equal(pixel, dark_color):
            start_pos[1] += 1
            pixel = rgb_screen.getpixel((start_pos[0], start_pos[1]))
            if start_pos[1] > top+max_height:
                start_pos = [start_pos[0]+1, top]
        i = 1
        top = start_pos[1]
        left = right = start_pos[0]
        counter = 0
        while True:
            pixel = rgb_screen.getpixel((start_pos[0] - i, start_pos[1]))
            if color_equal(pixel, color) or color_equal(pixel, dark_color):
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
            if color_equal(pixel, color) or color_equal(pixel, dark_color):
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