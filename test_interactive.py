#  test_interactive.py
#  Written by Matt Zola

from planspdf import PlansPDF
from csvmanager import CSVManager


def main():

    # Interactive console prompts
    print("Welcome to the Teen Flight Plans PDF Parser!")
    print("--------------------------------------------")
    print("Settings:")

    input_name = input(
        "------> What is the path of the PDF file you would like to parse? \n\t")

    pages = input(
        "------> What page/page range would you like to parse (type range A-B or press enter for all pages)? \n\t")

    output_name = input(
        "------> Would you like to output to a CSV? If yes, what is the path? If no, press enter. \n\t")

    debug_input = input(
        "------> Would you like the errors printed to the console? \n\t")

    results_print = input(
        "------> Would you like the results printed to the console? \n\t")

    print("--------------------------------------------")

    print("Thanks for your input, your file will begin parsing now.")

    # Start the parsing
    pdf = PlansPDF(input_name)

    if debug_input.lower().strip() == "yes":
        PlansPDF.debug = True
        CSVManager.debug = True

    if results_print.lower().strip() == "yes":
        PlansPDF.result_print = True

    if(pages):
        page_args = pages.split('-')
        dict_parsed = pdf.parse(page_args)
    else:
        dict_parsed = pdf.parse()

    if(output_name):
        CSVManager.output_csv(dict_parsed, output_name)


if __name__ == '__main__':
    import sys
    sys.exit(main())
