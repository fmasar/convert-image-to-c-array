from PIL import Image

from enums import ConvTypes, AlphaTypes, RLETypes
from genTempl import GenTempl
from utils import rgb888_to_rgb565

BYTES_PRE_LINE = 20


def convert(image_path: str, output_name: str, conv_type: ConvTypes,
            alpha_type: AlphaTypes, rle_type: RLETypes) -> (str, str):
    image_data = None
    image_data_len = None
    image_comp = None

    mask_data = None
    mask_data_len = None
    mask_comp = None

    im = Image.open(image_path)
    pix = im.load()
    get_templ = GenTempl(output_name, im.width, im.height)

    if conv_type in [ConvTypes.IMAGE, ConvTypes.BOTH]:
        if rle_type in [RLETypes.BOTH, RLETypes.IMAGE]:
            image_data, image_comp, image_data_len = gen_image_data_rle(im, pix)
            comp_redu = ((image_data_len * 2 + image_data_len) / (im.width * im.height * 2))
            print(f"Image reduced size: {comp_redu * 100:.2f} %")
        else:
            image_data = write_image_data(im, pix)
            image_data_len = im.width * im.height

    get_templ.set_image(image_data, image_data_len, image_comp)

    if conv_type in [ConvTypes.MASK, ConvTypes.BOTH]:
        number_of_bits = get_number_of_bits(alpha_type)
        div_by = 8 // number_of_bits
        if rle_type in [RLETypes.BOTH, RLETypes.MASK]:
            mask_data, mask_comp, mask_data_len = gen_mask_data_rle(alpha_type, im, pix)
            comp_redu = ((mask_data_len + mask_data_len) / (((im.width * im.height) + (div_by - 1)) // div_by))
            print(f"Image reduced size: {comp_redu * 100:.2f} %")
        else:
            mask_data = gen_mask_data(alpha_type, im, pix)
            mask_data_len = ((im.width * im.height) + (div_by - 1)) // div_by

    get_templ.set_mask(mask_data, mask_data_len, alpha_type, mask_comp)
    return get_templ.get_templ()


def convert_and_save(image_path: str, output_name: str, output_path: str,
                     conv_type: ConvTypes, alpha_type: AlphaTypes,
                     rle_type: RLETypes) -> None:
    output_h, output_c = convert(image_path, output_name, conv_type, alpha_type, rle_type)

    f_h = open(output_path + output_name + ".h", "w")
    f_c = open(output_path + output_name + ".cpp", "w")
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


def gen_image_data_rle(im: Image, pix) -> (str, str, int):
    output_data = ""
    output_comp = ""

    comp_counter = 0
    rgb565_int_before = -1
    bytes_counter = 0

    for y in range(im.height):
        for x in range(im.width):
            rgb565 = rgb888_to_rgb565(pix[x, y])
            rgb565_int = rgb565[0] << 11 | rgb565[1] << 5 | rgb565[2]
            rgb565_int = (rgb565_int << 8 | ((rgb565_int >> 8) & 255)) & 65535
            if rgb565_int == rgb565_int_before:
                comp_counter += 1

            if (rgb565_int != rgb565_int_before) or (comp_counter == 256):
                if comp_counter == 256:
                    comp_counter -= 1
                if rgb565_int_before != -1:
                    output_data += "0x{:04x}".format(rgb565_int_before)
                    output_comp += "0x{:02x}".format(comp_counter)
                    rgb565_int_before = rgb565_int
                    comp_counter = 0
                    bytes_counter += 1

                    output_data += ","
                    output_comp += ","

                    if bytes_counter % BYTES_PRE_LINE == 0:
                        output_data += "\n"
                        output_comp += "\n"
                else:
                    rgb565_int_before = rgb565_int

    output_data += "0x{:04x}".format(rgb565_int_before)
    output_comp += "0x{:02x}".format(comp_counter)
    bytes_counter += 1

    output_data += "\n"
    output_comp += "\n"

    return output_data, output_comp, bytes_counter


def gen_mask_data(alpha_type: AlphaTypes, im: Image, pix) -> str:
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

                if (bytes_counter == BYTES_PRE_LINE) and (alpha_type != AlphaTypes.BITS_8):
                    bytes_counter = 0
                    output += "\n"

        if alpha_type == AlphaTypes.BITS_8:
            bytes_counter = 0
            output += "\n"

    if mask_cache_counter != 0:
        mask_cache = (mask_cache << parts_in_byte)
        output += "0x{:02x}".format(mask_cache)
        output += "\n"

    return output


def gen_mask_data_rle(alpha_type: AlphaTypes, im: Image, pix) -> (str, str, int):
    output_data = ""
    output_comp = ""

    mask_cache = 0
    mask_cache_counter = 0
    bytes_counter = 0
    number_of_bits = get_number_of_bits(alpha_type)

    comp_counter = 0
    mask_before = -1

    div_by = pow(2, 8 - number_of_bits)
    parts_in_byte = (8 // number_of_bits)
    for y in range(im.height):
        for x in range(im.width):
            mask_cache = (mask_cache << number_of_bits) | (pix[x, y][3] // div_by)
            mask_cache_counter += 1

            if mask_cache_counter == parts_in_byte:
                if mask_cache == mask_before:
                    comp_counter += 1
                else:
                    if (mask_before != -1) or (comp_counter == 256):
                        if comp_counter == 256:
                            comp_counter -= 1
                        output_data += "0x{:02x}".format(mask_before)
                        output_comp += "0x{:02x}".format(comp_counter)
                        mask_before = mask_cache
                        comp_counter = 0
                        bytes_counter += 1

                        output_data += ","
                        output_comp += ","

                        if bytes_counter % BYTES_PRE_LINE == 0:
                            output_data += "\n"
                            output_comp += "\n"

                    else:
                        mask_before = mask_cache

                mask_cache = 0
                mask_cache_counter = 0

    output_data += "0x{:02x}".format(mask_before)
    output_comp += "0x{:02x}".format(comp_counter)
    bytes_counter += 1

    if mask_cache_counter != 0:
        if bytes_counter % BYTES_PRE_LINE == 0:
            output_data += "\n"
            output_comp += "\n"
        mask_cache = (mask_cache << (8 - (number_of_bits * mask_cache_counter)))
        output_data += ",0x{:02x}".format(mask_cache)
        output_comp += ",0x{:02x}".format(0)
        bytes_counter += 1

    output_data += "\n"
    output_comp += "\n"

    return output_data, output_comp, bytes_counter


def get_number_of_bits(alpha_type: AlphaTypes) -> int:
    match alpha_type:
        case AlphaTypes.BITS_8:
            return 8
        case AlphaTypes.BITS_4:
            return 4
        case AlphaTypes.BITS_2:
            return 2
        case AlphaTypes.BITS_1:
            return 1
        case _:
            assert False, "Not implemented AlphaType option"
