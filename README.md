# plans-parser
Parses Van's RV-12 plans PDF's and outputs the text into a CSV file organized by Section, Page and Step numbers. 

The directory "/RV12_Plans" is not included in the repository, but in order for the test.py program to work,
the directory needs to be created and populated with the RV-12 plans PDF's.

Note: In order to properly display error messages on a Windows OS, it may be necessary to type the command "chcp 65001"
(this enables utf-8 encoding) into the command prompt before running "python test.py"