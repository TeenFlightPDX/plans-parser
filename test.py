#  test.py 
#  Written by Matt Zola

import pdfparser

def main(args):
    pages = pdfparser.split_to_pages('RV12_Plans/12 Section 42 Avionics.pdf')    
    text_list = pdfparser.page_to_text_list(pages, debug=False)
    page_dict = pdfparser.page_list_to_dict(text_list, debug=False)
    
    # Debug - loop through and print out the dict
    for page_num in sorted(page_dict):
        print("--------------------")
        print("Page: %s" % page_num)
        # print("Text: %s" % page_dict[page_num])

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

    
