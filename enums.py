from enum import Enum


class AlphaTypes(Enum):
    ALPHA_NONE = 0
    ALPHA_8BITS = 1
    ALPHA_4BITS = 2
    ALPHA_2BITS = 3
    ALPHA_1BIT = 4


class RLETypes(Enum):
    RLE_OFF = 0
    RLE_IMAGE = 1
    RLE_MASK = 2
    RLE_BOTH = 3
