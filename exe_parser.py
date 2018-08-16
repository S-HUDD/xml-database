'''
script to parse through the large ".exe" files that were originally downloaded from the lexisnexis database. Script will parse through a single file attempting to find the lexis id and the following line containing the xml text, saving them to a directory of files with the same name.
'''


import os

def exe_parser(file_dir,dest_dir):
    ##create destination file if it doesn't already exist
    if os.path.isdir(dest_dir) != True:
        os.mkdir(dest_dir)
    large_file = open(file_dir,'r')
    log = open('logs/'+'exe_parser_log.txt','a')
    line_iter = 0
    filename = ''
    for line in large_file:
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
            print (filename+' written to: '+dest_dir+filename)
            log.write(filename+'\n')
            filename = ''
            line_iter +=1
        elif 'Content-ID' in str(line):
            filename = str(line)
            filename = filename.replace('Content-ID: urn:contentItem:','')
            filename = filename.replace('@lexisnexis.com','')
            print(filename)
            line_iter +=1
        else:
            filename=filename
            line_iter +=1
    print (line_iter)

test_dir = 'test_exe_files/'
# test_file = '735dc2ac-599b-4f8b-9bc6-1df234c4e4a6'
test_dest = 'case_files/'
# exe_parser(test_dir+test_file,test_dir+test_dest)

for file in os.listdir(test_dir):
    exe_parser(test_dir+file,test_dest)


# --yytet00pubSubBoundary00tetyy
# Content-ID: urn:contentItem:3RJ6-FCK0-003B-R0KR-00000-00@lexisnexis.com
# Content-Type: application/vnd.courtcasedoc-newlexis+xml
# Content-Length: 78755

# <?xml version="1.0" encoding="UTF-8"?><!--Transformation version 1.1--><courtCaseDoc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.lexisnexis.com/xmlschemas/content/public/courtcasedoc/1/" schemaVersion="1.0"><courtCaseDocHead><caseInfo><caseName><fullCaseName/><shortCaseName>Feist Publ'ns, Inc. v. Rural Tel. Serv. C