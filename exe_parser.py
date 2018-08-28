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
import datetime as dt
from multiprocessing import Pool

# function exe_parser accepts 3 arguments: A source_file argument "source_dir" that is our large native ".exe" file, a destination file that we will save to, and a log path
# destinations must end with '/'!
def exe_parser(source_dir,dest_dir,log_var):
    
    # define total and done variables. Used to track progress in command line
    total = 0
    done = 0
    for file in os.listdir(source_dir):
        total +=1
    
    # creating log directory if it doesn't exist
    if os.path.isdir(log_var) != True:
                 os.mkdir(log_var)
    
    # c_log is .txt file of completed raw files. Completed files that are encountered again are skipped
    c_log = log_var + 'exe_parser_completed_log.txt'
    if os.path.isdir(dest_dir) != True:
        os.mkdir(dest_dir)
        c_list = []
    else:
        open(c_log,'a')
        c_list = [item[:len(item)-1] for item in open(c_log,'r')]
    
    # iterating through each raw file within the source directory
    for file in os.listdir(source_dir):
        
        # skipped if the file is in the c_list
        if file in c_list:
            print (file + ' already complete. Skipping')
            done += 1
        
        # otherwise the main program proceeds
        else:
            
            # last_line variable is an integer stored in a temp file that allows the program to pick up at the same spot if interuppted
            if os.path.isdir(dest_dir+'last_line.txt') == True:
                last_line = int(open(dest_dir+'last_line.txt','r').readline())
            else:
                last_line = 0
            
            # open raw file as a readable
            large_file = open(source_dir+file,'r')
            
            # create reference log of written xmls for the run
            log = open(log_var+'exe_parser_log.txt','w')
            
            # create filename and line_done variables. filename is used to write the xml to file. line_done is used in tandem with last_line to allow continuity
            filename = ''
            line_done = 0
            
            # iterate through the raw file
            for line in large_file:
                
                # last_line catch up if the line_done and last_line don't match
                if line_done != last_line:
                    line_done += 1
                
                # otherwise the else statement proceeds
                else:
                    
                    # checks if the line has a string that contains an element only found in court case xmls(a tag that says 'courtCaseDoc') and that the filename has been set. This ensures that the xml file doesn't get named for the filename above or below it.
                    if 'courtCaseDoc' in str(line) and filename != '':
                        
                        # create a save destination based on the filename variable and create it if it doesn't already exist. The xml file is written to the save destination
                        save_dest = dest_dir+filename+'/'
                        if os.path.isdir(save_dest) == False:
                            os.mkdir(save_dest)
                            open(save_dest+filename+'.xml','w').write(line)
                        
                        # if the save destination already exists, the filename is changed based on how many other xml files are present in the save destination. The xml file is written to the save_dest with a new name
                        else:
                            filename_iter = 0
                            for file in os.listdir(dest_dir+filename):
                                filename_iter += 1
                            filename = filename+'_'+str(filename_iter)
                            open(save_dest+filename+'.xml','w').write(line)
                        
                        # command line conformations and percent complete
                        print (filename+' written at: '+str(dt.datetime.now()))
                        total_percent = done/total*100
                        print ('total:'+str(total_percent)+'%'+'\n')
                        
                        # the last line is written to file
                        open (dest_dir+'last_line.txt','w').write(str(line_done))
                        
                        # the log is updated with the most recent xml written
                        log.write(filename+'\n')
                        
                        # the filename variable is reset
                        filename = ''
                    
                    # prepping the filename variable so that only the lexis-ID remains
                    elif 'Content-ID' in str(line):
                        filename = str(line)
                        filename = filename.replace('Content-ID: urn:contentItem:','')
                        filename = filename.replace('@lexisnexis.com','')
                        filename = filename.replace('\n','')
                   
                    # lines that don't contain the xml or the lexis ID are passed
                    else:
                        pass
                    
                    # last_line and line_done are updated every line
                    line_done += 1
                    last_line = line_done
            
            # when a file is completed the last_line.txt file is deleted
            os.remove(dest_dir+'last_line.txt')
            
            # raw filename written to the completion log
            open(c_log,'a').write(str(file)+'\n')
            
            # files done is updated
            done += 1


s = 'raw/'
d = 'case_files/'
l = 'xml-database/logs/'

# pool = Pool()
# try:
#     pool.apply(exe_parser(s,d,l))
# except TypeError:
#     print ('complete')

