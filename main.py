from PIL import ImageGrab
from ctypes import windll

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout

user32 = windll.user32
user32.SetProcessDPIAware()

Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'borderless', 1)
Config.write()

img = ImageGrab.grab()
#Window.borderless = True
Window.size = (1920, 1080)
Window.clearcolor = (0, 0, 0, 0)

import win32gui
import win32con
import win32api



class RootWidget(FloatLayout):
    pass

class BotApp(App):
    def build(self):
        return RootWidget()

if __name__ == '__main__':
    BotApp().run()
    # Get the window
    handle = win32gui.FindWindow(None, "Bot")

    # Make it a layered window
    win32gui.SetWindowLong(handle, win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(handle, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)

    # make it transparent (alpha between 0 and 255)
    alpha = 255
    win32gui.SetLayeredWindowAttributes(handle, win32api.RGB(0, 0, 0), alpha, win32con.LWA_ALPHA)