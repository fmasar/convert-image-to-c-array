def fill_template_image(file_name: str, image_width: int, image_height: int, image_data: str, image_data_len: int) -> (str, str):
    final_data_type = "AimiImageData"
    name_suffix = ""
    output_h = fill_template_h(file_name, name_suffix, final_data_type)
    output_c = fill_template_c_start(file_name)
    output_c += fill_template_c_image(file_name, name_suffix, image_width, image_height, image_data, image_data_len)
    output_c += "\n"
    return output_h, output_c


def fill_template_image_mask(file_name: str, image_width: int, image_height: int, image_data: str, image_data_len: int, mask_type: int, mask_data: str, mask_data_len: int) -> (str, str):
    final_data_type = "AimiImageMaskData"
    name_suffix = ""
    image_name_suffix = "_image"
    mask_name_suffix = "_mask"
    output_h = fill_template_h(file_name, name_suffix, final_data_type)
    output_c = fill_template_c_start(file_name)
    output_c += fill_template_c_image(file_name, image_name_suffix, image_width, image_height, image_data, image_data_len)
    output_c += fill_template_c_mask(file_name, mask_name_suffix, mask_type, image_width, image_height, mask_data, mask_data_len)
    fill_template_c_image_mask_wrapper(file_name, name_suffix, image_name_suffix, mask_name_suffix, final_data_type)
    output_c += "\n"
    return output_h, output_c


def fill_template_c_start(file_name: str) -> str:
    output = f"#include \"{file_name}.h\"\n"
    return output


def fill_template_c_image(file_name: str, image_name_suffix: str, image_width: int, image_height: int, data: str, data_len: int) -> str:
    output = "\n"
    output += f"const uint16_t {file_name}_image_data[{data_len}] = {{\n"
    output += data
    output += f"}};  // {file_name}_image_data\n"
    output += "\n"
    output += f"const AimiImageData {file_name}{image_name_suffix}={{{image_width}, {image_height}, {file_name}_image_data}};\n"
    return output


def fill_template_c_mask(file_name: str, mask_name_suffix: str, mask_type: int, image_width: int, image_height: int, data: str, data_len: int) -> str:
    output = "\n"
    output += f"const uint8_t {file_name}_mask_data[{data_len}] = {{\n"
    output += data
    output += f"}};  // {file_name}_mask_data\n"
    output += "\n"
    output += f"const AimiMaskData {file_name}{mask_name_suffix}={{{image_width}, {image_height}, {mask_type}, {file_name}_mask_data}};\n"
    return output


def fill_template_c_image_mask_wrapper(file_name: str, name_suffix: str, image_name_suffix: str, mask_name_suffix: str, final_data_type: str) -> str:
    output = f"const {final_data_type} {file_name}{name_suffix}={{&{file_name}{image_name_suffix}, &{file_name}{mask_name_suffix}}};"
    return output


def fill_template_h(file_name: str, name_suffix: str, final_data_type: str) -> str:
    output = f"#ifndef IMAGE_{file_name.upper()}_H\n"
    output += f"#define IMAGE_{file_name.upper()}_H\n"
    output += "\n"
    output += "#include <include/AimiGTypes.h>\n"
    output += "\n"
    output += f"extern const {final_data_type} {file_name}{name_suffix};\n"
    output += "\n"
    output += f"#endif  // IMAGE_{file_name.upper()}_H\n"
    return output
