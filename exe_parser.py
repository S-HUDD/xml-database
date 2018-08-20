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

# function exe_parser accepts 3 arguments: A source_file argument "file_dir" that is our large native ".exe" file, a destination file that we will save to, and a log path
# destinations must end with '/'!
def exe_parser(file_dir,dest_dir,log_var,dir_done,dir_total):
    if os.path.isdir(dest_dir+'last_line.txt') == True:
        last_line = int(open(dest_dir+'last_line.txt','r').readline())
    else:
        last_line = 0
    os.mkdir(dest_dir) if os.path.isdir(dest_dir) != True else print(dest_dir)
    if os.path.isdir(log_var) != True:
         os.mkdir(log_var)
    large_file = open(file_dir,'r')
    log = open(log_var+'exe_parser_log.txt','a')
    filename = ''
    line_done = 0
    for line in large_file:
        if line_done != last_line:
            line_done += 1
        else:
            if 'courtCaseDoc' in str(line) and filename != '':
                save_dest = dest_dir+filename+'/'
                if os.path.isdir(save_dest) == False:
                    os.mkdir(save_dest)
                    open(save_dest+filename+'.xml','w').write(line)
                else:
                    filename_iter = 0
                    for file in os.listdir(dest_dir+filename):
                        filename_iter += 1
                    filename = filename+'_'+str(filename_iter)
                    open(save_dest+filename+'.xml','w').write(line)
                print (filename+' written at: '+str(dt.datetime.now()))
                total_percent = dir_done/dir_total*100
                print ('total:'+str(total_percent)+'%'+'\n')
                open (dest_dir+'last_line.txt','w').write(str(line_done))
                
                log.write(filename+'\n')
                    
                filename = ''
              
            elif 'Content-ID' in str(line):
                filename = str(line)
              
                filename = filename.replace('Content-ID: urn:contentItem:','')
                filename = filename.replace('@lexisnexis.com','')
                filename = filename.replace('\n','')
                
              
            else:
                pass
            line_done += 1
            last_line = line_done


def file_crack(s,d,l):
    total = 0
    done = 0
    for file in os.listdir(s):
        total +=1
    if os.path.isdir(d) != True:
        os.mkdir(d)
        c_log = open(d+'completed_log.txt','a')
        c_list = []
    else:
        c_log = open(d+'completed_log.txt','r')
        c_list = [item[:len(item)-1] for item in c_log]
    for file in os.listdir(s):
        if file in c_list:
            print (file + ' already complete. Skipping')
            done += 1
        elif os.path.getsize(s+file) >= 500000000:
            open(d+'too_big.txt', 'a').write(str(file)+'\n')
            print(str(file)+' IS TOO BIG \n'*100)
            done += 1
        else:
            print(str(file))
            exe_parser(s+file,d,l,done,total)
            open(d+'completed_log.txt','a').write(str(file)+'\n')
            done += 1

so = 'media/removable/HuddartHD/Supreme_Court_Data/'
de = 'media/removable/HuddartHD/case_files/'
lo = 'media/removable/HuddartHD/logs/'

pool = Pool()
# result =
pool.apply(file_crack(so,de,lo))
# result.get(timeout=1)
