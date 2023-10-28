#!/usr/bin/python

from PIL import Image
import argparse
import os


def rgb888_to_rgb565(rgb888):
    r = rgb888[0]
    g = rgb888[1]
    b = rgb888[2]

    r2 = round((31.0*r)/255)
    g2 = round((63.0*g)/255)
    b2 = round((31.0*b)/255)

    return tuple((r2, g2, b2))


def convert(image_path, output_name):
    im = Image.open(image_path)
    pix = im.load()
    f_c = open(output_name + ".c", "w")
    f_h = open(output_name + ".h", "w")

    f_h.write(f"#ifndef IMAGE_{output_name.upper()}_H\n")
    f_h.write(f"#define IMAGE_{output_name.upper()}_H\n")
    f_h.write("\n")
    f_h.write("#include <include/AimiGTypes.h>\n")
    f_h.write(f"extern const AimiImageData {output_name};\n")
    f_h.write("\n")
    f_h.write(f"#endif  // IMAGE_{output_name.upper()}_H\n")

    f_c.write(f"#include \"{output_name}.h\"\n\n")
    f_c.write(f"const uint16_t {output_name}_data[{im.width * im.height}] = {{\n")

    for y in range(im.height):
        for x in range(im.width):
            rgb565 = rgb888_to_rgb565(pix[x, y])
            rgb565_int = rgb565[0] << 11 | rgb565[1] << 5 | rgb565[2]
            f_c.write("0x{:04x}".format(rgb565_int))
            if not ((x == im.width - 1) and (y == im.height - 1)):
                f_c.write(",")
        f_c.write("\n")
    f_c.write("};\n\n")
    f_c.write(f"const AimiImageData {output_name}={{{im.width}, {im.height}, {output_name}_data}};\n")


def validate_file(file):
    if not os.path.exists(file):
        raise argparse.ArgumentTypeError("{0} file does not exist".format(file))
    return file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert image to C header file in RGB565 format.')
    try:
        parser.add_argument('--input', dest='input', required=True, type=validate_file, help='Input image',
                            metavar="FILE")

        parser.add_argument('--output', dest='output', required=True, help='Output C header file', metavar="FILE")
    except:
        exit(1)

    args = parser.parse_args()

    if args.input is None and args.output is None:
        exit(1)

    convert(args.input, args.output)
