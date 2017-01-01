#  pdfparser.py 
#  Written by Matt Zola

import re
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

"""
Opens the inputted file, checks if it is a PDF, and outputs a list
of PDFPage objects from the PDF
"""
def split_to_pages(file_name):
    ### pdfminer methods/variables
    # Open a PDF file.
    input_file = open(file_name, 'rb')
    
    # Return the list of pages    
    return PDFPage.get_pages(input_file)

"""
Converts the inputted list of pages to a nested list of extracted text
for each page
"""
def page_to_text_list(pages, debug=False):
    ### pdfminer methods/variables
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    extracted_text_list = []
    
    for page in pages:
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
            extracted_text_list.append(extracted_text)
        elif debug:
            # Text could not be extracted
            print("ERROR: Could not extract pageid %s" % page.pageid )

    return extracted_text_list

"""
Converts inputted nested text list to dictionary of pages
Key: Page name (ex: 42-03)
Value: extracted text list

Needs to check for three Scenarios:
    "PAGE"
    "42-01"

    "PAGE\nPAGE"
    "42-01"
    
    "PAGE 42-01"
"""
def page_list_to_dict(extracted_text_list, debug=False):
    page_dict = {}
    
    for text_list in extracted_text_list:
        
        possible_hits = []
        
        for index, line in enumerate(text_list):
            
            # Various formatting on the plans pages produces different parsed text
            cleaned_line = line.replace('\n', '').replace(':', '').strip('RV-12').strip()
            
            if (cleaned_line == "PAGE") or (cleaned_line == "PAGEPAGE"):
                # If the line only reads "PAGE" or "PAGE\nPAGE", check the next line
                # for a valid page number
                possible_hits.append(index+1)
                
            # Use re module to search the string for the text "PAGE ##-##"
            page_num_search = re.search('PAGE[:]?\s?[0-9][0-9][A-Z]?-[0-9][0-9]', line.strip('\n'))
            
            # If the first search failed, check if the last line was "PAGE"
            if (not page_num_search) and (index in possible_hits):
                # Check if this line has a valid page number
                page_num_search = re.search('[0-9][0-9][A-Z]?-[0-9][0-9]', line.strip('\n'))

            # Check if either search was successful
            if page_num_search is not None:
                # Strip the text 'PAGE' and whitespace from start of the string
                page_num = page_num_search.group().lstrip('PAGE').lstrip()
                
                # Add the entire text list to the dict
                page_dict[page_num] = text_list
                
                # Stop the loop because we already found the page number
                break
        
        # Else occurs when the for loop finishes and does not reach a "break" statement
        # This means the page number was not found
        else:
            if debug:
                print("ERROR: Page number not found!")
                print(text_list)
                print("--------------------")

    return page_dict
