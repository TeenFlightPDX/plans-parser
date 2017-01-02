# plans-parser
Parses Van's RV-12 plans PDF's and outputs the text into a CSV file organized by Section, Page and Step numbers. 

Usage: This program runs off of command line arguments. Here are a few example use cases:
	python test.py [input pdf] -d				        # Parses the pdf and prints the data to the console
	python test.py [input pdf] -o [output csv] 	        # Parses the pdf and outptus the data to a csv file
	python test.py [input pdf] -o [output csv] -p 1,3	# Parses pages 1-3 of the pdf and outptus the data to a csv file
	
	
Note: In order to properly display error messages on a Windows OS, it may be necessary to type the command "chcp 65001"
(this enables utf-8 encoding) into the command prompt before running "python test.py"

Note: The parsing process is very processing intensive, it is normal for the program to take upwards of a minute for longer PDF files