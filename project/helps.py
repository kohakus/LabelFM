import imgui
from .utils import check_empty_path


def show_labelFM_state(labelfm_flags, labelfm_state_flags, labelfm_env_flags):
    window_flags = 0
    if labelfm_state_flags["NO_COLLAPSE"]: window_flags |= imgui.WINDOW_NO_COLLAPSE
    labelfm_state_flags["EXPANDED"], labelfm_state_flags["OPENED"] = imgui.begin("State Monitor", True)

    # show mouse state
    imgui.text("[1]")
    imgui.same_line()
    if imgui.tree_node("Mouse States", imgui.TREE_NODE_DEFAULT_OPEN):
        io = imgui.get_io()
        imgui.indent()

        # mouse coordinate
        imgui.bullet_text("MousePos.x: {}".format(io.mouse_pos.x))
        imgui.same_line()
        imgui.text("MousePos.y: {}".format(io.mouse_pos.y))

        # mouse down
        imgui.bullet_text("Mouse Down: ")
        for i in range(len(io.mouse_down)):
            if imgui.is_mouse_down(i):
                imgui.same_line()
                imgui.text("b{}".format(i))

        # mouse clicked
        imgui.bullet_text("Mouse Clicked: ")
        for i in range(len(io.mouse_down)):
            if imgui.is_mouse_clicked(i):
                imgui.same_line()
                imgui.text("b{}".format(i))

        # mouse double clicked
        imgui.bullet_text("Mouse DBL-Clicked: ")
        for i in range(len(io.mouse_down)):
            if imgui.is_mouse_double_clicked(i):
                imgui.same_line()
                imgui.text("b{}".format(i))

        # mouse released
        imgui.bullet_text("Mouse Realeased: ")
        for i in range(len(io.mouse_down)):
            if imgui.is_mouse_released(i):
                imgui.same_line()
                imgui.text("b{}".format(i))

        imgui.unindent()
        imgui.tree_pop()

    # show uptime
    imgui.text("[2] ")
    imgui.same_line()
    imgui.text("Uptime: ")
    imgui.same_line()
    curr_uptime = imgui.get_time()
    imgui.text("{} hr {} min".format(int(curr_uptime/3600), int(curr_uptime/60)))

    # show current data path
    imgui.text("[3] ")
    imgui.same_line()
    imgui.text("Current Data Path: ")
    imgui.same_line()
    check_empty_path(labelfm_env_flags["FILE_PATH"][0], expt_text="Empty Path")

    # show current output path
    imgui.text("[4] ")
    imgui.same_line()
    imgui.text("Current Output Path: ")
    imgui.same_line()
    check_empty_path(labelfm_env_flags["OUT_PATH"][0], expt_text="Empty Path")

    # show the size of project window
    imgui.text("[5] ")
    imgui.same_line()
    imgui.text("Current Project Window Size: ")
    imgui.same_line()
    imgui.text("(Width, Height) = ({}, {})".format(labelfm_flags["WINDOW_WIDTH"], labelfm_flags["WINDOW_HEIGHT"]))

    imgui.end()


def show_labelFM_info(labelfm_helpinfo_flags):
    # info is a kind of overlap window, set its flags
    no_decoration  = imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE |\
                     imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_COLLAPSE
    window_flags = 0
    window_flags |= imgui.WINDOW_ALWAYS_AUTO_RESIZE
    window_flags |= imgui.WINDOW_NO_SAVED_SETTINGS
    window_flags |= imgui.WINDOW_NO_FOCUS_ON_APPEARING
    window_flags |= no_decoration
    if labelfm_helpinfo_flags["NO_MOVE"]:
        window_flags |= imgui.WINDOW_NO_MOVE

    # overlap window
    imgui.set_next_window_bg_alpha(0.35)
    labelfm_helpinfo_flags["EXPANDED"], labelfm_helpinfo_flags["OPENED"] = imgui.begin("Help Info", True, window_flags)

    imgui.push_style_color(imgui.COLOR_TEXT, 0.6706, 0.2314, 0.2275)
    imgui.text("Welcome to LabelFM Annotation Tool!")
    imgui.same_line()
    imgui.text(" ©Kohakus 2020")
    imgui.pop_style_color()

    imgui.text("(Right click to set moveable.)")
    if imgui.begin_popup_context_window():
        clicked_mv, selected_mv = imgui.menu_item("Moveable", None, not labelfm_helpinfo_flags["NO_MOVE"], True)
        clicked_cc, selected_cc = imgui.menu_item("Close", None, not labelfm_helpinfo_flags["OPENED"], True)
        if clicked_mv: labelfm_helpinfo_flags["NO_MOVE"] = not selected_mv
        if clicked_cc: labelfm_helpinfo_flags["OPENED"] = not selected_cc
        imgui.end_popup()
    imgui.separator()
    imgui.spacing()
    imgui.push_style_color(imgui.COLOR_TEXT, 0.1098, 0.1098, 0.1098)
    imgui.text("Github: https://github.com/kohakus")
    imgui.text("Home: http://www.metaphia.moe/")
    imgui.pop_style_color()

    imgui.end()
