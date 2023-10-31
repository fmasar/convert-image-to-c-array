from io import TextIOWrapper
from typing import TextIO
from PIL import Image
from enums import AlphaTypes
from utils import rgb888_to_rgb565

BYTES_PRE_LINE = 20


def convert(image_path: str, output_name: str, output_path: str, alpha_type: AlphaTypes) -> None:
    im = Image.open(image_path)
    pix = im.load()
    f_c = open(output_path + output_name + ".cpp", "w")
    f_h = open(output_path + output_name + ".h", "w")

    write_image_start(f_c, f_h, output_name, alpha_type, im)

    write_image_data(f_c, output_name, alpha_type, im, pix)

    if alpha_type != AlphaTypes.ALPHA_NONE:
        write_mask_data(f_c, output_name, alpha_type, im, pix)


def write_image_start(f_c: TextIO, f_h: TextIO, class_name: str, alpha_type: AlphaTypes, im: Image) -> None:
    f_h.write(f"#ifndef IMAGE_{class_name.upper()}_H\n")
    f_h.write(f"#define IMAGE_{class_name.upper()}_H\n")
    f_h.write("\n")
    f_h.write("#include <include/AimiGTypes.h>\n\n")
    if alpha_type == AlphaTypes.ALPHA_NONE:
        f_h.write(f"extern const AimiImageData {class_name};\n")
    else:
        f_h.write(f"extern const AimiImageMaskData {class_name};\n")

    f_h.write("\n")
    f_h.write(f"#endif  // IMAGE_{class_name.upper()}_H\n")

    f_c.write(f"#include \"{class_name}.h\"\n\n")
    f_c.write(f"const uint16_t {class_name}_data[{im.width * im.height}] = {{\n")


def write_image_data(f_c: TextIO, class_name: str, alpha_type: AlphaTypes, im: Image, pix) -> None:
    for y in range(im.height):
        for x in range(im.width):
            rgb565 = rgb888_to_rgb565(pix[x, y])
            rgb565_int = rgb565[0] << 11 | rgb565[1] << 5 | rgb565[2]
            rgb565_int = (rgb565_int << 8 | (rgb565_int >> 8 & 255)) & 65535
            f_c.write("0x{:04x}".format(rgb565_int))
            if not ((x == im.width - 1) and (y == im.height - 1)):
                f_c.write(",")

        f_c.write("\n")
    f_c.write("};\n\n")
    if alpha_type == AlphaTypes.ALPHA_NONE:
        f_c.write(f"const AimiImageData {class_name}={{{im.width}, {im.height}, {class_name}_data}};\n")
    else:
        f_c.write(f"const AimiImageData {class_name}_image={{{im.width}, {im.height}, {class_name}_data}};\n")


def write_mask_start(f_c: TextIO, class_name: str, alpha_type: AlphaTypes, im: Image) -> None:
    f_c.write("\n")
    if alpha_type == AlphaTypes.ALPHA_8BITS:
        f_c.write(f"const uint8_t {class_name}_mask_data[{im.width * im.height}] = {{\n")
    elif alpha_type == AlphaTypes.ALPHA_4BITS:
        f_c.write(f"const uint8_t {class_name}_mask_data[{((im.width * im.height) + 1) // 2}] = {{\n")
    elif alpha_type == AlphaTypes.ALPHA_1BIT:
        f_c.write(f"const uint8_t {class_name}_mask_data[{((im.width * im.height) + 7) // 8}] = {{\n")


def write_mask_data(f_c: TextIO, class_name: str, alpha_type: AlphaTypes, im: Image, pix) -> None:
    write_mask_start(f_c, class_name, alpha_type, im)

    mask_cache = 0
    mask_cache_counter = 0
    bytes_counter = 0
    match alpha_type:
        case AlphaTypes.ALPHA_8BITS:
            number_of_bits = 8
        case AlphaTypes.ALPHA_4BITS:
            number_of_bits = 4
        case AlphaTypes.ALPHA_2BITS:
            number_of_bits = 2
        case AlphaTypes.ALPHA_1BIT:
            number_of_bits = 1
        case _:
            assert False, "Not implemented AlphaType option"

    div_by = pow(2, 8 - number_of_bits)
    parts_in_byte = (8 // number_of_bits)
    for y in range(im.height):
        for x in range(im.width):
            mask_cache = (mask_cache << 4) | (pix[x, y][3] // div_by)
            mask_cache_counter += 1
            if mask_cache_counter == parts_in_byte:
                f_c.write("0x{:02x}".format(mask_cache))
                mask_cache = 0
                mask_cache_counter = 0
                bytes_counter += 1
                if not ((x == im.width - 1) and (y == im.height - 1)):
                    f_c.write(",")

                if (bytes_counter == BYTES_PRE_LINE) or (alpha_type == AlphaTypes.ALPHA_8BITS):
                    bytes_counter = 0
                    f_c.write("\n")

    if mask_cache_counter != 0:
        mask_cache = (mask_cache << parts_in_byte)
        f_c.write("0x{:02x}".format(mask_cache))
        f_c.write("\n")

    f_c.write("};\n\n")
    f_c.write(f"const AimiMaskData {class_name}_mask=")
    f_c.write(f"{{{im.width}, {im.height}, {alpha_type.value}, {class_name}_mask_data}};\n\n")
    f_c.write(f"const AimiImageMaskData {class_name}={{&{class_name}_image, &{class_name}_mask}};\n")
