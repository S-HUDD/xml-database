'''
This is a simple script that incorporates the xml_class to make a dataframe.
1. The function accepts a directory that contains 1 or more uber_files
2. Each file is converted into an xml_class object
3. Each file is imported into a dataframe of uberfiles where each row is a case and the columns are the xml_class attributes
4. The dataframe is exported to .csv when complete
'''

from lxml import etree as et
import pandas as pd
import numpy as np
import os
from xml_class import xml_class
import multiprocessing as mp
import datetime as dt

# dataframe_maker accepts a directory of uberfiles
def dataframe_maker(uber_directory,db_dir,log_var):
    
    # count files
    done = 0
    total = 0
    for file in os.listdir(uber_directory):
        total += 1
    
    # create the dataframe that will accept xml_class attributes
    uber_dataframe = pd.DataFrame()
    
    # Log
    c_log = log_var+'dataframe_completed.txt'
    open(c_log,'a')
    c_list = [line[:len(line)-1] for line in open(c_log,'r')]
    
    # for loop to create xml_class objects for each uber and import to dataframe
    for file in os.listdir(uber_dir):
        
        
        # checks to see if file is a .xml to ignore the completed file folder
        if file[len(file)-4:] == ".xml":
            
            # consolidate directory for xml_class
            uber_xml = uber_dir+file
            
            if uber_xml not in c_list:
            
                # create xml_class object
                new_class = xml_class(uber_xml, db_dir)
                
                
                # append row to the dataframe where the data is the attribute of each item in xml_class for the case
                uber_dataframe = uber_dataframe.append(
                    pd.Series([getattr(new_class, item) for item in vars(new_class).keys()], index = [item for item in vars(new_class).keys()]), ignore_index = True)
                print (uber_xml+' imported to dataframe at: '+str(dt.datetime.now()))
                open(c_log,'a').write(uber_xml+'\n')
            else:
                print (uber_xml+' in c_list. Skipping...')

        else:
            pass
        done += 1
        print (str(done/total*100))
    
    # write dataframe to csv file in the uber directorys
    uber_dataframe.to_csv(path_or_buf='uber_dataframe.csv',sep="|", index=True, header=True)
    print ('Done! uber_dataframe.csv written')
    

###Run###
pool = mp.Pool()
uber_dir = "uberfiles/"
database = 'xml-database/SCDB/'
log = 'xml-database/logs/'
pool.apply(dataframe_maker(uber_dir,database,log))
