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
    This method starts the parsing algorithm from start to finish.
    Returns a dictionary:
        Key = str - Page number (ex. 42A-16)
        Value = Dictionary:
                    Key = str - Step number (ex. 1)
                    Value = list - Text
    """

    def parse(self, page_range=None):
        ###
        # Split to PDFPage objects
        ###

        # Convert the inputted file name to a file object
        input_file = open(self.file_name, 'rb')

        if page_range:
            if len(page_range) is 1:
                # Indexing is weird, subtract one
                pages_to_parse = [int(page_range[0]) - 1]

                # Extract pdfminer PDFPage objects from the pdf file
                unparsed_pages = PDFPage.get_pages(input_file, pages_to_parse)
            elif len(page_range) is 2:
                start = int(page_range[0])
                end = int(page_range[1])

                # Subtract one to both values because range is weird
                # Range doesn't include the end number, so add 1 to end
                pages_to_parse = range(start - 1, end)

                # Extract pdfminer PDFPage objects from the pdf file
                unparsed_pages = PDFPage.get_pages(input_file, pages_to_parse)
            else:
                # If input was invalid, ignore and parse all
                unparsed_pages = PDFPage.get_pages(input_file)
        else:
            unparsed_pages = PDFPage.get_pages(input_file)

        # ------------------------------------------------------- #
        ###
        # Extract text-list from each PDFPage object
        ###

        # pdfminer methods/variables
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Parsed text from the pdf
        # This is a nested list consisting of a list of str objects for eachE
        # parsed page
        parsed_pages = []

        for page in unparsed_pages:
            extracted_text = []

            # Parses the page and saves it in device.get_result()
            interpreter.process_page(page)

            # The device renders the layout from the interpreter
            layout = device.get_result()

            # The layout consists of many LT objects (Text, Image, etc)
            for lt_obj in layout:
                # Only get text if the object is a TextBox or TextLine
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    extracted_text.append(lt_obj.get_text())

            if extracted_text:
                # Save extracted text t
                parsed_pages.append(extracted_text)
            elif PlansPDF.debug:
                # Text could not be extracted
                print("ERROR: Could not extract pageid %s" % page.pageid)

        # We no longer need the unparsed_pages list
        unparsed_pages = None
        # ------------------------------------------------------- #
        ###
        # Parse the page number from each page in the nested page list
        ###

        page_dict_raw = {}

        for text_list in parsed_pages:

            possible_hits = []

            for index, line in enumerate(text_list):

                # Various formatting on the plans pages produces differentm
                # parsed text
                cleaned_line = line.replace('\n', '').replace(
                    ':', '').strip('RV-12').strip()

                if (cleaned_line == "PAGE") or (cleaned_line == "PAGEPAGE") or (cleaned_line == "PAGEPAGEPAGE"):
                    # If the line only reads "PAGE" or "PAGE\nPAGE", check the
                    # next line for a valid page number
                    possible_hits.append(index + 1)

                # Use re module to search the string for the text "PAGE ##-##"
                page_num_search = re.search(
                    'PAGE[:]?\s?[0-9]?[0-9][A-Z]?-[0-9][0-9]', line.strip('\n'))

                # If the first search failed, check if the last line was "PAGE"
                if (not page_num_search) and (index in possible_hits):
                    # Check if this line has a valid page number
                    page_num_search = re.search(
                        '[0-9]?[0-9][A-Z]?-[0-9][0-9]', line.strip('\n'))

                # Check if either search was successful
                if page_num_search is not None:
                    # Strip the text 'PAGE' and whitespace from start of the
                    # string
                    page_num = page_num_search.group().lstrip('PAGE').lstrip()

                    # Add the entire text list to the dict
                    page_dict_raw[page_num] = text_list

                    # Stop the loop because we already found the page number
                    break

            # Else occurs when the for loop finishes and does not reach a "break" statement
            # This means the page number was not found
            else:
                if PlansPDF.debug:
                    print("ERROR: Page number not found!")
                    print(text_list)
                    print("--------------------")

        # Debug - loop through and print out the dict with page numbers
        if PlansPDF.result_print:
            for page_num in sorted(page_dict_raw):
                print("--------------------")
                print("Page: %s" % page_num)
                print("Text: %s" % page_dict_raw[page_num])

        # -------------------------------------------------------#
        ###
        # Parse each list of lines for section and step numbers
        ###

        # Dict for parsed pages (Key= Page #, Value= dict of steps
        page_dict_parsed = {}

        # Loops through each page in the dict
        for page_num, text_list in sorted(page_dict_raw.items()):

            # Dict for parsed steps (Key= Step #, Value= list of step text)
            steps_dict = {}

            # The last step is stored as a tuple of a step number and list of
            # text
            last_step = None

            # No steps on the first page
            if (not page_num.endswith('-01') or not page_num.endswith('-1')):
                for text in text_list:

                    # Don't add text that is all uppercase (Figures are upper
                    # only)
                    if not text.isupper():

                        # Check if the line starts with Step:
                        step_search = re.search('^Step [0-9][0-9]?: ', text)

                        # Remove newline characters from original formatting
                        text = text.replace('\n', ' ')

                        if step_search:
                            # Remove the text 'Step ' and ':' from the step number
                            # Only replace the first occurance of the str "Step
                            # "
                            step_number = step_search.group().replace('Step ', '', 1).rstrip().rstrip(':')

                            # Remove the str "Step ##: " from the step_text
                            step_text = text.replace(
                                step_search.group(), '', 1)

                            # If there was a previous step, save it and make a
                            # new one
                            if last_step:
                                last_step_number = last_step[0]
                                last_step_text = last_step[1]

                                # Add the step to the dict
                                steps_dict[last_step_number] = last_step_text

                                last_step = None

                            # Store this step's text inside a tuple
                            last_step = (step_number, [step_text])

                        # If the last_step object isn't None, then add the text
                        # to the last step
                        elif last_step:
                            last_step_number = last_step[0]
                            last_step_text = last_step[1]

                            # Add this line to the text list
                            last_step_text.append(text)

                            # Replace last_step
                            last_step = (last_step_number, last_step_text)

                    # If the text IS upper and there was a last_step, save the
                    # last step and clear it
                    elif last_step:
                        last_step_number = last_step[0]
                        last_step_text = last_step[1]

                        # Add the step to the dict
                        steps_dict[last_step_number] = last_step_text

                        last_step = None

            # Add the parsed steps_dict to the dict of parsed pages
            page_dict_parsed[page_num] = steps_dict

        # Debug - loop through and print out the dict with page numbers
        if PlansPDF.result_print:
            for page_number in sorted(page_dict_parsed):
                print("XXXXXXXXXXXXXXXXXXXXXX")
                print("Page: %s" % page_number)

                for step_number in sorted(page_dict_parsed[page_number]):
                    print("    --------------------")
                    print("    Step: %s" % step_number)
                    print("    Text: %s" %
                          str(page_dict_parsed[page_number][step_number]))

        # Make sure the input PDF file is closed
        input_file.close()

        # Return the final page_dict_parsed
        return page_dict_parsed
