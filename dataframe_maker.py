from lxml import etree as et
import pandas as pd
import numpy as np
import os
from xml_class import xml_class

def uber_dataframe_maker(uber_directory):
    uber_dataframe = pd.DataFrame()
    for file in os.listdir(uber_dir):
        if file[len(file)-4:] == ".xml":
            uber_xml = uber_dir+file
            new_class = xml_class(uber_xml)
            uber_dataframe = uber_dataframe.append(
                pd.Series([getattr(new_class, item) for item in vars(new_class).keys()], index = [item for item in vars(new_class).keys()]), ignore_index = True)
            print (uber_xml+' imported to dataframe')
        else:
            pass
    uber_dataframe.to_csv(path_or_buf=uber_dir+'uber_dataframe.csv',sep="|", index=True, header=True)
    
uber_dir = "PSULawProject/uberfiles/"
uber_dataframe_maker(uber_dir)