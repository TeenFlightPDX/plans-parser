#  csvmanager.py
#  Written by Matt Zola

import csv


class CSVManager:
    debug = False

    """
    This method writes the inputted dictionary to the inputted csv file name
    """
    @staticmethod
    def output_csv(page_dict_parsed, output_file_name):

        # Opens the output file in append mode
        output_file = open(output_file_name, 'a+')

        # Initializes the writer set to separate items with a comma (",")
        writer = csv.writer(output_file, delimiter=',')

        # Checks if the csv file is new
        import os
        is_new_file = os.stat(os.path.realpath(output_file.name)).st_size == 0

        # Only write the header if the file is new
        if is_new_file:
            writer.writerow(['page', 'step', 'text'])

        for page_number in sorted(page_dict_parsed):
            for step_number in sorted(page_dict_parsed[page_number]):
                text_list = page_dict_parsed[page_number][step_number]

                # Contracts the list of textboxes to one str with two new lines
                # b/w each box
                text = '\n\n'.join(text_list).strip()
                data = [page_number, step_number, text]
                writer.writerow(data)

        if CSVManager.debug:
            print("Done outputting to CSV file")

        output_file.close()
        return
