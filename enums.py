from enum import Enum


class ConvTypes(Enum):
    BOTH = "BOTH"
    IMAGE = "IMAGE"
    MASK = "MASK"

    def __str__(self):
        return self.value


class AlphaTypes(Enum):
    BITS_8 = "BITS_8"
    BITS_4 = "BITS_4"
    BITS_2 = "BITS_2"
    BITS_1 = "BITS_1"

    def __str__(self):
        return self.value


class RLETypes(Enum):
    OFF = "OFF"
    IMAGE = "IMAGE"
    MASK = "MASK"
    BOTH = "BOTH"

    def __str__(self):
        return self.value
