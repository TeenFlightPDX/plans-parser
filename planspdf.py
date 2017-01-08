#  planspdf.py
#  Written by Matt Zola

import re
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine


class PlansPDF:
    debug = False
    result_print = False

    def __init__(self, file_name):
        self.file_name = file_name

    """
    Fully parses the PDF file inputted in the constructor
    """

    def parse(self, page_range=None):
        with open(self.file_name, 'rb') as input_file:
            unparsed_pages = self.convert_pages(input_file, page_range)
            parsed_pages = self.parse_pages(unparsed_pages)
            page_dict_raw = self.extract_page_numbers(parsed_pages)
            page_dict_parsed = self.extract_steps(page_dict_raw)

            return page_dict_parsed

    """
    Converts the inputed file into PDFPage objects via the pdfminer.six library
    """

    def convert_pages(self, input_file, page_range):
        if page_range:
            if len(page_range) is 1:
                # Quirk in page indexing, need to -1
                pages_to_parse = [int(page_range[0]) - 1]
            elif len(page_range) is 2:
                start = int(page_range[0])
                end = int(page_range[1])
                # Quirk in page indexing, need to -1
                pages_to_parse = range(start - 1, end)
            else:
                return PDFPage.get_pages(input_file)
            return PDFPage.get_pages(input_file, pages_to_parse)
        else:
            return PDFPage.get_pages(input_file)

    """
    Parses text from list of unparsed pages and returns nested list of pages with text strings
    """

    def parse_pages(self, unparsed_pages):
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Nested list consisting lists of str objects for each page
        parsed_pages = []

        for unparsed_page in unparsed_pages:
            extracted_text = []

            interpreter.process_page(unparsed_page)
            layout = device.get_result()

            for lt_obj in layout:
                # Only extract text from TextBoxes or TextLines
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    extracted_text.append(lt_obj.get_text())

            if extracted_text:
                parsed_pages.append(extracted_text)
            elif PlansPDF.debug:
                print("ERROR: Could not extract pageid %s" %
                      unparsed_page.pageid)

        return parsed_pages

    """
    Extract the page number from the list string objects on each page
    """

    def extract_page_numbers(self, parsed_pages):
        # Nested dict containing key for each page and value of extracted pages
        page_dict_raw = {}

        for text_list in parsed_pages:

            possible_hits = []

            for index, line in enumerate(text_list):

                # Clean blank space, Van's logo from the text
                cleaned_line = line.replace('\n', '').replace(
                    ':', '').strip('RV-12').strip()

                valid_precursors = ["PAGE", "PAGEPAGE", "PAGEPAGEPAGE"]
                if cleaned_line in valid_precursors:
                    # Check the next line for a valid page number
                    possible_hits.append(index + 1)

                page_num_search = re.search(
                    'PAGE[:]?\s?[0-9]?[0-9][A-Z]?-[0-9][0-9]', line.strip('\n'))

                # If the first search failed, check if the last line was "PAGE"
                if (not page_num_search) and (index in possible_hits):
                    page_num_search = re.search(
                        '[0-9]?[0-9][A-Z]?-[0-9][0-9]', line.strip('\n'))

                # Check if either search was successful
                if page_num_search is not None:
                    page_num = page_num_search.group().lstrip('PAGE').lstrip()
                    page_dict_raw[page_num] = text_list
                    break
            else:
                if PlansPDF.debug:
                    print("ERROR: Page number not found!")
                    print(text_list)
                    print("--------------------")

        return page_dict_raw

    """
    Extracts steps from the list of text on each page and assembles final dict
    """

    def extract_steps(self, page_dict_raw):
        # Dict for parsed pages (Key= Page #, Value= dict of steps)
        page_dict_parsed = {}

        for page_num, text_list in sorted(page_dict_raw.items()):

            # Dict for parsed steps (Key= Step #, Value= list of step text)
            steps_dict = {}

            # Tuple: (step # , [step text])
            last_step = None

            # No steps on the first page
            if (not page_num.endswith('-01') or not page_num.endswith('-1')):
                for text in text_list:

                    # Ignore figures (all uppercase)
                    if not text.isupper():

                        step_search = re.search('^Step [0-9][0-9]?: ', text)
                        text = text.replace('\n', ' ')

                        if step_search:
                            found_step = step_search.group()

                            step_number = found_step.replace(
                                'Step ', '', 1).rstrip().rstrip(':')

                            # Remove the str "Step ##: " from the step_text
                            step_text = text.replace(found_step, '', 1)

                            # Save and replace previous step
                            if last_step:
                                last_step_number = last_step[0]
                                last_step_text = last_step[1]

                                steps_dict[last_step_number] = last_step_text

                                last_step = None

                            last_step = (step_number, [step_text])

                        # Append text to previous step
                        elif last_step:
                            last_step_number = last_step[0]
                            last_step_text = last_step[1]

                            last_step_text.append(text)

                            # Update last_step
                            last_step = (last_step_number, last_step_text)

                    # Once  a figure is reached, save the last step
                    elif last_step:
                        last_step_number = last_step[0]
                        last_step_text = last_step[1]

                        steps_dict[last_step_number] = last_step_text

                        last_step = None

            # Add the parsed steps_dict to the dict of parsed pages
            page_dict_parsed[page_num] = steps_dict

        if PlansPDF.result_print:
            for page_number in sorted(page_dict_parsed):
                print("XXXXXXXXXXXXXXXXXXXXXX")
                print("Page: %s" % page_number)

                for step_number in sorted(page_dict_parsed[page_number]):
                    text = str(page_dict_parsed[page_number][step_number])
                    print("    --------------------")
                    print("    Step: %s" % step_number)
                    print("    Text: %s" % text)

        return page_dict_parsed
