# http://www.eejournal.ktu.lt/index.php/elt/article/view/10058/5000


def is_aa(img, x1, y1, width, height, img2=None):
    rgb1 = img[x1, y1]
    a1 = rgb1[3] / 255 if len(rgb1) > 3 else 1
    rgb1 = (255 + (rgb1[0] - 255) * a1, 255 + (rgb1[1] - 255) * a1, 255 + (rgb1[2] - 255) * a1)

    x0 = max(x1 - 1, 0)
    y0 = max(y1 - 1, 0)
    x2 = min(x1 + 1, width - 1)
    y2 = min(y1 + 1, height - 1)

    zeroes = 0
    positives = 0
    negatives = 0

    min_c = 0
    max_c = 0
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0

    # go through 8 adjacent pixels
    for x in range(x0, x2 + 1):
        for y in range(y0, y2 + 1):
            if x == x1 and y == y1:
                continue

            rgb2 = img[x, y]
            a2 = rgb2[3] / 255 if len(rgb2) > 3 else 1
            rgb2 = (255 + (rgb2[0] - 255) * a2, 255 + (rgb2[1] - 255) * a2, 255 + (rgb2[2] - 255) * a2)

            # brightness delta between the center pixel and adjacent one
            current_delta = (rgb1[0] * 0.29889531 + rgb1[1] * 0.58662247 + rgb1[2] * 0.11448223) - \
                            (rgb2[0] * 0.29889531 + rgb2[1] * 0.58662247 + rgb2[2] * 0.11448223)

            # count the number of equal, darker and brighter adjacent pixels
            if current_delta == 0:
                zeroes += 1
            elif current_delta < 0:
                negatives += 1
            else:
                positives += 1

            # if found more than 2 equal siblings, it's definitely not anti-aliasing
            if zeroes > 2:
                return False

            if not img2:
                continue

            # remember the darkest pixel
            if current_delta < min_c:
                min_c = current_delta
                min_x = x
                min_y = y

            # remember the brightest pixel
            if current_delta > max_c:
                max_c = current_delta
                max_x = x
                max_y = y

    if not img2:
        return True

    # if there are no both darker and brighter pixels among siblings, it's not anti-aliasing
    if negatives == 0 or positives == 0:
        return False

    # if either the darkest or the brightest pixel has more than 2 equal siblings in both images
    # (definitely not anti-aliased), this pixel is anti-aliased
    return (not is_aa(img, min_x, min_y, width, height) and not is_aa(img2, min_x, min_y, width, height)) or \
           (not is_aa(img, max_x, max_y, width, height) and not is_aa(img2, max_x, max_y, width, height))
