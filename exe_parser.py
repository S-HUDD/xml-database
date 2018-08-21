'''
exe_parser.py is an iterative script to parse through the large native ".exe" files. The script will parse through a single large_file attempting to find the line with the lexis ID saving it as the variable "filename" it will then proceed through the lines until it finds a line containing an xml string. Lexis keeps each updated version of the file, so there will be almost exact copies of a case file with very minor differences. Each of these copies will be placed in a folder named after the lexis ID and the entire xml string is written to a .xml file with the name "filename.xml" or "filename_n.xml", where n is the number of files that are already in the filename directory.

e.g. string with the ID "ABC" is placed in a folder with the same name where there are already 3 "ABC" xml files

1. string named ABC to folder ABC:
>ABC
	>ABC.xml
	>ABC_1.xml
	>ABC_2.xml
2. string ABC becomes ABC_3.xml
3. folder ABC becomes:
>ABC
	>ABC.xml
	>ABC_1.xml
	>ABC_2.xml
	>ABC_3.xml

Example of the header and a truncated xml lines:

	1 --yytet00pubSubBoundary00tetyy
	2 Content-ID: urn:contentItem:3RJ6-FCK0-003B-R0KR-00000-00@lexisnexis.com
	3 Content-Type: application/vnd.courtcasedoc-newlexis+xml
	4 Content-Length: 78755

	5 <?xml version="1.0" encoding="UTF-8"?><!--Transformation version 1.1--><courtCaseDoc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.lexisnexis.com/xmlschemas/content/public/courtcasedoc/1/" schemaVersion="1.0"><courtCaseDocHead><caseInfo><caseName><fullCaseName/><shortCaseName>Feist Publ'ns, Inc. v. Rural Tel. Serv. C ... </courtCaseDoc>

The portion of line 2 named "3RJ6-FCK0-003B-R0KR-00000-00" is what will become the filename variable.
The program searches for 'courtCaseDoc' within the string to determine whether a line is an xml or not.

'''


import os

# function exe_parser accepts 2 arguments: A source_file argument "file_dir" that is our large native ".exe" file. And a destination file that we will save to
# destinations must end with '/'!
def exe_parser(file_dir,dest_dir):  
	
	# create destination file if it doesn't already exist    
	if os.path.isdir(dest_dir) != True:    
		os.mkdir(dest_dir) 
		
	# open our large file as readable 
	large_file = open(file_dir,'r')
	
	# open our log file to the log directory as appendable
	log = open('logs/'+'exe_parser_log.txt','a')
	
	# set the filename variable to '' before we begin the loop
	filename = ''
	
	# the for loop iterates through each line of the large_file and either: 1. saves the file to dest_dir, 1. finds the filename line and creates the filename variable, or 3. else statement if neither of the two lines are encountered, retaining the filename variable
	for line in large_file:
		
		# if statement that checks if line is the xml string and that it has a useable filename variable
        if 'courtCaseDoc' in str(line) and filename != '':
			
			# preparing a save destination variable save_dest
            save_dest = dest_dir+filename+'/'
			
			# if loop to check if save_dest exists
            if os.path.isdir(save_dest) == False:
                os.mkdir(save_dest)
				
				# since this file is the first to be saved to the new dirctory, it is not given a numbered suffix
                open(save_dest+filename+'.xml','w').write(line)
				
             #else statement for if the filename directory already exists
			else:
				
				# creating a file iteration variable and using it to count how many files are already in the directory with a for loop
                filename_iter = 0
                for file in os.listdir(dest_dir+filename):
                    filename_iter += 1
					
				# saving the filename with the suffix being equal to filename_iter
                filename = filename+'_'+str(filename_iter)
                open(save_dest+filename+'.xml','w').write(line)
				
			# print statement to command line for progress and debugging
            print (filename+' written to: '+dest_dir+filename)
			
			# write our filename to our log
            log.write(filename+'\n')
            
			# rename our log file to '' to prep for the next header
			filename = ''
			
        # elif that creates the filename variable if the substring 'Content-ID is found in the line string
		elif 'Content-ID' in str(line):
			
			# filename first equals the whole line
            filename = str(line)
			
			# the preceding part before the lexis guid is removed
            filename = filename.replace('Content-ID: urn:contentItem:','')
			
			#then the following portion, leaving just the guid 
            filename = filename.replace('@lexisnexis.com','')
			
			# print statement to command line for progress and debugging
            print(filename)
        
		# else statement for when the line is not the guid or the xml string, preserves the filename variable
		else:
            filename=filename

# test_dir = 'test_exe_files/'
# test_file = '735dc2ac-599b-4f8b-9bc6-1df234c4e4a6'
# test_dest = 'case_files/'
# exe_parser(test_dir+test_file,test_dir+test_dest)

# for file in os.listdir(test_dir):
    # exe_parser(test_dir+file,test_dest)
