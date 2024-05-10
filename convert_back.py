import re
from typing import Optional

from PIL import Image

from enums import AlphaTypes
from utils import rgb565_to_rgb888


def parse_input(image_path: str) -> tuple[int, int, str, str, str]:
    image_data = ""
    mask_data = ""
    mask_type = ""
    image_width = 0
    image_height = 0
    with open(image_path) as file:
        writing: Optional[str] = None
        while line := file.readline():
            line = line.rstrip()
            if writing is None:
                if re.search("^const uint16_t .+_image_data.+", line):
                    writing = "image_data"
                elif re.search("^const uint8_t .+_mask_data.+", line):
                    writing = "mask_data"
                elif m := re.search("^const AimiImageData .+_image={.+, .+, .+};", line):
                    m = re.search("{.+, .+, .+}", m.group(0))
                    text = m.group(0)[1:-1].replace(" ", "")
                    split = text.split(",")
                    image_width = int(split[0])
                    image_height = int(split[1])
                elif m := re.search("aimi_mask_type_bits[0-9]", line):
                    mask_type = m.group(0)[-1]
            else:
                if re.search("};", line):
                    writing = None
                else:
                    match writing:
                        case "image_data":
                            image_data += line
                        case "mask_data":
                            mask_data += line
    return image_width, image_height, image_data, mask_data, mask_type


def data_to_list(data_str: str) -> list:
    data_list = []
    for x in data_str.split(","):
        data_list.append(int(x, 0))
    return data_list


def mask_to_full(mask_data: list, alpha_type: AlphaTypes) -> list:
    if alpha_type == AlphaTypes.BITS_8:
        return mask_data
    output = []
    for x in mask_data:
        match alpha_type:
            case AlphaTypes.BITS_4:
                output.append(((x >> 4) & 0x7F) * 17)
                output.append((x & 0x7F) * 17)
            case AlphaTypes.BITS_2:
                output.append(((x >> 6) & 0x03) * 58)
                output.append(((x >> 4) & 0x03) * 58)
                output.append(((x >> 2) & 0x03) * 58)
                output.append((x & 0x03) * 58)
            case AlphaTypes.BITS_1:
                output.append(((x >> 7) & 0x01) * 255)
                output.append(((x >> 6) & 0x01) * 255)
                output.append(((x >> 5) & 0x01) * 255)
                output.append(((x >> 4) & 0x01) * 255)
                output.append(((x >> 3) & 0x01) * 255)
                output.append(((x >> 2) & 0x01) * 255)
                output.append(((x >> 1) & 0x01) * 255)
                output.append((x & 0x01) * 255)
    return output


def data_list_into_image(image_width: int, image_height: int, image_data: list,
                         mask_data: Optional[list]) -> Image:
    pixels = []
    i = 0
    for color in image_data:
        color = ((color << 8) | ((color >> 8) & 0xFF)) & 65535
        pixel = rgb565_to_rgb888(color)
        alpha = 255
        if mask_data is not None:
            alpha = mask_data[i]
        pixel_alpha = (pixel[0], pixel[1], pixel[2], alpha)
        pixels.append(pixel_alpha)
        i += 1

    im = Image.new("RGBA", (image_width, image_height))
    im.putdata(pixels)
    return im


def convert_back_and_save(image_path: str, output_path: str) -> None:
    image_width, image_height, image_data, mask_data, mask_type = parse_input(image_path)
    assert image_data, "No image data detected!"
    image_data_list = data_to_list(image_data)
    mask_data_list: Optional[list] = None
    if mask_type:
        assert mask_data, "No mask data detected!"
        match mask_type:
            case "8":
                alpha_type = AlphaTypes.BITS_8
            case "4":
                alpha_type = AlphaTypes.BITS_4
            case "2":
                alpha_type = AlphaTypes.BITS_2
            case "1":
                alpha_type = AlphaTypes.BITS_1
            case _:
                assert False, "Unsupported alpha type"
        mask_data_list = data_to_list(mask_data)
        mask_data_list = mask_to_full(mask_data_list, alpha_type)
    im = data_list_into_image(image_width, image_height, image_data_list, mask_data_list)
    im.save(f"{output_path}.png")


convert_back_and_save("out/bulletdual_new.cpp", "output")
