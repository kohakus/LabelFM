import imgui
from .utils import help_marker
from .utils import check_data_path


def show_labelFM_setting_APP(labelfm_flags, labelfm_setting_flags, labelfm_env_flags):
    window_flags = 0
    if labelfm_setting_flags["NO_COLLAPSE"]: window_flags |= imgui.WINDOW_NO_COLLAPSE

    labelfm_setting_flags["EXPANDED"], labelfm_setting_flags["OPENED"] = imgui.begin("Settings", True, window_flags)

    # collapsing header -- Data Source Info
    collapse_data_src_info(labelfm_flags, labelfm_setting_flags, labelfm_env_flags)
    imgui.spacing()

    # collapsing header -- Project Layout Info
    collapse_proj_layout_info(labelfm_flags, labelfm_setting_flags, labelfm_env_flags)
    imgui.spacing()

    # collapsing header -- Annotation Info
    collapse_anno_info(labelfm_flags, labelfm_setting_flags, labelfm_env_flags)

    imgui.end()


def collapse_data_src_info(labelfm_flags, labelfm_setting_flags, labelfm_env_flags):
    datainfo_expanded, datainfo_visible = imgui.collapsing_header("Data Source Info")
    if datainfo_expanded:
        imgui.spacing()
        imgui.separator()
        # automatic data path checking
        _, labelfm_setting_flags["AUTO_PATH_CHECK"] = imgui.checkbox("[Auto Path Checking]", labelfm_setting_flags["AUTO_PATH_CHECK"])
        imgui.same_line()
        help_marker("Check if the input path is valid.")
        imgui.separator()

        # Data Path Setting
        imgui.spacing()
        path_save_clicked = imgui.button("Apply(D)")
        imgui.same_line()
        path_revt_clicked = imgui.button("Reset(D)")
        imgui.same_line()
        imgui.push_item_width(imgui.get_window_width() * 0.45)
        path_changed, labelfm_env_flags["FILE_PATH"][1] = \
            imgui.input_text("[Data Path]", labelfm_env_flags["FILE_PATH"][1], 256, imgui.INPUT_TEXT_AUTO_SELECT_ALL)
        imgui.pop_item_width()
        imgui.same_line()
        help_marker("Please set the image path before labeling.")

        if path_revt_clicked:
            labelfm_env_flags["FILE_PATH"][0] = ""
            labelfm_env_flags["FILE_PATH"][1] = ""
        if path_save_clicked:
            if labelfm_setting_flags["AUTO_PATH_CHECK"]:
                if check_data_path(labelfm_env_flags["FILE_PATH"][1]):
                    labelfm_env_flags["FILE_PATH"][0] = labelfm_env_flags["FILE_PATH"][1]
            else:
                labelfm_env_flags["FILE_PATH"][0] = labelfm_env_flags["FILE_PATH"][1]

        # Output Path Setting
        imgui.spacing()
        outpath_save_clicked = imgui.button("Apply(O)")
        imgui.same_line()
        outpath_revt_clicked = imgui.button("Reset(O)")
        imgui.same_line()
        imgui.push_item_width(imgui.get_window_width() * 0.45)
        outpath_changed, labelfm_env_flags["OUT_PATH"][1] = \
            imgui.input_text("[Output Path]", labelfm_env_flags["OUT_PATH"][1], 256, imgui.INPUT_TEXT_AUTO_SELECT_ALL)
        imgui.pop_item_width()
        imgui.same_line()
        help_marker("Please set the output path before labeling.")

        if outpath_revt_clicked:
            labelfm_env_flags["OUT_PATH"][0] = ""
            labelfm_env_flags["OUT_PATH"][1] = ""
        if outpath_save_clicked:
            if labelfm_setting_flags["AUTO_PATH_CHECK"]:
                if check_data_path(labelfm_env_flags["OUT_PATH"][1]):
                    labelfm_env_flags["OUT_PATH"][0] = labelfm_env_flags["OUT_PATH"][1]
            else:
                labelfm_env_flags["OUT_PATH"][0] = labelfm_env_flags["OUT_PATH"][1]


def collapse_proj_layout_info(labelfm_flags, labelfm_setting_flags, labelfm_env_flags):
    layoutinfo_expanded, layoutinfo_visible = imgui.collapsing_header("Window Layout Info")
    if layoutinfo_expanded:
        imgui.spacing()
        imgui.separator()
        # proj window clocked setting
        _, labelfm_flags["NO_RESIZE"] = imgui.checkbox("[Window Locked]", labelfm_flags["NO_RESIZE"])
        imgui.same_line()
        help_marker("Control if the size of the project window is changeable.")
        imgui.separator()

        # Image Region Setting
        imgui.spacing()
        imregion_changed, imregion_vals = \
            imgui.slider_float2("[Image Region Size]",
                                *(labelfm_flags["IMREGION_WIDTH"], labelfm_flags["IMREGION_HEIGHT"]),
                                min_value=0.0,
                                max_value=int(min(labelfm_flags["WINDOW_WIDTH"], labelfm_flags["WINDOW_HEIGHT"])*0.96),
                                format="%.0f",
                                power=1.0)
        labelfm_flags["IMREGION_WIDTH"], labelfm_flags["IMREGION_HEIGHT"] = imregion_vals
        imgui.same_line()
        help_marker("Drag slider bars to change image region size.")


def collapse_anno_info(labelfm_flags, labelfm_setting_flags, labelfm_env_flags):
    annoinfo_expanded, annoinfo_visible = imgui.collapsing_header("Annotation Info")
    if annoinfo_expanded:
        imgui.spacing()
        # set canvas point color
        _, labelfm_env_flags["CANVAS_ENV"]["POINT_RGBA"] = imgui.color_edit4("[Canvas Point Color]",
                                                                             *labelfm_env_flags["CANVAS_ENV"]["POINT_RGBA"],
                                                                             show_alpha=True)
        # set canvas line color
        _, labelfm_env_flags["CANVAS_ENV"]["LINE_RGBA"]  = imgui.color_edit4("[Canvas Line Color]",
                                                                             *labelfm_env_flags["CANVAS_ENV"]["LINE_RGBA"],
                                                                             show_alpha=True)
        # set canvas plane color
        _, labelfm_env_flags["CANVAS_ENV"]["PLANE_RGBA"] = imgui.color_edit4("[Canvas Plane Color]",
                                                                             *labelfm_env_flags["CANVAS_ENV"]["PLANE_RGBA"],
                                                                             show_alpha=True)
        imgui.same_line()
        help_marker("The color of lines that belong to annotated plane(s).")

        # set canvas point radius
        _, atmp_point_radius = imgui.input_float("[Canvas Point Radius]",
                                                 labelfm_env_flags["CANVAS_ENV"]["POINT_RADIUS"],
                                                 0.5)
        point_radius_bound = (0.5, 10.0)
        if atmp_point_radius < point_radius_bound[0]: atmp_point_radius = point_radius_bound[0]
        if atmp_point_radius > point_radius_bound[1]: atmp_point_radius = point_radius_bound[1]
        labelfm_env_flags["CANVAS_ENV"]["POINT_RADIUS"] = atmp_point_radius
