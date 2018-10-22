from ctypes import windll

from functions import get_screen
from l2bot import LineageWindow

from kivy.app import App
from kivy.graphics import Rectangle, Line, Color

from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.floatlayout import Layout

Config.read('config.ini')
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'window_state', 'hidden')
Config.write()

Window.fullscreen = False

import time

user32 = windll.user32
user32.SetProcessDPIAware()

class RootWidget(Layout):
    line = [0, 0, 0, 0]
    screen_size = (0, 0)

    def create_screen(self):
        screen = get_screen()
        screen.save('tmp\\screenshot.jpg', 'JPEG', quality=90)
        self.screen_size = screen.size
        Window.size = (1921, screen.size[1])
        Window.left = 0
        Window.top = 0
        self.root_widget.set_background()

    def set_background(self):
        with self.canvas:
            self.bg_rect = Rectangle(source="tmp\\screenshot.jpg", pos=(0, 0), size=self.screen_size)

    def set_line(self, points):
        self.canvas.clear()
        self.set_background()
        with self.canvas:
            Color(0.8, 0.2, 0.2, 1)
            Line(points=points, width=1)

    def on_touch_down(self, touch):
        self.line[0] = int(touch.pos[0])
        self.line[1] = self.line[3] = int(touch.pos[1])

    def on_touch_move(self, touch):
        self.line[2] = int(touch.pos[0])
        self.set_line(self.line)

    def on_touch_up(self, touch):
        self.line[2] = int(touch.pos[0])
        self.set_line(self.line)

class L2Bot(App):

    def init_window(self):
        l2_window = LineageWindow()
        l2_window.save_screen()

    def build(self):
        self.init_window()
        self.root_widget = RootWidget()
        self.root_widget.create_screen()
        return self.root_widget

l2bot_app = L2Bot()

if __name__ == '__main__':
    l2bot_app.run()


# lineage = LineageWindow(get_window_info()[0])
# lineage.calibration()

