from PIL import Image

from enums import AlphaTypes, RLETypes
from templates import fill_template_image, fill_template_image_mask
from utils import rgb888_to_rgb565

BYTES_PRE_LINE = 20


def convert(image_path: str, output_name: str, output_path: str, alpha_type: AlphaTypes, rle_type: RLETypes) -> None:
    assert rle_type in [RLETypes.RLE_OFF, RLETypes.RLE_BOTH], "Not implemented RLEType option"
    im = Image.open(image_path)
    pix = im.load()
    f_h = open(output_path + output_name + ".h", "w")
    f_c = open(output_path + output_name + ".cpp", "w")

    # write_image_start(f_c, f_h, output_name, alpha_type, rle_type, im)

    image_data = write_image_data(im, pix)
    image_data_len = im.width * im.height

    if alpha_type != AlphaTypes.ALPHA_NONE:
        mask_data = write_mask_data(alpha_type, im, pix)
        number_of_bits = get_number_of_bits(alpha_type)
        div_by = 8 // number_of_bits
        mask_data_len = ((im.width * im.height) + (div_by - 1)) // div_by
        (output_h, output_c) = fill_template_image_mask(output_name, im.width, im.height, image_data, image_data_len,
                                                        alpha_type.value, mask_data, mask_data_len)
    else:
        (output_h, output_c) = fill_template_image(output_name, im.width, im.height, image_data, image_data_len)

    f_h.write(output_h)
    f_c.write(output_c)


def write_image_data(im: Image, pix) -> str:
    output = ""
    for y in range(im.height):
        for x in range(im.width):
            rgb565 = rgb888_to_rgb565(pix[x, y])
            rgb565_int = rgb565[0] << 11 | rgb565[1] << 5 | rgb565[2]
            rgb565_int = (rgb565_int << 8 | ((rgb565_int >> 8) & 255)) & 65535
            output += "0x{:04x}".format(rgb565_int)
            if not ((x == im.width - 1) and (y == im.height - 1)):
                output += ","

        output += "\n"
    return output


def write_mask_data(alpha_type: AlphaTypes, im: Image, pix) -> str:
    output = ""

    mask_cache = 0
    mask_cache_counter = 0
    bytes_counter = 0
    number_of_bits = get_number_of_bits(alpha_type)

    div_by = pow(2, 8 - number_of_bits)
    parts_in_byte = (8 // number_of_bits)
    for y in range(im.height):
        for x in range(im.width):
            mask_cache = (mask_cache << number_of_bits) | (pix[x, y][3] // div_by)
            mask_cache_counter += 1
            if mask_cache_counter == parts_in_byte:
                output += "0x{:02x}".format(mask_cache)
                mask_cache = 0
                mask_cache_counter = 0
                bytes_counter += 1
                if not ((x == im.width - 1) and (y == im.height - 1)):
                    output += ","

                if (bytes_counter == BYTES_PRE_LINE) and (alpha_type != AlphaTypes.ALPHA_8BITS):
                    bytes_counter = 0
                    output += "\n"

        if alpha_type == AlphaTypes.ALPHA_8BITS:
            bytes_counter = 0
            output += "\n"

    if mask_cache_counter != 0:
        mask_cache = (mask_cache << parts_in_byte)
        output += "0x{:02x}".format(mask_cache)
        output += "\n"

    return output


def get_number_of_bits(alpha_type: AlphaTypes) -> int:
    match alpha_type:
        case AlphaTypes.ALPHA_8BITS:
            return 8
        case AlphaTypes.ALPHA_4BITS:
            return 4
        case AlphaTypes.ALPHA_2BITS:
            return 2
        case AlphaTypes.ALPHA_1BIT:
            return 1
        case _:
            assert False, "Not implemented AlphaType option"
