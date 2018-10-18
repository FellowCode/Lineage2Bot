from PIL import ImageGrab, ImageDraw, Image
from ctypes import windll
import cv2
from numpy import *
import numpy as np
from desktopmagic.screengrab_win32 import getScreenAsImage

user32 = windll.user32
user32.SetProcessDPIAware()

def load_img_cv(path):
    return cv2.imread(path, 0)

def get_screen():
    return getScreenAsImage()

screen = get_screen()

def get_screen_cv():
    return array(screen.getdata(), dtype=uint8).reshape((screen.size[1], screen.size[0], 3))

def find_template(img, template, method=0):
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']



    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(img, template, eval(methods[method]))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if eval(methods[method]) in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc

    tp = Image.open('Screenshot_1.jpg')
    draw = ImageDraw.Draw(screen)
    draw.rectangle([top_left, (top_left[0]+tp.size[0], top_left[1]+tp.size[1])])
    del draw
    screen.save('screen.jpg', 'JPEG')
    return max_val, top_left

print(find_template(get_screen_cv(), load_img_cv('Screenshot_1.jpg'), 3))