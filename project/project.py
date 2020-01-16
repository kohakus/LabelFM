import os
import imgui

from .utils import get_idclr
from .utils import help_marker
from .utils import time_delay_ms
from .utils import get_plane_route
from .utils import get_closest_ptidx
from .utils import check_plane_valid

from .data import save_label
from .data import textureDeleter
from .data import clear_curr_data
from .data import clear_curr_texture
from .data import get_data_from_path
from .data import load_texture_from_file


def show_labelFM_window(labelfm_flags, labelfm_env_flags, labelfm_anno_params):
    window_flags = 0
    if labelfm_flags["NO_COLLAPSE"]: window_flags |= imgui.WINDOW_NO_COLLAPSE
    if labelfm_flags["NO_RESIZE"]: window_flags |= imgui.WINDOW_NO_RESIZE

    imgui.set_next_window_size(labelfm_flags["WINDOW_WIDTH"],
                               labelfm_flags["WINDOW_HEIGHT"],
                               condition=imgui.ALWAYS)
    labelfm_flags["EXPANDED"], labelfm_flags["OPENED"] = imgui.begin("LabelFM", True, window_flags)

    # reload and reset project window size
    project_window_size = imgui.get_window_size()
    labelfm_flags["WINDOW_WIDTH"] = project_window_size[0]
    labelfm_flags["WINDOW_HEIGHT"] = project_window_size[1]

    # check if the cache should be refreshed
    if labelfm_env_flags["DATA_CLEAR_SIGNAL"]:
        labelfm_env_flags["DATA_CLEAR_SIGNAL"] = False
        clear_curr_texture(labelfm_env_flags)

    # check if the point annotation should be cleared
    if labelfm_anno_params["POINT_CLEAR_SIGNAL"]:
        labelfm_anno_params["POINT_CLEAR_SIGNAL"] = False
        labelfm_anno_params["POINTS"].clear()
        labelfm_env_flags["CANVAS_ENV"]["ADDING_LINE"] = False
        labelfm_env_flags["CANVAS_ENV"]["LINE_CACHE"] = -1
        labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"].clear()
        labelfm_anno_params["LINES"].clear()

    # set image region
    imgui.begin_child("Image Region", labelfm_flags["IMREGION_WIDTH"], labelfm_flags["IMREGION_HEIGHT"], True)
    region_image_content(labelfm_flags, labelfm_env_flags, labelfm_anno_params)
    imgui.end_child()

    imgui.same_line()

    # set canvas region
    imgui.begin_child("Canvas Region", labelfm_flags["IMREGION_WIDTH"], labelfm_flags["IMREGION_HEIGHT"], True)
    region_canvas_content(labelfm_flags, labelfm_env_flags, labelfm_anno_params)
    imgui.end_child()

    imgui.same_line()

    # set file region
    imgui.begin_child("File Region", 0, labelfm_flags["IMREGION_HEIGHT"], True)
    region_file_content(labelfm_flags, labelfm_env_flags)
    imgui.end_child()

    # set label region
    imgui.begin_child("Label Region", 0, 0, False)
    region_label_content(labelfm_flags, labelfm_env_flags, labelfm_anno_params)
    imgui.end_child()

    imgui.end()


def region_image_content(labelfm_flags, labelfm_env_flags, labelfm_anno_params):
    # read an image if the selection changed
    if labelfm_env_flags["SELECTION_CHANGED"]:
        img_selected_idx = labelfm_env_flags["IMG_SELECTED"]

        # the first time to select an item, generate a new texture id
        if labelfm_env_flags["DATA_LIST"][img_selected_idx][1] == -1:
            image_path = os.path.join(labelfm_env_flags["FILE_PATH"][0],
                                      labelfm_env_flags["DATA_LIST"][img_selected_idx][0])
            imagetxtid, image_w, image_h = load_texture_from_file(image_path)
            labelfm_env_flags["DATA_LIST"][img_selected_idx][1] = imagetxtid
            labelfm_env_flags["DATA_LIST"][img_selected_idx][2] = image_w
            labelfm_env_flags["DATA_LIST"][img_selected_idx][3] = image_h
            labelfm_env_flags["TEXTID_CLEAR_BUFFER"].append(textureDeleter(imagetxtid))

        labelfm_env_flags["CURR_IMAGE_TID"] = labelfm_env_flags["DATA_LIST"][img_selected_idx][1]
        labelfm_env_flags["CURR_IMAGE_WIDTH"] = labelfm_env_flags["DATA_LIST"][img_selected_idx][2]
        labelfm_env_flags["CURR_IMAGE_HEIGHT"] = labelfm_env_flags["DATA_LIST"][img_selected_idx][3]

    # show current image info.
    imgui.text("TextureId: {}".format(labelfm_env_flags["CURR_IMAGE_TID"]))
    imgui.same_line()
    imgui.text("Width: {}".format(labelfm_env_flags["CURR_IMAGE_WIDTH"]))
    imgui.same_line()
    imgui.text("Height: {}".format(labelfm_env_flags["CURR_IMAGE_HEIGHT"]))
    imgui.separator()

    # show the selected image, as well as image cursor position
    imgui.begin_child("Image Texture", 0, 0, False)
    mousePosition = imgui.get_mouse_pos()
    cursPosition = imgui.get_cursor_screen_pos()
    if labelfm_env_flags["IMG_SELECTED"] != -1:

        imgui.image(labelfm_env_flags["CURR_IMAGE_TID"],
                    labelfm_env_flags["CURR_IMAGE_WIDTH"],
                    labelfm_env_flags["CURR_IMAGE_HEIGHT"])

        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            x_pos = mousePosition[0] - cursPosition[0]
            y_pos = mousePosition[1] - cursPosition[1]
            imgui.text("cursor.x: {}".format(x_pos))
            imgui.text("cursor.y: {}".format(y_pos))
            imgui.end_tooltip()

            if not labelfm_anno_params["POINT_ANNO_LOCKED"]:
                # deal with junction point annotation
                if imgui.is_mouse_clicked(0):
                    labelfm_anno_params["POINTS"].append((x_pos, y_pos))
                if imgui.is_mouse_clicked(1) and len(labelfm_anno_params["POINTS"]) > 0:
                    labelfm_anno_params["POINTS"].pop()
                    labelfm_env_flags["CANVAS_ENV"]["ADDING_LINE"] = False
                    labelfm_env_flags["CANVAS_ENV"]["LINE_CACHE"] = -1
                    labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"].clear()
                    labelfm_anno_params["LINES"].clear()

    # check if point selection is valid
    if len(labelfm_anno_params["POINTS"]) <= labelfm_anno_params["POINT_SELECTED"]:
        labelfm_anno_params["POINT_SELECTED"] = -1

    imgui.end_child()


def region_file_content(labelfm_flags, labelfm_env_flags):
    # generating data list
    gen_data_clicked = imgui.small_button("Refresh DataList")

    if gen_data_clicked:
        labelfm_env_flags["DATA_CLEAR_SIGNAL"] = True
        clear_curr_data(labelfm_env_flags)
        current_data_path = labelfm_env_flags["FILE_PATH"][0]
        labelfm_env_flags["DATA_REFRESH_STATE"] = get_data_from_path(current_data_path, labelfm_env_flags["DATA_LIST"])
        labelfm_env_flags["DATA_REFRESH_TICK"] = imgui.get_time()

    # show data list refresh state, 1.5 seconds
    if labelfm_env_flags["DATA_REFRESH_TICK"] != 0:
        if imgui.get_time() - labelfm_env_flags["DATA_REFRESH_TICK"] <= 1.5:
            if labelfm_env_flags["DATA_REFRESH_STATE"]:
                imgui.same_line()
                imgui.text_colored("Refresh successfully!", 0.5255, 0.7569, 0.4000)
            else:
                imgui.same_line()
                imgui.text_colored("Unknown data path!!!", 1.0, 0.0, 0.0)
        else:
            labelfm_env_flags["DATA_REFRESH_TICK"] = 0.0
    imgui.separator()

    # show image list, single selection
    imgui.begin_child("Image List", 0, 0, False)
    selection_changed = False
    for idx in range(len(labelfm_env_flags["DATA_LIST"])):
        _, img_select_state = imgui.selectable("{}".format(labelfm_env_flags["DATA_LIST"][idx][0]),
                                               idx == labelfm_env_flags["IMG_SELECTED"])

        if img_select_state:
            if labelfm_env_flags["IMG_SELECTED"] != idx:
                selection_changed = True
            labelfm_env_flags["IMG_SELECTED"] = idx
    imgui.end_child()

    # refresh selection changed flag
    labelfm_env_flags["SELECTION_CHANGED"] = selection_changed


def region_canvas_content(labelfm_flags, labelfm_env_flags, labelfm_anno_params):
    if labelfm_env_flags["ANNO_MODE_CHANGED"]:
        labelfm_env_flags["ANNO_MODE_CHANGED"] = False
        labelfm_env_flags["CANVAS_ENV"]["ADDING_LINE"] = False
        labelfm_env_flags["CANVAS_ENV"]["LINE_CACHE"] = -1
        labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"].clear()
        labelfm_anno_params["LINES"].clear()

    clear_lines_clicked = imgui.small_button("Clear Lines")
    if clear_lines_clicked:
        labelfm_env_flags["CANVAS_ENV"]["ADDING_LINE"] = False
        labelfm_env_flags["CANVAS_ENV"]["LINE_CACHE"] = -1
        labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"].clear()
        labelfm_anno_params["LINES"].clear()

    if labelfm_env_flags["CURR_ANNO_MODE"] == 1:
        imgui.same_line()
        save_plane_clicked = imgui.small_button("Save Plane")

        if save_plane_clicked:
            if check_plane_valid(labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"]):
                labelfm_anno_params["LINES"].append(labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"].copy())
                labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"].clear()

    imgui.separator()

    # Canvas Rendering Begin
    imgui.begin_child("Canvas Rend", 0, 0, False)
    canvas_pos = imgui.get_cursor_screen_pos()
    canvas_size = imgui.Vec2(labelfm_env_flags["CURR_IMAGE_WIDTH"], labelfm_env_flags["CURR_IMAGE_HEIGHT"])
    draw_list = imgui.get_window_draw_list()

    if canvas_size.x != 0 and canvas_size.y != 0:
        # draw canvas BG
        draw_list.add_rect_filled(canvas_pos.x, canvas_pos.y,
                                  canvas_pos.x + canvas_size.x,
                                  canvas_pos.y + canvas_size.y,
                                  imgui.get_color_u32_rgba(0.196, 0.196, 0.196, 1.0))
        # draw canvas border
        draw_list.add_rect(canvas_pos.x, canvas_pos.y,
                           canvas_pos.x + canvas_size.x,
                           canvas_pos.y + canvas_size.y,
                           imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0),
                           thickness=0.2)

        # using invisible button as a convenience
        imgui.invisible_button("Canvas Mask", canvas_size.x, canvas_size.y)
        mousePosition = imgui.get_mouse_pos()
        labelfm_env_flags["CANVAS_ENV"]["POINT_HOVERED"] = -1
        if imgui.is_item_hovered():
            pos_in_canvas = imgui.Vec2(mousePosition.x-canvas_pos.x, mousePosition.y-canvas_pos.y)
            labelfm_env_flags["CANVAS_ENV"]["POINT_HOVERED"] = get_closest_ptidx(pos_in_canvas,
                                                                                 labelfm_anno_params["POINTS"],
                                                                                 labelfm_env_flags["CANVAS_ENV"]["POINT_RADIUS"])

            # adding-line process
            if imgui.is_mouse_clicked(0):
                if labelfm_env_flags["CANVAS_ENV"]["POINT_HOVERED"] != -1:
                    if labelfm_env_flags["CANVAS_ENV"]["ADDING_LINE"]:
                        if labelfm_env_flags["CANVAS_ENV"]["POINT_HOVERED"] != labelfm_env_flags["CANVAS_ENV"]["LINE_CACHE"]:
                            new_line_anno = ( labelfm_env_flags["CANVAS_ENV"]["LINE_CACHE"],
                                              labelfm_env_flags["CANVAS_ENV"]["POINT_HOVERED"] )

                            if labelfm_env_flags["CURR_ANNO_MODE"] == 0:
                                labelfm_anno_params["LINES"].append(new_line_anno)

                            if labelfm_env_flags["CURR_ANNO_MODE"] == 1:
                                labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"].append(new_line_anno)

                            labelfm_env_flags["CANVAS_ENV"]["LINE_CACHE"] = -1
                            labelfm_env_flags["CANVAS_ENV"]["ADDING_LINE"] = False
                    else:
                        labelfm_env_flags["CANVAS_ENV"]["LINE_CACHE"] = labelfm_env_flags["CANVAS_ENV"]["POINT_HOVERED"]
                        labelfm_env_flags["CANVAS_ENV"]["ADDING_LINE"] = True

            # revoke process
            if imgui.is_mouse_clicked(1):
                if labelfm_env_flags["CANVAS_ENV"]["ADDING_LINE"]:
                    labelfm_env_flags["CANVAS_ENV"]["LINE_CACHE"] = -1
                    labelfm_env_flags["CANVAS_ENV"]["ADDING_LINE"] = False
                else:
                    if labelfm_env_flags["CURR_ANNO_MODE"] == 0:
                        if len(labelfm_anno_params["LINES"]) > 0:
                            labelfm_anno_params["LINES"].pop()
                    if labelfm_env_flags["CURR_ANNO_MODE"] == 1:
                        if len(labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"]) > 0:
                            labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"].pop()
                        else:
                            if len(labelfm_anno_params["LINES"]) > 0:
                                labelfm_anno_params["LINES"].pop()

        # check if item selection is valid before drawing
        if len(labelfm_anno_params["LINES"]) <= labelfm_anno_params["ITEM_SELECTED"]:
            labelfm_anno_params["ITEM_SELECTED"] = -1

        # draw line annotation
        point_radius = labelfm_env_flags["CANVAS_ENV"]["POINT_RADIUS"]
        if labelfm_env_flags["CURR_ANNO_MODE"] == 0:
            line_color = labelfm_env_flags["CANVAS_ENV"]["LINE_RGBA"]
            for idx in range(len(labelfm_anno_params["LINES"])):
                start_id, end_id = labelfm_anno_params["LINES"][idx]
                start_pos_rel = labelfm_anno_params["POINTS"][start_id]
                end_pos_rel = labelfm_anno_params["POINTS"][end_id]

                if idx == labelfm_anno_params["ITEM_SELECTED"]:
                    draw_list.add_line(canvas_pos.x+start_pos_rel[0], canvas_pos.y+start_pos_rel[1],
                                       canvas_pos.x+end_pos_rel[0], canvas_pos.y+end_pos_rel[1],
                                       imgui.get_color_u32_rgba(1.0, 0.0, 0.0, 0.7),
                                       point_radius)
                else:
                    draw_list.add_line(canvas_pos.x+start_pos_rel[0], canvas_pos.y+start_pos_rel[1],
                                       canvas_pos.x+end_pos_rel[0], canvas_pos.y+end_pos_rel[1],
                                       imgui.get_color_u32_rgba(*line_color),
                                       point_radius)

        if labelfm_env_flags["CURR_ANNO_MODE"] == 1:
            # draw plane lines
            plane_line_color = labelfm_env_flags["CANVAS_ENV"]["PLANE_RGBA"]
            for idx in range(len(labelfm_anno_params["LINES"])):
                plane_idx = labelfm_anno_params["LINES"][idx]
                for plane_line in plane_idx:
                    start_id, end_id = plane_line
                    start_pos_rel = labelfm_anno_params["POINTS"][start_id]
                    end_pos_rel = labelfm_anno_params["POINTS"][end_id]
                    draw_list.add_line(canvas_pos.x+start_pos_rel[0], canvas_pos.y+start_pos_rel[1],
                                       canvas_pos.x+end_pos_rel[0], canvas_pos.y+end_pos_rel[1],
                                       imgui.get_color_u32_rgba(*plane_line_color),
                                       point_radius)

            # highlight selected plane
            if labelfm_anno_params["ITEM_SELECTED"] != -1:
                selected_id = labelfm_anno_params["ITEM_SELECTED"]
                highlight_color = get_idclr(selected_id)
                plane_selected = labelfm_anno_params["LINES"][selected_id]
                for plane_line in plane_selected:
                    start_id, end_id = plane_line
                    start_pos_rel = labelfm_anno_params["POINTS"][start_id]
                    end_pos_rel = labelfm_anno_params["POINTS"][end_id]
                    draw_list.add_line(canvas_pos.x+start_pos_rel[0], canvas_pos.y+start_pos_rel[1],
                                       canvas_pos.x+end_pos_rel[0], canvas_pos.y+end_pos_rel[1],
                                       imgui.get_color_u32_rgba(*highlight_color),
                                       point_radius)

            # draw plane cache lines
            cache_line_color = labelfm_env_flags["CANVAS_ENV"]["LINE_RGBA"]
            for plane_line in labelfm_env_flags["CANVAS_ENV"]["PLANE_CACHE"]:
                start_id, end_id = plane_line
                start_pos_rel = labelfm_anno_params["POINTS"][start_id]
                end_pos_rel = labelfm_anno_params["POINTS"][end_id]
                draw_list.add_line(canvas_pos.x+start_pos_rel[0], canvas_pos.y+start_pos_rel[1],
                                   canvas_pos.x+end_pos_rel[0], canvas_pos.y+end_pos_rel[1],
                                   imgui.get_color_u32_rgba(*cache_line_color),
                                   point_radius)

        # draw adding line
        adding_line_color = labelfm_env_flags["CANVAS_ENV"]["LINE_RGBA"]
        if labelfm_env_flags["CANVAS_ENV"]["ADDING_LINE"]:
            start_point_id = labelfm_env_flags["CANVAS_ENV"]["LINE_CACHE"]
            end_point_id = labelfm_env_flags["CANVAS_ENV"]["POINT_HOVERED"]

            if end_point_id != -1:
                end_point_pos_rel = labelfm_anno_params["POINTS"][end_point_id]
                end_point_pos = imgui.Vec2( canvas_pos.x+end_point_pos_rel[0],
                                            canvas_pos.y+end_point_pos_rel[1] )
            else:
                end_x = mousePosition.x
                end_y = mousePosition.y
                # line clipping
                if end_x > canvas_pos.x + canvas_size.x: end_x = canvas_pos.x + canvas_size.x
                if end_y > canvas_pos.y + canvas_size.y: end_y = canvas_pos.y + canvas_size.y
                end_point_pos = imgui.Vec2(end_x, end_y)

            start_point_pos_rel = labelfm_anno_params["POINTS"][start_point_id]
            start_point_pos = imgui.Vec2( canvas_pos.x+start_point_pos_rel[0],
                                          canvas_pos.y+start_point_pos_rel[1] )

            draw_list.add_line(start_point_pos.x, start_point_pos.y,
                               end_point_pos.x, end_point_pos.y,
                               imgui.get_color_u32_rgba(*adding_line_color),
                               point_radius)

        # draw annotated points
        point_color = labelfm_env_flags["CANVAS_ENV"]["POINT_RGBA"]
        for idx in range(len(labelfm_anno_params["POINTS"])):
            point_idx = labelfm_anno_params["POINTS"][idx]

            if idx == labelfm_env_flags["CANVAS_ENV"]["POINT_HOVERED"]:
                draw_list.add_circle_filled(canvas_pos.x+point_idx[0],
                                            canvas_pos.y+point_idx[1],
                                            point_radius,
                                            imgui.get_color_u32_rgba(1.0, 0.0, 0.0, 1.0))
            else:
                draw_list.add_circle_filled(canvas_pos.x+point_idx[0],
                                            canvas_pos.y+point_idx[1],
                                            point_radius,
                                            imgui.get_color_u32_rgba(*point_color))

            if idx == labelfm_anno_params["POINT_SELECTED"]:
                draw_list.add_circle(canvas_pos.x+point_idx[0],
                                     canvas_pos.y+point_idx[1],
                                     point_radius,
                                     imgui.get_color_u32_rgba(1.0, 0.0, 0.0, 0.68))

    imgui.end_child()


def region_label_content(labelfm_flags, labelfm_env_flags, labelfm_anno_params):
    ## show junction points annotation list
    imgui.push_style_var(imgui.STYLE_CHILD_ROUNDING, 5.0)
    imgui.begin_child("Point Annotation List", labelfm_flags["POINTLST_WIDTH"], 0, True)
    imgui.text("Junction Point List")
    imgui.same_line()
    help_marker("Click image to change point annotation.\n(L-Click) add a point\n(R-Click) Revoke")
    imgui.separator()

    # right click to open point-clear-menu
    if imgui.begin_popup_context_window():
        refresh_selection_clicked, _ = imgui.menu_item("Refresh Selection", None, False, True)
        pl_clicked, pl_selected = imgui.menu_item("Points Locked", None, labelfm_anno_params["POINT_ANNO_LOCKED"], True)
        clear_points_clicked, _ = imgui.menu_item("Clear Points", None, False, True)
        if clear_points_clicked: labelfm_anno_params["POINT_CLEAR_SIGNAL"] = True
        if pl_clicked: labelfm_anno_params["POINT_ANNO_LOCKED"] = pl_selected
        if refresh_selection_clicked: labelfm_anno_params["POINT_SELECTED"] = -1
        imgui.end_popup()

    # draw point list
    for idx in range(len(labelfm_anno_params["POINTS"])):
        point_idx = labelfm_anno_params["POINTS"][idx]
        _, point_select_state = imgui.selectable("{:0>2d}: ({}, {})".format(idx, point_idx[0], point_idx[1]),
                                                 idx == labelfm_anno_params["POINT_SELECTED"])
        if point_select_state:
            labelfm_anno_params["POINT_SELECTED"] = idx

    imgui.end_child()
    imgui.pop_style_var(1)

    imgui.same_line()

    ## show the last big block
    imgui.push_style_var(imgui.STYLE_CHILD_ROUNDING, 5.0)
    imgui.begin_child("The Last Block", 0, 0, True)

    # set wireframe-lines annotation list
    imgui.begin_child("Wireframe Annotation List", -labelfm_flags["DECISION_WIDTH"], 0, False)
    imgui.text("Wireframe/Line List")
    imgui.same_line()
    help_marker("Select a pair of points and generate a line segment.")
    imgui.separator()

    if imgui.begin_popup_context_window():
        refresh_selection_clicked, _ = imgui.menu_item("Refresh Selection", None, False, True)
        if refresh_selection_clicked: labelfm_anno_params["ITEM_SELECTED"] = -1
        imgui.end_popup()

    if labelfm_env_flags["CURR_ANNO_MODE"] == 0:
        imgui.columns(3, "LineSeg List", True)
        for idx in range(len(labelfm_anno_params["LINES"])):
            start_id, end_id = labelfm_anno_params["LINES"][idx]
            start_pos = labelfm_anno_params["POINTS"][start_id]
            end_pos = labelfm_anno_params["POINTS"][end_id]
            _, line_select_state = imgui.selectable("{:0>2d}: {} <-> {}, ({}, {}) <-> ({}, {})"\
                                              .format(idx, start_id, end_id,\
                                                      start_pos[0], start_pos[1],\
                                                      end_pos[0], end_pos[1]),
                                                    idx == labelfm_anno_params["ITEM_SELECTED"])
            if line_select_state:
                labelfm_anno_params["ITEM_SELECTED"] = idx
            imgui.next_column()
        imgui.columns(1)

    if labelfm_env_flags["CURR_ANNO_MODE"] == 1:
        imgui.columns(4, "Plane List", True)
        imgui.text("ID")
        imgui.next_column()
        imgui.text("Line Num")
        imgui.next_column()
        imgui.text("Route")
        imgui.next_column()
        imgui.text("Color")
        imgui.next_column()
        imgui.separator()

        for idx in range(len(labelfm_anno_params["LINES"])):
            plane_idx = labelfm_anno_params["LINES"][idx]
            plane_color = get_idclr(idx)
            _, plane_select_state = imgui.selectable("{:0>2d}".format(idx),
                                                     idx == labelfm_anno_params["ITEM_SELECTED"],
                                                     imgui.SELECTABLE_SPAN_ALL_COLUMNS)
            if plane_select_state:
                labelfm_anno_params["ITEM_SELECTED"] = idx
            imgui.next_column()
            imgui.text("{}".format(len(plane_idx)))
            imgui.next_column()
            imgui.text(get_plane_route(plane_idx))
            imgui.next_column()
            imgui.color_button("Plane {} colorbar".format(idx),
                               plane_color[0], plane_color[1],
                               plane_color[2], plane_color[3], 0,
                               imgui.get_text_line_height(),
                               imgui.get_text_line_height())
            imgui.next_column()
        imgui.columns(1)
    imgui.end_child()

    imgui.same_line()

    # set decision sub-block
    imgui.begin_child("Decision Sub-block", 0, 0, True)

    # annotation mode selection
    if imgui.radio_button("LineSeg", 0 == labelfm_env_flags["CURR_ANNO_MODE"]):
        if labelfm_env_flags["CURR_ANNO_MODE"] == 1: labelfm_env_flags["ANNO_MODE_CHANGED"] = True
        labelfm_env_flags["CURR_ANNO_MODE"] = 0
    if imgui.radio_button("Plane", 1 == labelfm_env_flags["CURR_ANNO_MODE"]):
        if labelfm_env_flags["CURR_ANNO_MODE"] == 0: labelfm_env_flags["ANNO_MODE_CHANGED"] = True
        labelfm_env_flags["CURR_ANNO_MODE"] = 1
    imgui.spacing()
    imgui.separator()
    imgui.spacing()

    # decision buttons
    imgui.push_style_color(imgui.COLOR_BUTTON, 0.2392, 0.6, 0.4431, 1.0)
    imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, 0.2078,  0.6980, 0.4863, 1.0)
    imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.1569, 0.8, 0.52156, 1.0)
    annotation_save_clicked = imgui.button("Save Label",
                                           labelfm_flags["DECISION_WIDTH"] * 0.8,
                                           labelfm_flags["DECISION_WIDTH"] * 0.8)
    imgui.pop_style_color(3)

    imgui.spacing()

    imgui.push_style_color(imgui.COLOR_BUTTON, 0.3412, 0.6, 0.2392, 1.0)
    imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED,  0.3490, 0.6980, 0.20784, 1.0)
    imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, 0.3412, 0.8, 0.1569, 1.0)
    annotation_reset_clicked = imgui.button("Reset Label",
                                            labelfm_flags["DECISION_WIDTH"] * 0.8,
                                            labelfm_flags["DECISION_WIDTH"] * 0.8)
    imgui.pop_style_color(3)

    if annotation_save_clicked:
        save_label_state = save_label(labelfm_env_flags, labelfm_anno_params)
        if save_label_state:
            imgui.open_popup("Saved Successfully!")
        else:
            imgui.open_popup("Save Failed!")

    if imgui.begin_popup_modal( "Save Failed!",
                                flags=imgui.WINDOW_NO_RESIZE |\
                                      imgui.WINDOW_ALWAYS_AUTO_RESIZE )[0]:
        imgui.text("Save Failed! Please select an image and do labeling.")
        imgui.same_line()
        if imgui.small_button("Ok, I will Check Again"):
            imgui.close_current_popup()
        imgui.end_popup()

    if imgui.begin_popup_modal( "Saved Successfully!",
                                flags=imgui.WINDOW_NO_RESIZE |\
                                      imgui.WINDOW_ALWAYS_AUTO_RESIZE )[0]:
        imgui.text("Current Label has been saved successfully!")
        imgui.same_line()
        if imgui.small_button("Ok, close this popup."):
            imgui.close_current_popup()
        imgui.end_popup()

    if annotation_reset_clicked:
        labelfm_anno_params["POINT_CLEAR_SIGNAL"] = True
    imgui.end_child()

    imgui.end_child()
    imgui.pop_style_var(1)
