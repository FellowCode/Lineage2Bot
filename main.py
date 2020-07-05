from ctypes import windll
import os

from functions import get_screen, get_windows_hwnd
from l2bot import MainLineageWindow, ValuesMonitor, LineageWindow

import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

import time

user32 = windll.user32
user32.SetProcessDPIAware()

# WINDOW_NAME = 'Lineage II'
WINDOW_NAME = 'luki1'


class L2BotApp:
    cycle_update = False

    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.show_main_window()

    def show_main_window(self):
        self.frame.title = 'Bot'
        self.master.geometry('200x340+2200+600')
        self.master.resizable(False, False)

        window_name_btn = Button(self.frame, text='Подключить окна', height=1)
        window_name_btn.place(relx=0.05, y=10, relwidth=0.9)
        window_name_btn.bind('<ButtonRelease-1>', lambda event: self.setup_l2_window())

        auto_calibration_btn = Button(self.frame, text='Настройки окон', height=1)
        auto_calibration_btn.place(relx=0.05, y=55, relwidth=0.9)
        auto_calibration_btn.bind('<ButtonRelease-1>', lambda event: self.window_setup_l2_supports())

        auto_calibration_btn = Button(self.frame, text='Автокалибровка', height=1)
        auto_calibration_btn.place(relx=0.05, y=85, relwidth=0.9)
        auto_calibration_btn.bind('<ButtonRelease-1>', lambda event: self.calibration_window_init('auto'))

        set_hp_button = Button(self.frame, text='Указать ХП', height=1)
        set_hp_button.place(relx=0.05, y=115, relwidth=0.9)
        set_hp_button.bind('<ButtonRelease-1>', lambda event: self.calibration_window_init('manual_hp'))

        set_mp_button = Button(self.frame, text='Указать МП', height=1)
        set_mp_button.place(relx=0.05, y=145, relwidth=0.9)
        set_mp_button.bind('<ButtonRelease-1>', lambda event: self.calibration_window_init('manual_mp'))

        set_target_hp_button = Button(self.frame, text='Указать ХП цели', height=1)
        set_target_hp_button.place(relx=0.05, y=175, relwidth=0.9)
        set_target_hp_button.bind('<ButtonRelease-1>', lambda event: self.calibration_window_init('manual_target_hp'))

        screen_btn = Button(self.frame, text='Сделать скриншот', height=1)
        screen_btn.place(relx=0.05, y=205, relwidth=0.9)
        screen_btn.bind('<ButtonRelease-1>', lambda ev: self.l2_window.save_screen())

        self.updater_button = Button(self.frame, text='Включить', height=1)
        self.updater_button.place(relx=0.05, y=235, relwidth=0.9)
        self.updater_button.bind('<ButtonRelease-1>', self.change_cycle_update)

        self.hp_label = Label(text='HP: None')
        self.hp_label.place(relx=0.05, y=270, relwidth=0.9)

        self.mp_label = Label(text='MP: None')
        self.mp_label.place(relx=0.05, y=290, relwidth=0.9)

        self.target_hp_label = Label(text='T_HP: None')
        self.target_hp_label.place(relx=0.05, y=310, relwidth=0.9)

        self.frame.place(x=0, y=0, relwidth=1, relheight=1)

    def change_cycle_update(self, event):
        self.cycle_update = not self.cycle_update
        if self.cycle_update:
            self.updater_button['text'] = 'Выключить'
            self.monitor = ValuesMonitor(self)
            self.monitor.start()
        else:
            self.monitor.stop()
            self.updater_button['text'] = 'Включить'
            self.hp_label['text'] = 'HP: None'
            self.mp_label['text'] = 'MP: None'
            self.target_hp_label['text'] = 'T_HP: None'

    def update_values(self):
        if self.cycle_update:
            self.hp_label['text'] = 'HP: %d' % self.l2_window.hp
            self.mp_label['text'] = 'MP: %d' % self.l2_window.mp
            self.target_hp_label['text'] = 'T_HP: %d' % self.l2_window.target_hp
            self.master.after(500, self.update_values)

    def calibration_window_init(self, method):
        self.calibration_window = Toplevel(self.master)
        self.app = CalibrationWindow(self, method)

    def setup_l2_window(self):
        self.l2_window = MainLineageWindow(get_windows_hwnd('aaa')[0])

    def window_setup_l2_supports(self):
        self.supports_window = Toplevel(self.master)
        self.app = SupportsSetupWindow(self)


class SupportsSetupWindow:
    def __init__(self, main_window):
        self.root = main_window
        self.master = main_window.supports_window
        self.master.geometry('600x340+2200+600')
        self.master.resizable(False, False)

        self.window_bind = WindowBind()

        self.ui_init()

    def ui_init(self):
        tab_parent = ttk.Notebook(self.master)

        tab_names = [StringVar()]*9

        for i in range(9):
            tab = ttk.Frame(tab_parent)

            tab_parent.add(tab, text=f'Окно {i + 1}')
            frame = ttk.Frame(tab)
            ttk.Label(frame, text='Название окна').pack(side=LEFT)
            ttk.Entry(frame, textvariable=tab_names[i]).pack(side=LEFT)
            ttk.Button(frame, text='Добавить триггер', command=lambda: self.add_trigger(i)).pack(side=LEFT)
            frame.pack(side=LEFT)

        tab_parent.pack(expand=1, fill='both')

        btn_frame = ttk.Frame(self.master)
        btn_frame.pack(side=BOTTOM)

    def add_trigger(self, i):
        self.trigger_window = Toplevel(self.master)
        self.app = TriggerWindow(self, i)



class TriggerWindow:
    def __init__(self, root, index):
        self.root = root
        self.index = index
        self.master = root.trigger_window
        self.master.geometry('280x150')
        self.master.resizable(False, False)

        ttk.Label(self.master, text='Выберите триггер').pack()
        self.trigger = StringVar()
        trigger_list = ttk.Combobox(self.master, width=30)
        trigger_list['values'] = ['ХП основы меньше ...%',
                                  'МП основы меньше ...%',
                                  'Баф каждые n с.',
                                  'Нет цели',
                                  'Моб убит']
        trigger_list.pack()

        ttk.Label(self.master, text='Значение если есть').pack()
        self.value = IntVar()
        ttk.Entry(self.master, width=10, textvariable=self.value).pack()
        ttk.Label(self.master, text='Кнопка (F)').pack()
        self.btn = IntVar()
        ttk.Entry(self.master, width=10, textvariable=self.btn).pack()
        ttk.Button(self.master, text='Добавить', command=self.add).pack()

    def add(self):
        self.root.window_bind.values[self.index]['triggers'].append(
            {'trigger': self.trigger.get(), 'value': self.value.get(), 'btn': self.btn.get()})
        self.root.window_bind.save()
        #self.root.master.destroy()
        #self.root.__init__(self.root.root)


class WindowBind:
    def __init__(self):
        self.values = [{'name': '', 'triggers': []}]*9

    def save(self):
        if not os.path.exists('save'):
            os.makedirs('save')
        with open('save/window_bind.txt', 'w') as f:
            print(str(self.values), file=f)

    def load(self):
        if os.path.exists('save/window_bind.txt'):
            with open('save/window_bind.txt', 'r') as f:
                self.values = eval(f.read().strip())


class CalibrationWindow:
    def __init__(self, main_window, method):
        self.master = main_window.calibration_window
        self.frame = tk.Frame(self.master)
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.main_window = main_window
        self.l2_window = main_window.l2_window
        self.l2_window.update_screen()
        self.pos = self.l2_window.pos
        self.size = self.l2_window.size
        self.master.geometry('%dx%d+%d+%d' % (self.size[0], self.size[1], self.pos[0], self.pos[1] - 1))
        self.master.resizable(False, False)
        self.master.overrideredirect(True)
        self.set_background()
        self.method = method

        if method == 'auto':
            self.auto_calibration()
        elif method == 'manual_hp' or method == 'manual_mp' or method == 'manual_target_hp':
            self.draw_line()

    def set_background(self):
        image = ImageTk.PhotoImage(self.l2_window.screen)
        bg_label = tk.Label(self.frame, image=image)
        bg_label.image = image

        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        self.canvas = tk.Canvas(self.frame, width=self.size[0], height=self.size[1])
        self.canvas.create_image(0, 0, image=image, anchor=tk.NW)
        self.canvas.pack()

    def auto_calibration(self):
        def show_end_buttons():
            if hasattr(self, 'btn_ok'):
                self.btn_ok.destroy()
            if hasattr(self, 'btn_repeat'):
                self.btn_repeat.destroy()
            if hasattr(self, 'btn_cancel'):
                self.btn_cancel.destroy()

            def Ok(event):
                self.master.destroy()
                self.main_window.master.focus_force()

            def cancel(event):
                self.l2_window.hp_line = None
                self.l2_window.mp_line = None
                self.l2_window.target_hp_line = None
                self.master.destroy()
                self.main_window.master.focus_force()

            self.btn_ok = Button(self.frame, text='Ok', width=20, height=2)
            self.btn_ok.place(relx=0.5, x=-150, rely=0.5)
            self.btn_ok.bind('<ButtonRelease-1>', Ok)

            self.btn_cancel = Button(self.frame, text='Отмена', width=20, height=2)
            self.btn_cancel.place(relx=0.5, x=2, rely=0.5)
            self.btn_cancel.bind('<ButtonRelease-1>', cancel)

        self.l2_window.calibration()
        self.draw_lines()
        self.master.focus_force()
        show_end_buttons()

    def draw_line(self):
        self.l2_window.update_screen()
        self.set_background()
        line = [0, 0, 0, 0]
        self.motion_bind = None
        self.canvas_line = None
        self.master.focus_force()

        def new_line(event):
            if self.canvas_line:
                self.canvas.delete(self.canvas_line)
            line[0] = line[2] = event.x
            line[1] = line[3] = event.y
            self.motion_bind = self.master.bind('<Motion>', update_line)

        def update_line(event):
            if event.x > line[0]:
                line[2] = event.x
            if self.canvas_line:
                self.canvas.delete(self.canvas_line)
            self.canvas_line = self.canvas.create_line(line, width=2, fill='white')

        def close_line(event):
            update_line(event)
            if self.motion_bind:
                self.master.unbind('<Motion>', self.motion_bind)
            if self.new_line_bind:
                self.master.unbind('<Button-1>', self.new_line_bind)
            if self.close_line_bind:
                self.master.unbind('<ButtonRelease-1>', self.close_line_bind)
            show_end_buttons()

        def show_end_buttons():

            def Ok(event):
                if self.method == 'manual_hp':
                    self.l2_window.hp_line = line
                elif self.method == 'manual_mp':
                    self.l2_window.mp_line = line
                elif self.method == 'manual_target_hp':
                    self.l2_window.target_hp_line = line
                self.master.destroy()
                self.main_window.master.focus_force()

            def cancel(event):
                self.master.destroy()
                self.main_window.master.focus_force()

            def repeat(event):
                if hasattr(self, 'btn_ok'):
                    self.btn_ok.destroy()
                if hasattr(self, 'btn_repeat'):
                    self.btn_repeat.destroy()
                if hasattr(self, 'btn_cancel'):
                    self.btn_cancel.destroy()
                if self.canvas_line:
                    self.canvas.delete(self.canvas_line)
                self.draw_line()

            self.btn_ok = Button(self.frame, text='Ok')
            self.btn_ok.place(x=line[2] - 120, y=line[3] + 10)
            self.btn_ok.bind('<ButtonRelease-1>', Ok)

            self.btn_repeat = Button(self.frame, text='Повторить')
            self.btn_repeat.place(x=line[2] - 92, y=line[3] + 10)
            self.btn_repeat.bind('<ButtonRelease-1>', repeat)

            self.btn_cancel = Button(self.frame, text='Отмена')
            self.btn_cancel.place(x=line[2] - 20, y=line[3] + 10)
            self.btn_cancel.bind('<ButtonRelease-1>', cancel)

        self.new_line_bind = self.master.bind('<Button-1>', new_line)
        self.close_line_bind = self.master.bind('<ButtonRelease-1>', close_line)

    def draw_lines(self):
        self.set_background()
        if self.l2_window.hp_line:
            self.hp_line = self.canvas.create_line(self.l2_window.hp_line, width=2, fill='white')
        if self.l2_window.mp_line:
            self.mp_line = self.canvas.create_line(self.l2_window.mp_line, width=2, fill='white')
        if self.l2_window.target_hp_line:
            self.target_hp_line = self.canvas.create_line(self.l2_window.target_hp_line, width=2, fill='white')
        try:
            self.party_hp_lines = []
            self.party_mp_lines = []
            for i, php_line in enumerate(self.l2_window.party_hp_lines):
                self.party_hp_lines.append(self.canvas.create_line(php_line, width=2, fill='white'))
                self.party_mp_lines.append(
                    self.canvas.create_line(self.l2_window.party_mp_lines, width=2, fill='white'))
        except:
            pass


if __name__ == '__main__':
    root = tk.Tk()
    app = L2BotApp(root)
    root.mainloop()
