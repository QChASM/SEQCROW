"""random functions that are used more than once"""
def iter2str(t):
    """converts tuple to str and cuts off ()"""
    return str(t)[1:-1]

def contrast_bw(color):
    """
    color: RGB tuple
    luminance defined here: https://www.w3.org/TR/WCAG20/#relativeluminancedef
    if luminance is < 0.179, color contrasts more with black, so black is returned
    otherwise, white
    """
    lumin = [0, 0, 0]
    for i in range(0, 3):
        if (color[i] / 255.) <= 0.03928:
            lumin[i] = color[i] / (12.92 * 255)
        else:
            lumin[i] = (((color[i] / 255) + 0.055) / 1.055) ** 2.4
    luminosity = 0.2126 * lumin[0] + 0.7152 * lumin[1] + 0.0722 * lumin[2]
    if luminosity > 0.179:
        return "black"
    return "white"
