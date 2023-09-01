from math import pow, sqrt, atan2, pi, cos, sin, exp


def rgb_to_xyz(rgb):
    """Преобразуем RGB в XYZ"""

    # Based on http://www.easyrgb.com/index.php?X=MATH&H=02
    r = rgb[0] / 255
    g = rgb[1] / 255
    b = rgb[2] / 255

    r = pow(((r + 0.055) / 1.055), 2.4) if r > 0.04045 else r / 12.92
    g = pow(((g + 0.055) / 1.055), 2.4) if g > 0.04045 else g / 12.92
    b = pow(((b + 0.055) / 1.055), 2.4) if b > 0.04045 else b / 12.92

    r *= 100
    g *= 100
    b *= 100

    # Observer = 2°, Illuminant = D65
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    return x, y, z


def xyz_to_lab(xyz):
    """Преобразуем XYZ в Lab"""

    # Based on http://www.easyrgb.com/index.php?X=MATH&H=07
    # Observer = 2°, Illuminant = D65
    ref_x = 95.047
    ref_y = 100.000
    ref_z = 108.883

    x = xyz[0] / ref_x
    y = xyz[1] / ref_y
    z = xyz[2] / ref_z

    x = pow(x, 1 / 3) if x > 0.008856 else (7.787 * x) + (16 / 116)
    y = pow(y, 1 / 3) if y > 0.008856 else (7.787 * y) + (16 / 116)
    z = pow(z, 1 / 3) if z > 0.008856 else (7.787 * z) + (16 / 116)

    l = (116 * y) - 16
    a = 500 * (x - y)
    b = 200 * (y - z)
    return l, a, b


def rgb_to_lab(rgb):
    """Преобразуем RGB в Lab"""

    xyz = rgb_to_xyz(rgb)
    return xyz_to_lab(xyz)


def equal_lab(rgb1, rgb2):
    """Вычисляет разницу между двумя Lab цветами CIE76"""

    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)
    delta = sqrt(pow(lab2[0] - lab1[0], 2) + pow(lab2[1] - lab1[1], 2) + pow(lab2[2] - lab1[2], 2))
    return delta < 2.3


def equal_ciede2000(rgb1, rgb2):
    """Вычисляет разницу между двумя Lab цветами CIEDE2000"""
    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)
    k_l = 1.0
    k_c = 1.0
    k_h = 1.0
    l_bar_prime = 0.5 * (lab1[0] + lab2[0])
    c1 = sqrt(lab1[1] * lab1[1] + lab1[2] * lab1[2])
    c2 = sqrt(lab2[1] * lab2[1] + lab2[2] * lab2[2])
    c_bar = 0.5 * (c1 + c2)
    c_bar7 = c_bar * c_bar * c_bar * c_bar * c_bar * c_bar * c_bar
    g = 0.5 * (1.0 - sqrt(c_bar7 / (c_bar7 + 6103515625.0)))
    a1_prime = lab1[1] * (1.0 + g)
    a2_prime = lab2[1] * (1.0 + g)
    c1_prime = sqrt(a1_prime * a1_prime + lab1[2] * lab1[2])
    c2_prime = sqrt(a2_prime * a2_prime + lab2[2] * lab2[2])
    c_bar_prime = 0.5 * (c1_prime + c2_prime)
    h1_prime = (atan2(lab1[2], a1_prime) * 180.0) / pi
    if h1_prime < 0.:
        h1_prime += 360.0
    h2_prime = (atan2(lab2[2], a2_prime) * 180.0) / pi
    if h2_prime < 0.0:
        h2_prime += 360.0
    h_bar_prime = (0.5 * (h1_prime + h2_prime + 360.0)) if abs(h1_prime - h2_prime) > 180.0 else (
            0.5 * (h1_prime + h2_prime))
    t = 1.0 - 0.17 * cos(pi * (h_bar_prime - 30.0) / 180.0) + 0.24 * cos(pi * (2.0 * h_bar_prime) / 180.0) \
        + 0.32 * cos(pi * (3.0 * h_bar_prime + 6.0) / 180.0) - 0.20 * cos(pi * (4.0 * h_bar_prime - 63.0) / 180.0)

    if abs(h2_prime - h1_prime) <= 180.0:
        dh_prime = h2_prime - h1_prime
    else:
        dh_prime = (h2_prime - h1_prime + 360.0) if h2_prime <= h1_prime else (h2_prime - h1_prime - 360.0)
    d_l_prime = lab2[0] - lab1[0]
    d_c_prime = c2_prime - c1_prime
    d_h_prime = 2.0 * sqrt(c1_prime * c2_prime) * sin(pi * (0.5 * dh_prime) / 180.0)
    s_l = 1.0 + ((0.015 * (l_bar_prime - 50.0) * (l_bar_prime - 50.0)) / sqrt(
        20.0 + (l_bar_prime - 50.0) * (l_bar_prime - 50.0)))
    s_c = 1.0 + 0.045 * c_bar_prime
    s_h = 1.0 + 0.015 * c_bar_prime * t
    d_theta = 30.0 * exp(-((h_bar_prime - 275.0) / 25.0) * ((h_bar_prime - 275.0) / 25.0))
    c_bar_prime7 = c_bar_prime * c_bar_prime * c_bar_prime * c_bar_prime * c_bar_prime * c_bar_prime * c_bar_prime
    r_c = sqrt(c_bar_prime7 / (c_bar_prime7 + 6103515625.0))
    r_t = -2.0 * r_c * sin(pi * (2.0 * d_theta) / 180.0)
    delta = sqrt(
        (d_l_prime / (k_l * s_l)) * (d_l_prime / (k_l * s_l)) +
        (d_c_prime / (k_c * s_c)) * (d_c_prime / (k_c * s_c)) +
        (d_h_prime / (k_h * s_h)) * (d_h_prime / (k_h * s_h)) +
        (d_c_prime / (k_c * s_c)) * (d_h_prime / (k_h * s_h)) * r_t)
    return delta