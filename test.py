#  test.py
#  Written by Matt Zola

from planspdf import PlansPDF
from csvmanager import CSVManager

import argparse


def main():
    parser = argparse.ArgumentParser()
    # Positional argument - Always need an input file
    parser.add_argument('input_file', help="Input PDF file name", type=str)

    # Optional arguments
    parser.add_argument(
        '-o', '--output', help="Output CSV file name", type=str)
    parser.add_argument(
        '-d', '--debug', help="Enable debug printing", action="store_true")
    parser.add_argument(
        '-p', '--pages', help="PDF page restriction [first,last]")

    args = parser.parse_args()

    input_name = args.input_file

    pdf = PlansPDF(input_name)

    if(args.debug):
        PlansPDF.debug = True
        CSVManager.debug = True

    if(args.pages):
        page_args = args.pages.split('-')
        dict_parsed = pdf.parse(page_args)
    else:
        dict_parsed = pdf.parse()

    if(args.output):
        output_name = args.output
        CSVManager.output_csv(dict_parsed, output_name)


if __name__ == '__main__':
    import sys
    sys.exit(main())
