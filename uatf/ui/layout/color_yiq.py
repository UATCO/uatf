"""
http://www.progmat.uaem.mx:8080/artVol2Num2/Articulo3Vol2Num2.pdf
https://github.com/mapbox/pixelmatch
"""


def equal_yiq(rgba1, rgba2):

    a1 = rgba1[3] / 255 if len(rgba1) > 3 else 1
    a2 = rgba2[3] / 255 if len(rgba2) > 3 else 1

    rgb1 = (255 + (rgba1[0] - 255) * a1, 255 + (rgba1[1] - 255) * a1, 255 + (rgba1[2] - 255) * a1)
    rgb2 = (255 + (rgba2[0] - 255) * a2, 255 + (rgba2[1] - 255) * a2, 255 + (rgba2[2] - 255) * a2)

    y = (rgb1[0] * 0.29889531 + rgb1[1] * 0.58662247 + rgb1[2] * 0.11448223) - \
        (rgb2[0] * 0.29889531 + rgb2[1] * 0.58662247 + rgb2[2] * 0.11448223)

    i = (rgb1[0] * 0.59597799 - rgb1[1] * 0.27417610 - rgb1[2] * 0.32180189) - \
        (rgb2[0] * 0.59597799 - rgb2[1] * 0.27417610 - rgb2[2] * 0.32180189)

    q = (rgb1[0] * 0.21147017 - rgb1[1] * 0.52261711 + rgb1[2] * 0.31114694) - \
        (rgb2[0] * 0.21147017 - rgb2[1] * 0.52261711 + rgb2[2] * 0.31114694)

    delta = 0.5053 * y * y + 0.299 * i * i + 0.1957 * q * q
    return delta < 8.1
