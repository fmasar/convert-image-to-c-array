import pytest
from os import path

from convert import convert
from enums import ConvTypes, AlphaTypes, RLETypes

_REGENERATE_TESTS = False
_TEST_DATA = "data"
_TEST_INPUT_PATH = path.join(_TEST_DATA, "input")
_TEST_OUTPUT_PATH = path.join(_TEST_DATA, "output")


@pytest.mark.parametrize("input_image", ["girl_blond.png", "girl_brunet.png"])
def test_both_8bits(input_image: str) -> None:
    _suffix = "both_8bits_rle_off"
    input_name = input_image.split('.')[0]
    output_h, output_c = convert(
        path.join(_TEST_INPUT_PATH, input_image),
        input_name,
        ConvTypes.BOTH,
        AlphaTypes.BITS_8,
        RLETypes.OFF
    )

    utils_compare_file(output_h, f"{input_name}_{_suffix}.h")
    utils_compare_file(output_c, f"{input_name}_{_suffix}.c")


def utils_compare_file(input_text: str, file_name: str) -> None:
    file_path = path.join(_TEST_OUTPUT_PATH, file_name)
    if _REGENERATE_TESTS:
        file = open(file_path, "w")
        file.write(input_text)
    else:
        assert input_text == open(file_path).read(), "Files does not match!"
