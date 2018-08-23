'''

This script uses the lxml library to parse a directory of folders containing .xml files with similar names and content.

This is accomplished in the following steps:

1. Determining which of the files, if any, have publicationstatus="full" attribute, hereby referred to as the "primary" file
2. Saving the primary file as the base for a new master file that will contain all the disparate subelements, hereby referred to as the "uberfile"
3. To iterate through the rest of the files and find the necessary subelements, and  then writing them to the uberfile at the proper hierarchy position*

*step 3 is done with the help of the index_insert function found in index_insert.py

To decrease runtime, the program uses exclusion tags. These are the tags of missing elements that appeared during the preliminary runs of this program when it ran every element in the source_file against every element in the dest_file. Now only the elements with the exclusion tags will be compared. In order to improve the exclusion list, 1 in every n tags is let in randomly to see if it is a missing tag. If the element is indeed missing from the dest_file it is added to the exclusion list as a new tag.
'''

from lxml import etree as et
import os
from random import randint
import datetime as dt
from index_inserter import index_inserter
import multiprocessing as mp

# all paths that don't end in a file must end with '/'!

# uber_maker function accepts 3 arguments: a source directory s_dir, and destination directory "d_dir", and a exclusion file destination "e_file"

def uber_maker(s_dir,d_dir,e_file):
    
    # make destination file if it doesn't already exist
    os.mkdir(d_dir) if os.path.isdir(d_dir) != True else print('Uber destination: '+d_dir)
    
    # exclusions list created from elements in the exclusion file. len(line)-1 is used to avoid copying the '\n' character at the end of each tag
    e_list = [line[:len(line)-1] for line in open(e_file,'r')]
    
    # a file of completed ubers is kept to avoid duplicates during reruns. opened as an appenable file
    c_log = d_dir+'completed.txt'
    
    # a list of completed files is created to compare below
    c_list = [line[:len(line)-1] for line in open(c_log, 'r')]
    
    # a log file is created in the destination directory and named using datetime library for unique filenames
    # log is encoded in utf-8, because certain characters (e.g. the section symbol) will throw a >128 ordinal range error if they are not encoded
    os.mkdir(d_dir+'outputlogs') if os.path.isdir(d_dir+'outputlogs') != True else print('Log destination: '+d_dir+'outputlogs')
    log=open(d_dir+'outputlogs/'+str(dt.datetime.now())+'output.txt',"a",encoding='utf-8')
    
    # iteration through every file in the source directory
    for file in os.listdir(s_dir):
        
        # check to see if file is in the completed list, skipping if it is
        if file in c_list:
            print (file+" is in completed list. Skipped...")
        
        # else loop containing main body of function
        else:
            
            # creating a temporary file where non-primary files will be sent during the comparison portion of the code
            if os.path.isdir(d_dir+'temp') != True:
                os.mkdir(d_dir+'temp')
            
            # if the temp file isn't empty this loop removes all the files so it can start fresh
            else:
                for tmp in os.listdir(d_dir+'temp'):
                    os.remove(d_dir+'temp'+'/'+tmp)
           
            # for loop for finding the primary file among the .xml files in the "file"
            for xml in os.listdir(s_dir+file):
                
                #  lxml call to create root and tree
                tree = et.parse(s_dir+file+'/'+xml)
                root = tree.getroot()
                
                # if the xml has the status="full" tag it is the primary
                if et.iselement(root.find('.//*[@status="full"]')) == True or len(os.listdir(s_dir+file))==1:
                    
                    # is written to the destination directory
                    uber_xml = 'uber' + file +'.xml'
                    tree.write(d_dir+uber_xml)
                    
                    # and the uber_root is made
                    uber_tree = et.parse(d_dir+uber_xml)
                    uber_root = uber_tree.getroot()
                    
                # non-uberfiles written to temp file
                else:
                    tree.write(d_dir+'temp'+'/'+xml)
                    
            # create uber_list from uber_root
            uber_list = []
            for el in uber_root.iter():
                
                # uber_list is the list of all elements in the uber_file that have tags matching those in the exclusion list
                # if the exclusion list is empty all tags from the uber_file are added and then filtered in the next block
                if el.tag in e_list or e_list == []:
                    
                    # attributes of the element are unique enough to be a good comparison
                    uber_list.append(el.attrib)
                
                # tags are randomly let in to improve the pool of exclusion tags
                elif randint(1,10) == 10:
                    uber_list.append(el.attrib)
                
                # tags that aren't accepted are passed
                else:
                    pass
            
            # copy missing elements from source file in the temp folder to uber_file
            for xml in os.listdir(d_dir+'temp'):
                
                # add '#' break to log to improve readability
                log.write("#\n"*5)
                
                # add header of source and destination to log
                log.write(xml+' to '+uber_xml)
                
                # create source root from xml
                source_root = et.parse(d_dir+'temp'+'/'+xml).getroot()
                
                # parse through source_file iterable and use index insert function
                for el in source_root.iter():
                    
                    # only elements with tags in the exclusion list are allowed through or if the exclusion list is empty
                    if el.tag in e_list or e_list == []:
                        
                        # elements with attributes matching those found in the uber_list are removed
                        if el.attrib in uber_list:
                            print (el.tag + " already in uber_list. Skipping...")
                        
                        # these elements are missing from the destination uber
                        else:
                            
                            # element inserted into the proper hierarchy using index_insert function
                            index_inserter(el,uber_tree,d_dir+uber_xml,uber_xml,log)
                            
                            # element attributes are added to the uber_list to avoid duplicates
                            uber_list.append(el.attrib)
                            
                            # if the element tag isn't in the exclusion list it is added as a new line
                            if str(el.tag) not in e_list:
                                open(e_file,"a").write(str(el.tag)+"\n")
                            else:
                                pass
                    else:
                        pass
                
                # the xml is removed from the temp file
                os.remove(d_dir+'temp'+'/'+xml)
                
            ##when file completed write to c_file##
            open(c_log,'a').write(file+"\n")
            
            ##delete temp file##
            os.rmdir(d_dir+'temp')
            
##test###

s = 'case_files/'
d = 'uberfiles/'
e = 'xml-database/logs/exclusions.txt'

uber_maker(s,d,e)

# pool = mp.Pool()

# results = pool.apply_async(uber_maker(s,d,e))
# results.get(timeout=1)
