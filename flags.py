# labeFM window flags
LABELFM_WINDOW = {
    "EXPANDED":            False,
    "OPENED":              True,
    "NO_COLLAPSE":         True,
    "NO_RESIZE":           False,
    "WINDOW_WIDTH":        890,
    "WINDOW_HEIGHT":       630,
    "IMREGION_WIDTH":      280,
    "IMREGION_HEIGHT":     300,
    "POINTLST_WIDTH":      200,
    "DECISION_WIDTH":      120,
}

# labelFM setting Application flags
LABELFM_SETTING_APP = {
    "EXPANDED":            False,
    "OPENED":              False,
    "NO_COLLAPSE":         False,
    "AUTO_PATH_CHECK":     False,
}

# labelFM state window flags
LABELFM_STATE_WINDOW = {
    "EXPANDED":            False,
    "OPENED":              False,
    "NO_COLLAPSE":         False,
}

# labelFM Help-Info window flags
LABELFM_INFO_WINDOW = {
    "EXPANDED":            False,
    "OPENED":              False,
    "NO_MOVE":             True,
}

# labelFM Env flags
LABELFM_ENV = {
    "FILE_PATH":           ["", ""],
    "OUT_PATH":            ["", ""],
    "DATA_LIST":           [],
    "TEXTID_CLEAR_BUFFER": [],
    "DATA_CLEAR_SIGNAL":   False,
    "IMG_SELECTED":        -1,
    "SELECTION_CHANGED":   False,
    "DATA_REFRESH_STATE":  False,
    "DATA_REFRESH_TICK":   0.0,
    "CURR_IMAGE_TID":      -1,
    "CURR_IMAGE_WIDTH":    0,
    "CURR_IMAGE_HEIGHT":   0,
    "CURR_ANNO_MODE":      0,
    "ANNO_MODE_CHANGED":   False,

    # labelFM Canvas Env flags
    "CANVAS_ENV": {
                           "POINT_RGBA":    (1.0, 1.0, 0.0, 0.8),
                           "LINE_RGBA":     (0.0, 0.8, 0.3, 0.8),
                           "PLANE_RGBA":    (0.4, 0.4, 0.6, 0.8),
                           "POINT_RADIUS":  2.0,
                           "POINT_HOVERED": -1,
                           "ADDING_LINE":   False,
                           "LINE_CACHE":    -1,
                           "PLANE_CACHE":   [],
    }
}

# labelFM Annotation params
LABELFM_ANNO_PARAMS = {
    "POINTS":              [],
    "POINT_SELECTED":      -1,
    "POINT_ANNO_LOCKED":   False,
    "POINT_CLEAR_SIGNAL":  False,
    "LINES":               [],
    "ITEM_SELECTED":       -1,
}
