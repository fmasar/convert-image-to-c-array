#!/usr/bin/python

import argparse
import os

from convert import convert
from enums import ConvTypes, AlphaTypes, RLETypes


def validate_file(file):
    if not os.path.exists(file):
        raise argparse.ArgumentTypeError("{0} file does not exist".format(file))
    return file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert image to C array file in RGB565 format.')
    try:
        parser.add_argument(
            '--input',
            dest='input',
            required=True,
            type=validate_file,
            help='Input image',
            metavar="FILE"
        )

        parser.add_argument('--output', dest='output', required=True, help='Output H/C file name')
        parser.add_argument('--path', dest='output_path', required=False, help='Output path')

        parser.add_argument(
            '--conv',
            dest='conv',
            required=False,
            help='Conversion type',
            type=ConvTypes,
            choices=list(ConvTypes)
        )

        parser.add_argument(
            '--alpha',
            dest='alpha',
            required=False,
            help='Alpha type',
            type=AlphaTypes,
            choices=list(AlphaTypes)
        )
        parser.add_argument(
            '--rle',
            dest='rle',
            required=False,
            help='RLE type',
            type=RLETypes,
            choices=list(RLETypes)
        )

    except:
        exit(1)

    args = parser.parse_args()

    if args.input is None and args.output is None:
        exit(1)

    if args.conv is None:
        conv_type = ConvTypes.IMAGE

    if args.alpha is None:
        alpha_type = AlphaTypes.BITS_8

    if args.rle is None:
        rle_type = RLETypes.OFF

    if args.output_path is not None:
        output_path = args.output_path
        if output_path[-1] != '/':
            output_path += '/'
        if not os.path.exists(output_path):
            print('Dir does not exist! Creating...')
            os.mkdir(output_path)
    else:
        output_path = 'out/'
        if not os.path.exists(output_path):
            os.mkdir(output_path)

    print(f"Convert type: \t{args.conv}")
    print(f"Alpha type: \t{args.alpha}")
    print(f"RLE type: \t{args.rle}")

    convert(args.input, args.output, output_path, args.conv, args.alpha, args.rle)
