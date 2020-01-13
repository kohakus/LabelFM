import os
import sys
import imgui
import OpenGL.GL as gl

import numpy as np
from PIL import Image


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
    pass
