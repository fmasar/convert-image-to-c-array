def rgb888_to_rgb565(rgb888: tuple):
    r = rgb888[0]
    g = rgb888[1]
    b = rgb888[2]

    r2 = round((31.0 * r) / 255)
    g2 = round((63.0 * g) / 255)
    b2 = round((31.0 * b) / 255)

    return tuple((r2, g2, b2))


def rgb565_to_rgb888(rgb565: int) -> tuple:
    r = (rgb565 >> 11) & 0x1F
    g = (rgb565 >> 5) & 0x3F
    b = rgb565 & 0x1F

    r2 = round((255 * r) / 31)
    g2 = round((255 * g) / 63)
    b2 = round((255 * b) / 31)

    return tuple((r2, g2, b2))
