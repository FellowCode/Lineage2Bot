from desktopmagic.screengrab_win32 import getScreenAsImage
from PIL import ImageGrab, ImageDraw, Image
import cv2
from numpy import *
import win32gui

WINDOW_SUBSTRING = 'Lineage II'

def invert_top_pos(top_pos, height):
    return height-top_pos

def load_img_cv(path, thumbnail=1):
    img = Image.open(path)
    img.thumbnail((img.size[0]//thumbnail, img.size[1]//thumbnail))
    return img_to_cv(img)

def get_screen():
    return getScreenAsImage()

def img_to_cv(img):
    return array(img.getdata(), dtype=uint8).reshape((img.size[1], img.size[0], 3))

screen_main = get_screen()

def get_screen_cv(box=None, thumbnail=1):
    screen = screen_main.copy()
    if box:
        screen.crop(box)
    screen.thumbnail((screen.size[0]//thumbnail, screen.size[1]//thumbnail))
    return img_to_cv(screen)

def find_template(img, template, method_id=0):
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

    res = cv2.matchTemplate(img, template, eval(methods[method_id]))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if eval(methods[method_id]) in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc

    return top_left


def get_window_info():
    # set window info
    windows_info = []
    win32gui.EnumWindows(get_window_coordinates, windows_info)
    return windows_info

# EnumWindows handler
# sets L2 window coordinates
def get_window_coordinates(hwnd, windows_info):
    if win32gui.IsWindowVisible(hwnd):
        if WINDOW_SUBSTRING in win32gui.GetWindowText(hwnd):
            rect = win32gui.GetWindowRect(hwnd)
            window_info = {}
            x = rect[0] + 8
            y = rect[1] + 8
            w = rect[2] - x - 8
            h = rect[3] - y - 8
            window_info['x'] = x
            window_info['y'] = y
            window_info['width'] = w
            window_info['height'] = h
            window_info['name'] = win32gui.GetWindowText(hwnd)
            window_info['hwnd'] = hwnd
            windows_info.append(window_info)
            #win32gui.SetForegroundWindow(hwnd)

def color_equal(pixel, value):
    for i, color in enumerate(pixel):
        if color > value[i] + 7 or color < value[i] - 7:
            return False
    return True