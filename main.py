from ctypes import windll
import os

from functions import get_screen, get_windows_hwnd
from l2bot import LineageWindow, ValuesMonitor, SupportWindow

import tkinter as tk
from tkinter import *
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
        key_bind = KeyBind()
        if len(key_bind.se_name.get()) > 0:
            self.se_window = SupportWindow(get_windows_hwnd(key_bind.se_name.get())[0],
                                           recharge=key_bind.se_recharge.get(), heal=key_bind.se_heal.get(),
                                           buff=key_bind.se_buff.get())
        else:
            self.se_window = None
        if len(key_bind.pp_name.get()) > 0:
            self.pp_window = SupportWindow(get_windows_hwnd(key_bind.pp_name.get())[0], buff=key_bind.pp_buff.get())
        else:
            self.pp_window = None
        if len(key_bind.bd_name.get()) > 0:
            self.bd_window = SupportWindow(get_windows_hwnd(key_bind.bd_name.get())[0], attack=key_bind.bd_attack.get(),
                                           buff=key_bind.bd_buff.get(), buff_time=120)
        else:
            self.bd_window = None

        self.l2_window = LineageWindow(get_windows_hwnd(key_bind.main_name.get())[0], attack=key_bind.main_attack.get(),
                                       target_bliz=key_bind.main_target.get(),
                                       target_dal=key_bind.main_target_daln.get(),
                                       hp_potion=key_bind.main_hp_potion.get(), mob_dead=key_bind.main_mob_dead.get(),
                                       se_window=self.se_window, pp_window=self.pp_window, bd_window=self.bd_window)

    def window_setup_l2_supports(self):
        self.supports_window = Toplevel(self.master)
        self.app = SupportsSetupWindow(self)


class SupportsSetupWindow:
    def __init__(self, main_window):
        self.master = main_window.supports_window
        self.master.geometry('400x340+2200+600')
        self.master.resizable(False, False)

        self.key_bind = KeyBind()

        self.ui_init()

    def ui_init(self):
        # Основа
        title = Label(self.master, text='Основа')
        title.place(x=10, y=5)
        main_name_entry = Entry(self.master, textvariable=self.key_bind.main_name)
        main_name_entry.place(x=10, y=25, width=120)
        Label(self.master, text='Цель близ.').place(x=160, y=25)
        Entry(self.master, textvariable=self.key_bind.main_target).place(x=230, y=25, width=30)
        Label(self.master, text='Цель даль.').place(x=270, y=25)
        Entry(self.master, textvariable=self.key_bind.main_target_daln).place(x=340, y=25, width=30)
        Label(self.master, text='Атака').place(x=10, y=55)
        Entry(self.master, textvariable=self.key_bind.main_attack).place(x=50, y=55, width=30)
        Label(self.master, text='Смерть моба').place(x=100, y=55)
        Entry(self.master, textvariable=self.key_bind.main_mob_dead).place(x=180, y=55, width=30)
        Label(self.master, text='HP банка').place(x=220, y=55)
        Entry(self.master, textvariable=self.key_bind.main_hp_potion).place(x=280, y=55, width=30)

        # SE \ EE

        Label(self.master, text='Shilen Elder \ Elven Elder').place(x=10, y=85)
        Label(self.master, text='Место в пати').place(x=170, y=85)
        Entry(self.master, textvariable=self.key_bind.se_name).place(x=10, y=105, width=120)
        Entry(self.master, textvariable=self.key_bind.se_pos).place(x=170, y=105, width=40)
        Label(self.master, text='Heal').place(x=10, y=130)
        Entry(self.master, textvariable=self.key_bind.se_heal).place(x=50, y=130, width=30)
        Label(self.master, text='Recharge').place(x=90, y=130)
        Entry(self.master, textvariable=self.key_bind.se_recharge).place(x=150, y=130, width=30)
        Label(self.master, text='Buff').place(x=190, y=130)
        Entry(self.master, textvariable=self.key_bind.se_buff).place(x=230, y=130, width=30)

        # Prophet

        Label(self.master, text='Prophet').place(x=10, y=160)
        Entry(self.master, textvariable=self.key_bind.pp_name).place(x=10, y=180, width=120)
        Entry(self.master, textvariable=self.key_bind.pp_pos).place(x=170, y=180, width=40)
        Label(self.master, text='Buff').place(x=10, y=205)
        Entry(self.master, textvariable=self.key_bind.pp_buff).place(x=50, y=205, width=30)

        # Bladedancer

        Label(self.master, text='Bladedancer').place(x=10, y=235)
        Entry(self.master, textvariable=self.key_bind.bd_name).place(x=10, y=255, width=120)
        Entry(self.master, textvariable=self.key_bind.bd_pos).place(x=170, y=255, width=40)
        Label(self.master, text='Buff').place(x=10, y=280)
        Entry(self.master, textvariable=self.key_bind.bd_buff).place(x=50, y=280, width=30)
        Label(self.master, text='Атака').place(x=90, y=280)
        Entry(self.master, textvariable=self.key_bind.bd_attack).place(x=130, y=280, width=30)

        btn = Button(self.master, text='Сохранить', height=1)
        btn.place(x=10, y=310)
        btn.bind('<ButtonRelease-1>', lambda ev: self.save())

    def save(self):
        self.key_bind.save()
        self.master.destroy()


class KeyBind:
    def __init__(self):
        self.main_name = StringVar()
        self.main_target = StringVar()
        self.main_target_daln = StringVar()
        self.main_attack = StringVar()
        self.main_mob_dead = StringVar()
        self.main_hp_potion = StringVar()

        self.se_name = StringVar()
        self.se_pos = IntVar()
        self.se_heal = StringVar()
        self.se_recharge = StringVar()
        self.se_buff = StringVar()

        self.pp_name = StringVar()
        self.pp_pos = IntVar()
        self.pp_buff = StringVar()

        self.bd_name = StringVar()
        self.bd_pos = IntVar()
        self.bd_buff = StringVar()
        self.bd_attack = StringVar()

        self.load()

    def save(self):
        if not os.path.exists('save'):
            os.makedirs('save')
        with open('save/window_bind.txt', 'w') as f:
            d = {}
            for key, value in self.__dict__.items():
                d[key] = value.get()
            print(d, file=f)

    def load(self):
        if os.path.exists('save/window_bind.txt'):
            with open('save/window_bind.txt', 'r') as f:
                d = eval(f.read().strip())
                for key, value in d.items():
                    self.__dict__[key].set(value)


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
