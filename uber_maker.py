from lxml import etree as et
import os
from random import randint
import datetime as dt
from index_insert import index_insert

#all paths that don't end in a file must end with '/'!

def uber_maker(s_dir,d_dir,e_file):
    ##make destination##
    os.mkdir(d_dir) if os.path.isdir(d_dir) != True else print('Uber destination: '+d_dir)
    ##exclusions list##
    e_list = [line[:len(line)-1] for line in open(e_file,'r')]
    ##completed files list##
    open(d_dir+'completed.txt','a')
    c_list = [line[:len(line)-1] for line in open(d_dir+'completed.txt', 'r')]
    ##log creation##
    os.mkdir(d_dir+'outputlogs') if os.path.isdir(d_dir+'outputlogs') != True else print('Log destination: '+d_dir+'outputlogs')
    log=open(d_dir+'outputlogs/'+str(dt.datetime.now())+'output.txt',"a",encoding='utf-8')
    ##primary and uber_loop##
    for file in os.listdir(s_dir):
        if file in c_list:
            print (file+" is in completed list. Skipped...")
        else:
            ##make temporary file directory 'temp'
            if os.path.isdir(d_dir+'temp') != True:
                os.mkdir(d_dir+'temp')
            else:
                for tmp in os.listdir(d_dir+'temp'):
                    os.remove(d_dir+'temp'+'/'+tmp)
            ##find primary
            for xml in os.listdir(s_dir+file):
                tree = et.parse(s_dir+file+'/'+xml)
                root = tree.getroot()
                #uberfile written to uberdir and uber_root is made
                if et.iselement(root.find('.//*[@status="full"]')) == True or len(os.listdir(s_dir+file))==1:
                    uber_xml = 'uber' + file +'.xml'
                    tree.write(d_dir+uber_xml)
                    uber_tree = et.parse(d_dir+uber_xml)
                    uber_root = uber_tree.getroot()
                #non-uberfiles written to temp file
                else:
                    tree.write(d_dir+'temp'+'/'+xml)
            ##create uber_list from uber_root##
            uber_list = []
            for el in uber_root.iter():
                if el.tag in e_list or e_list == []:
                    uber_list.append(el.attrib)
                elif randint(1,10) == 10:
                    uber_list.append(el.attrib)
                else:
                    pass
            ##copy missing elements from sfile to uber_file##
            for xml in os.listdir(d_dir+'temp'):
                log.write("#\n"*5)
                log.write(xml+' to '+uber_xml)
                source_root = et.parse(d_dir+'temp'+'/'+xml).getroot()
                #parse through source_file iterable and use index insert function
                for el in source_root.iter():
                    if el.tag in e_list:
                        if el.attrib in uber_list:
                            print (el.tag + " already in uber_list.skipping...")
                        else:
                            index_insert(el,uber_tree,d_dir+uber_xml,uber_xml,log)
                            uber_list.append(el.attrib)
                            if str(el.tag) not in e_list:
                                open(e_file,"a").write(str(el.tag)+"\n")
                            else:
                                pass
                    else:
                        pass
                os.remove(d_dir+'temp'+'/'+xml)
            ##when file completed write to c_file##
            open(d_dir+'completed.txt','a').write(file+"\n")
            ##delete temp file##
            os.rmdir(d_dir+'temp')
            

s_def = 'case_files/'
d_def = 'uberfiles/'
e_def = 'logs/exclusion_log.txt'

uber_maker(s_def,d_def,e_def)