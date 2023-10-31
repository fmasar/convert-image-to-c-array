def rgb888_to_rgb565(rgb888: tuple):
    r = rgb888[0]
    g = rgb888[1]
    b = rgb888[2]

    r2 = round((31.0 * r) / 255)
    g2 = round((63.0 * g) / 255)
    b2 = round((31.0 * b) / 255)

    return tuple((r2, g2, b2))
