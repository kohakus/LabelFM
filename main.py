# -*- coding: utf-8 -*-
import glfw
import imgui
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer

import flags
from project import show_labelFM_info
from project import show_labelFM_state
from project import show_labelFM_window
from project import show_labelFM_setting_APP


def impl_glfw_init():
    width, height = 1080, 960
    window_name = "LabelFM ImGui/GLFW3 Space"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window


def main():
    # flags references
    LABELFM_WINDOW       = flags.LABELFM_WINDOW
    LABELFM_SETTING_APP  = flags.LABELFM_SETTING_APP
    LABELFM_STATE_WINDOW = flags.LABELFM_STATE_WINDOW
    LABELFM_INFO_WINDOW  = flags.LABELFM_INFO_WINDOW
    LABELFM_ENV          = flags.LABELFM_ENV
    LABELFM_ANNO_PARAMS  = flags.LABELFM_ANNO_PARAMS

    # imgui window initialization
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    # main loop
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        # LabeFM menu bar initialization
        if imgui.begin_main_menu_bar():
            # Project sub-menu
            if imgui.begin_menu("Project", True):
                clicked_show, selected_show = imgui.menu_item("Show Project", None, LABELFM_WINDOW["OPENED"], True)
                clicked_quit, selected_quit = imgui.menu_item("Quit", None, False, True)
                if clicked_quit: exit(1)
                if clicked_show: LABELFM_WINDOW["OPENED"] = selected_show
                imgui.end_menu()

            # Settings sub-menu
            if imgui.begin_menu("Settings", True):
                clicked_show, selected_show = imgui.menu_item("Show Settings", None, LABELFM_SETTING_APP["OPENED"], True)
                if clicked_show: LABELFM_SETTING_APP["OPENED"] = selected_show
                imgui.end_menu()

            # Help sub-menu
            if imgui.begin_menu("Help", True):
                clicked_show, selected_show = imgui.menu_item("Show States", None, LABELFM_STATE_WINDOW["OPENED"], True)
                clicked_info, selected_info = imgui.menu_item("Info", None, LABELFM_INFO_WINDOW["OPENED"], True)
                if clicked_show: LABELFM_STATE_WINDOW["OPENED"] = selected_show
                if clicked_info: LABELFM_INFO_WINDOW["OPENED"] = selected_info
                imgui.end_menu()
            imgui.end_main_menu_bar()

        # show labeFM windows
        if LABELFM_INFO_WINDOW["OPENED"]:  show_labelFM_info(LABELFM_INFO_WINDOW)
        if LABELFM_WINDOW["OPENED"]:       show_labelFM_window(LABELFM_WINDOW, LABELFM_ENV, LABELFM_ANNO_PARAMS)
        if LABELFM_STATE_WINDOW["OPENED"]: show_labelFM_state(LABELFM_WINDOW, LABELFM_STATE_WINDOW, LABELFM_ENV)
        if LABELFM_SETTING_APP["OPENED"]:  show_labelFM_setting_APP(LABELFM_WINDOW, LABELFM_SETTING_APP, LABELFM_ENV)

        # opengl rendering setting
        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    # shutdown
    impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    main()
