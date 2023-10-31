#!/usr/bin/python

import argparse
import os
from enums import AlphaTypes
from convert import convert


def validate_file(file):
    if not os.path.exists(file):
        raise argparse.ArgumentTypeError("{0} file does not exist".format(file))
    return file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert image to C array file in RGB565 format.')
    try:
        parser.add_argument('--input', dest='input', required=True, type=validate_file, help='Input image',
                            metavar="FILE")

        parser.add_argument('--output', dest='output', required=True, help='Output C header file', metavar="FILE")

        parser.add_argument('--path', dest='output_path', required=False, help='Output path', metavar="FILE")

        parser.add_argument('--alpha', dest='alpha', required=False, help='Alpha type', metavar="FILE")
    except:
        exit(1)

    args = parser.parse_args()

    if args.input is None and args.output is None:
        exit(1)

    if args.alpha is None:
        alpha_type = AlphaTypes.ALPHA_NONE
    else:
        alpha_type = AlphaTypes(int(args.alpha))

    if args.output_path is not None:
        output_path = args.output_path
        if output_path[-1] != '/':
            output_path += '/'
        if not os.path.exists(output_path):
            print('Dir does not exists! Creating...')
            os.mkdir(output_path)
    else:
        output_path = 'out/'
        if not os.path.exists(output_path):
            os.mkdir(output_path)

    convert(args.input, args.output, output_path, alpha_type)
