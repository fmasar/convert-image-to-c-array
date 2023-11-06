from enums import AlphaTypes


class GenTempl:
    def __init__(self, final_name: str, width: int, height: int) -> None:
        self._final_name = final_name
        self._width = width
        self._height = height

        self._image_data = None
        self._image_data_len = None
        self._image_comp = None

        self._mask_data = None
        self._mask_data_len = None
        self._mask_type = None
        self._mask_comp = None

        self._templ_h = ""
        self._templ_c = ""
        self._define_prefix = ""
        self._final_data_type = ""
        self._image_name_suffix = ""
        self._mask_name_suffix = ""

    def set_image(self, image_data: str, image_data_len: int, image_comp: str = None) -> None:
        self._image_data = image_data
        self._image_data_len = image_data_len
        self._image_comp = image_comp

    def set_mask(self, mask_data: str, mask_data_len: int, alpha_type: AlphaTypes, mask_comp: str = None) -> None:
        self._mask_data = mask_data
        self._mask_data_len = mask_data_len
        self._mask_type = alpha_type
        self._mask_comp = mask_comp

    def get_templ(self) -> (str, str):
        self._generate_templ()
        return self._templ_h, self._templ_c

    def _generate_templ(self) -> None:
        self._set_variables()
        self._templ_h = self._fill_template_h()
        self._templ_c = self._fill_template_c_start()
        if (self._image_data is not None) and (self._mask_data is not None):
            if self._image_comp is None:
                self._templ_c += self._fill_template_c_image()
            else:
                self._templ_c += self._fill_template_c_image_rle()

            if self._mask_comp is None:
                self._templ_c += self._fill_template_c_mask()
            else:
                self._templ_c += self._fill_template_c_mask_rle()

            self._templ_c += self._fill_template_c_image_mask_wrapper()
        elif (self._image_data is not None) and (self._mask_data is None):
            if self._image_comp is None:
                self._templ_c += self._fill_template_c_image()
            else:
                self._templ_c += self._fill_template_c_image_rle()
        elif (self._image_data is None) and (self._mask_data is not None):
            if self._mask_comp is None:
                self._templ_c += self._fill_template_c_mask()
            else:
                self._templ_c += self._fill_template_c_mask_rle()
        else:
            assert False, "Unable to generate template!"

    def _set_variables(self):
        if (self._image_data is not None) and (self._mask_data is not None):
            self._define_prefix = "IMAGE"
            self._image_name_suffix = ""

            if (self._image_comp is None) and (self._mask_comp is None):
                self._image_name_suffix = "_image"
                self._mask_name_suffix = "_mask"
                self._final_data_type = "AimiImageMask"
            elif (self._image_comp is not None) and (self._mask_comp is None):
                self._image_name_suffix = "_image_rle"
                self._mask_name_suffix = "_mask"
                self._final_data_type = "AimiImageRLEMask"
            elif (self._image_comp is not None) and (self._mask_comp is not None):
                self._image_name_suffix = "_image_rle"
                self._mask_name_suffix = "_mask_rle"
                self._final_data_type = "AimiImageMaskRLE"
            else:
                assert False, "Not implemented"
        elif (self._image_data is not None) and (self._mask_data is None):
            self._define_prefix = "IMAGE"
            self._image_name_suffix = ""
            if self._image_comp is None:
                self._final_data_type = "AimiImageData"
            else:
                self._final_data_type = "AimiImageDataRLE"
        elif (self._image_data is None) and (self._mask_data is not None):
            self._define_prefix = "MASK"
            self._image_name_suffix = ""
            if self._image_comp is None:
                self._final_data_type = "AimiMaskData"
            else:
                self._final_data_type = "AimiMaskDataRLE"
        else:
            assert False, "Not implemented"

    def _fill_template_h(self) -> str:
        output = f"#ifndef {self._define_prefix.upper()}_{self._final_name.upper()}_H\n"
        output += f"#define {self._define_prefix.upper()}_{self._final_name.upper()}_H\n"
        output += "\n"
        output += "#include <include/AimiGTypes.h>\n"
        output += "\n"
        output += f"extern const {self._final_data_type} {self._final_name};\n"
        output += "\n"
        output += f"#endif  // {self._define_prefix.upper()}_{self._final_name.upper()}_H\n"
        return output

    def _fill_template_c_start(self) -> str:
        output = f"#include \"{self._final_name}.h\"\n"
        return output

    def _fill_template_c_image(self) -> str:
        output = "\n"
        output += f"const uint16_t {self._final_name}_image_data[{self._image_data_len}] = {{\n"
        output += self._image_data
        output += f"}};  // {self._final_name}_image_data\n"
        output += "\n"
        output += f"const AimiImageData {self._final_name}{self._image_name_suffix}={{{self._width}, {self._height}, {self._final_name}_image_data}};\n"
        return output

    def _fill_template_c_image_rle(self) -> str:
        output = "\n"
        output += f"const uint16_t {self._final_name}_image_data[{self._image_data_len}] = {{\n"
        output += self._image_data
        output += f"}};  // {self._final_name}_image_data\n"
        output += "\n"
        output += f"const uint8_t {self._final_name}_image_comp[{self._image_data_len}] = {{\n"
        output += self._image_comp
        output += f"}};  // {self._final_name}_image_comp\n"
        output += "\n"
        output += f"const AimiImageDataRLE {self._final_name}{self._image_name_suffix}={{{self._width}, {self._height}, {self._final_name}_image_data, {self._final_name}_image_comp}};\n"
        return output

    def _fill_template_c_mask(self) -> str:
        output = "\n"
        output += f"const uint8_t {self._final_name}_mask_data[{self._mask_data_len}] = {{\n"
        output += self._mask_data
        output += f"}};  // {self._final_name}_mask_data\n"
        output += "\n"
        output += f"const AimiMaskData {self._final_name}{self._mask_name_suffix}={{{self._width}, {self._height}, {self._mask_type}, {self._final_name}_mask_data}};\n"
        return output

    def _fill_template_c_mask_rle(self) -> str:
        output = "\n"
        output += f"const uint8_t {self._final_name}_mask_data[{self._mask_data_len}] = {{\n"
        output += self._mask_data
        output += f"}};  // {self._final_name}_mask_data\n"
        output += "\n"
        output += f"const uint8_t {self._final_name}_mask_comp[{self._mask_data_len}] = {{\n"
        output += self._mask_comp
        output += f"}};  // {self._final_name}_mask_comp\n"
        output += "\n"
        output += f"const AimiMaskDataRLE {self._final_name}{self._mask_name_suffix}={{{self._width}, {self._height}, {self._mask_type}, {self._final_name}_mask_data, {self._final_name}_mask_comp}};\n"
        return output

    def _fill_template_c_image_mask_wrapper(self) -> str:
        output = "\n"
        output += f"const {self._final_data_type} {self._final_name}={{&{self._final_name}{self._image_name_suffix}, &{self._final_name}{self._mask_name_suffix}}};\n"
        return output
