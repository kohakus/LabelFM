import os
import re
import sys
import math
import time
import imgui


def help_marker(helptext):
    imgui.text_colored("(?)", 0.85490, 0.78823, 0.65098)
    if imgui.is_item_hovered():
        imgui.begin_tooltip()
        imgui.push_text_wrap_pos(imgui.get_font_size() * 35.0)
        imgui.text_unformatted(helptext)
        imgui.pop_text_wrap_pos()
        imgui.end_tooltip()


def check_empty_path(path, expt_text="Empty", expt_rgb=(1.0, 0.0, 0.0)):
    if path == "":
        imgui.text_colored(expt_text, expt_rgb[0], expt_rgb[1], expt_rgb[2])
    else:
        imgui.text("{}".format(path))


def time_delay_ms(ms):
    time.sleep(ms/1000.0)


def check_data_path(path):
    return os.path.isabs(path) and os.path.isdir(path)


def file_path_split(filepath):
    # return a triple (Base Path, File Name, File Extension)
    return re.match("^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))", filepath).groups()


def euclidean_dist2_2d(point1, point2):
    return (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2


def get_closest_ptidx(curspos, points, search_radius=1.0):
    ret_idx = -1
    min_dist = math.inf
    sr_2 = search_radius**2
    for idx, point in enumerate(points):
        atmp_dist = euclidean_dist2_2d(curspos, point)
        if atmp_dist < sr_2 or math.isclose(atmp_dist, sr_2):
            if atmp_dist < min_dist:
                min_dist = atmp_dist
                ret_idx = idx
    return ret_idx


def check_plane_valid(plane):
    line_num = len(plane)
    if line_num < 3:
        return False
    else:
        for idx in range(line_num):
            if plane[idx][0] != plane[idx-1][1]:
                return False
    return True


def get_idclr(idx):
    return [ (255.0/255.0, 186.0/255.0, 132.0/255.0, 1.0),\
             (244.0/255.0, 167.0/255.0, 185.0/255.0, 1.0),\
             (32.0/255.0,  96.0/255.0,  79.0/255.0 , 1.0),\
             (129.0/255.0, 199.0/255.0, 212.0/255.0, 1.0),\
             (11.0/255.0,  52.0/255.0,  110.0/255.0, 1.0),\
             (143.0/255.0, 119.0/255.0, 181.0/255.0, 1.0),\
             (131.0/255.0, 138.0/255.0, 45.0/255.0,  1.0),\
             (148.0/255.0, 122.0/255.0, 109.0/255.0, 1.0),\
             (185.0/255.0, 136.0/255.0, 125.0/255.0, 1.0),\
             (73.0/255.0,  92.0/255.0,  105.0/255.0, 1.0),\
             (99.0/255.0,  187.0/255.0, 208.0/255.0, 1.0),\
             (18.0/255.0,  170.0/255.0, 156.0/255.0, 1.0),\
             (74.0/255.0,  64.0/255.0,  53.0/255.0,  1.0),\
             (238.0/255.0, 247.0/255.0, 242.0/255.0, 1.0),\
             (184.0/255.0, 148.0/255.0, 133.0/255.0, 1.0),\
             (136.0/255.0, 58.0/255.0,  30.0/255.0,  1.0),\
             (244.0/255.0, 199.0/255.0, 186.0/255.0, 1.0),\
             (93.0/255.0,  49.0/255.0,  49.0/255.0,  1.0),\
             (36.0/255.0,  128.0/255.0, 103.0/255.0, 1.0),\
             (19.0/255.0,  24.0/255.0,  36.0/255.0,  1.0),\
             (104.0/255.0, 23.0/255.0,  82.0/255.0,  1.0),\
             (28.0/255.0,  13.0/255.0,  26.0/255.0,  1.0),\
             (236.0/255.0, 45.0/255.0,  122.0/255.0, 1.0),\
             (84.0/255.0,  30.0/255.0,  36.0/255.0,  1.0),\
             (149.0/255.0, 74.0/255.0,  69.0/255.0,  1.0) ][idx]


def get_plane_route(plane):
    route = ""
    for line in plane:
        route = route + "{} -> ".format(line[0])
    route = route + "{}".format(plane[0][0])
    return route
