'''
proof of concept to see if the index/path of an element can be successfully located. streamlined version will be integrated into uberxmlmakerV4.py
'''

from lxml import etree as et
import os
import copy
# import datetime


def index_insert(element, dest_tree, write_dest, filename, log_var): #accepts a xml element from a source iter element and a root of a destination file
    dest_root = dest_tree.getroot()
    ##Path and Index Finding loop##
    loop_el = element
    index_int = (loop_el.getparent()).index(loop_el)
    path_list = []
    while loop_el.getparent() != None: #if the element is not in the list, a while loop creates a list of the index of each successive parent
        loop_el_parent = loop_el.getparent()
        path_list.insert(0,loop_el_parent)
        loop_el = loop_el_parent
    ##Create path as a XPath String to search for parent element within destination root
    path_string = './'
    for item in path_list[1:]: #start at element 1 to skip the root for the find function
        ##if loop to make subelement paths that exist in the source but not in the destination
        if dest_root.find(path_string+'/'+item.tag) == None:
            if dest_root.find(path_string) == None:
                missing_parent = path_list[0]
            else:
                missing_parent = (dest_root.find(path_string)).getparent()
            et.SubElement(missing_parent, item.tag, item.attrib)
        else:
            pass
        ##creates path string that ends in parent of element
        path_string = path_string+'/'+item.tag
    if dest_root.find(path_string) != None:
        (dest_root.find(path_string)).insert(index_int, element)
        log_var.write(filename+'\n'+element.tag+' written to: '+path_string+' at index: '+str(index_int)+'\n'*2)
        dest_tree.write(write_dest)
        print (filename+'\n'+element.tag+' written to: '+path_string+' at index: '+str(index_int))
    else:
        log_var.write(filename+'\n'+element.tag+' ###NOT### written to: '+path_string+'\n'*2)
        print (filename+'\n'+element.tag+' ###NOT### written to: '+path_string)
            

# ###Test###
# s_file = 'PSULawProject/Case_Files/3S4X-3SG0-003B-71N0-00000-00/3S4X-3SG0-003B-71N0-00000-00_2.xml'
# s_tree = et.parse(s_file)
# s_root = s_tree.getroot()
# s_list = [element for element in s_root.iter()]
# d_file = 'PSULawProject/Case_Files/3S4X-3SG0-003B-71N0-00000-00/3S4X-3SG0-003B-71N0-00000-00_13.xml'
# d_tree = et.parse(d_file)
# d_root = d_tree.getroot()
# d_list = [element.attrib for element in d_root.iter()]

# open('PSULawProject/index_log.txt','w')
# for el in s_list:
#     if el.attrib in d_list:
#         print ('pass')
#     else:
#         index_finder(el, d_tree,'PSULawProject/index_finder_test.xml')
#         print('write '+el.tag)
#         # d_list.append(el.attrib)
    
