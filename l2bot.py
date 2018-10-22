from functions import get_screen, get_window_info

class LineageWindow:
    hp_pos = (0, 0)
    target_pos = (0, 0)
    def __init__(self):
        window_info = get_window_info()[0]
        print(window_info)
        self.pos = (window_info['x'], window_info['y']+24)
        self.size = (window_info['width'], window_info['height']-24)
        self.box = (self.pos[0], self.pos[1], self.pos[0]+self.size[0], self.pos[1]+self.size[1])

    def save_screen(self):
        get_screen().crop(self.box).save('tmp\\l2.jpg', 'JPEG')

    def calibration(self):
        pass

        #screen_cv = get_screen_cv(box)
        #self.hp_pos = find_template(screen_cv, load_img_cv('templates\\hp.jpg'), 1)
        #self.target_pos = find_template(screen_cv, load_img_cv('templates\\target.jpg'), 1)