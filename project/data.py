import os
import sys
import imgui
import OpenGL.GL as gl

import cv2
import pickle
import numpy as np
from PIL import Image

from .utils import get_idclr
from .utils import draw_arrow
from .utils import round_tuple


def get_data_from_path(path, data_stori):
    if not os.path.isdir(path):
        return False

    # get rgb image names
    file_dir_list = os.listdir(path)
    imgs_list = list(filter(lambda name: os.path.splitext(name)[-1] in [".png", ".jpg"], file_dir_list))
    imgs_list.sort()

    for name in imgs_list:
        # data explanation: [ImgName, TextureId, Width, Height]
        data_stori.append([name, -1, 0, 0])

    return True


def load_texture_from_file(filepath):
    im = Image.open(filepath).convert("RGB")
    w, h = im.size
    imdata = np.frombuffer(im.tobytes(), np.uint8)
    texname = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texname)

    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT,1)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, w, h, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, imdata)

    return texname, w, h


def textureDeleter(textureID):
    def cleanup():
        if gl.glDeleteTextures:
            gl.glDeleteTextures([textureID])
    return cleanup


def clear_curr_data(labelfm_env_flags):
    # clear data list
    labelfm_env_flags["DATA_LIST"].clear()


def clear_curr_cache(labelfm_env_flags):
    labelfm_env_flags["IMG_SELECTED"] = -1
    labelfm_env_flags["CURR_IMAGE_TID"] = -1
    labelfm_env_flags["CURR_IMAGE_WIDTH"] = 0
    labelfm_env_flags["CURR_IMAGE_HEIGHT"] = 0


def clear_curr_texture(labelfm_env_flags):
    # clear current flag cache
    clear_curr_cache(labelfm_env_flags)

    # clear texture id buffer
    for textid_cleaner in labelfm_env_flags["TEXTID_CLEAR_BUFFER"]:
        textid_cleaner()

    # clear texture clear buffer
    labelfm_env_flags["TEXTID_CLEAR_BUFFER"].clear()


def save_label(labelfm_env_flags, labelfm_anno_params):
    curr_anno_mode = labelfm_env_flags["CURR_ANNO_MODE"]
    curr_anno_id = labelfm_env_flags["IMG_SELECTED"]
    image_dir = labelfm_env_flags["FILE_PATH"][0]
    out_dir = labelfm_env_flags["OUT_PATH"][0]
    curr_image_name = None

    if curr_anno_id == -1:
        return False

    curr_image_name = labelfm_env_flags["DATA_LIST"][curr_anno_id][0]
    curr_image_pext = os.path.splitext(curr_image_name)[0]
    curr_image_path = os.path.join(image_dir, curr_image_name)
    curr_anno_image = cv2.imread(curr_image_path)
    labeled_image = curr_anno_image.copy()

    # change the type of images
    curr_anno_image = cv2.cvtColor(curr_anno_image, cv2.COLOR_BGR2RGB)
    labeled_image = cv2.cvtColor(labeled_image, cv2.COLOR_BGR2RGBA)

    # pickle data to be saved
    pkl_data = {}
    pkl_data["name"]   = curr_image_pext
    pkl_data["image"]  = curr_anno_image
    pkl_data["points"] = labelfm_anno_params["POINTS"].copy()
    if curr_anno_mode == 0:
        pkl_data["linesegs"] = labelfm_anno_params["LINES"].copy()
    if curr_anno_mode == 1:
        pkl_data["planes"] = labelfm_anno_params["LINES"].copy()

    out_itemdir = os.path.join(out_dir, curr_image_pext)
    if not os.path.isdir(out_itemdir):
        os.makedirs(out_itemdir)

    # save data
    with open(os.path.join(out_itemdir, curr_image_pext+".pkl"), 'wb') as f:
        pickle.dump(pkl_data, f)

    # save annotation visualization
    cv2_font = cv2.FONT_HERSHEY_SIMPLEX
    if curr_anno_mode == 0:
        for idx in range(len(labelfm_anno_params["LINES"])):
            start_id, end_id = labelfm_anno_params["LINES"][idx]
            start_pos = round_tuple(labelfm_anno_params["POINTS"][start_id])
            end_pos = round_tuple(labelfm_anno_params["POINTS"][end_id])
            cv2.line(labeled_image, start_pos, end_pos, (0, 204, 77, 150), 1, cv2.LINE_AA)
        cv2.putText(labeled_image, "LineSeg Mode", (10, 250), cv2_font, 0.35, (255, 255, 255, 120), 1, cv2.LINE_AA)

    if curr_anno_mode == 1:
        for idx in range(len(labelfm_anno_params["LINES"])):
            plane_idx = labelfm_anno_params["LINES"][idx]
            plane_color = get_idclr(idx)
            label_color = (round(plane_color[0]*255), round(plane_color[1]*255), round(plane_color[2]*255), 200)
            for plane_line in plane_idx:
                start_id, end_id = plane_line
                start_pos = round_tuple(labelfm_anno_params["POINTS"][start_id])
                end_pos = round_tuple(labelfm_anno_params["POINTS"][end_id])
                draw_arrow(labeled_image, start_pos, end_pos, label_color, 12)
            cv2.putText(labeled_image, "Plane Mode", (10, 250), cv2_font, 0.35, (255, 255, 255, 120), 1, cv2.LINE_AA)

    for idx in range(len(labelfm_anno_params["POINTS"])):
        point_pos = round_tuple(labelfm_anno_params["POINTS"][idx])
        cv2.circle(labeled_image, point_pos, 2, (255, 0, 0, 150), -1, cv2.LINE_AA)

    labeled_image = cv2.cvtColor(labeled_image, cv2.COLOR_RGBA2BGRA)
    cv2.imwrite(os.path.join(out_itemdir, curr_image_pext+"_viz.png"), labeled_image)
    return True
