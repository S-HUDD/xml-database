'''
This script is designed to work as a part of the uber_maker() function. The process is as follows:
1. Accepting information about an element missing from the destination file
2. Locating it's proper bottom-level position in the source .xml hierarchy using the lxml functions element.getparent() and element.index(sub_elemenet)
3. Using a while loop to create a list of all the parent tags immediately above it
4. Constructing a path out of the element tags starting immediately below the root
    4a. If the path doesn't exist within the destination file, it is constructed using the same path list
5. Inserting that element into the matching path hierarchy of the destination .xml file
'''

from lxml import etree as et
import os
import copy

# index_inserter accepts an xml element from the source iterative object, the uber_tree, the d_dir, the name of the directory (lexis ID in this case), and the variable for the log
def index_inserter(element, dest_tree, write_dest, filename, log_var):
    
    # creates its own version of the uber_root to avoid disrupting the uber_list
    dest_root = dest_tree.getroot()
    
    # renaming the element to preserve it for index insertion
    loop_el = element
    
    # lxml indexs of elements within their parents are stored as integers
    index_int = (loop_el.getparent()).index(loop_el)
    
    # path list will eventually contain tags of direct ancestors
    path_list = []
    
    # a while loop creates a list of the tags of each successive parent, loop_el_parent.getparent() = None when the root element is reached
    while loop_el.getparent() != None: 
        loop_el_parent = loop_el.getparent()
        
        # inserting at the beginning of the list to get proper path order starting from highest to lowest element
        path_list.insert(0,loop_el_parent)
        loop_el = loop_el_parent
    
    # Create path as a XPath String to search for parent element within destination root
    path_string = './'
    
    # for loop to create the path_string
    # starting at element 1 to skip the root for the find function, otherwise root.find() will return a NoneType
    for item in path_list[1:]: 
        
        # if loop to make subelement paths that exist in the source but not in the destination
        if dest_root.find(path_string+'/'+item.tag) == None:
            
            # catches root element so that the else statement doesn't throw a NoneType error
            if dest_root.find(path_string) == None:
                missing_parent = path_list[0]
            
            # finds the lowest common parent element and starts creating parth_string from there
            else:
                missing_parent = (dest_root.find(path_string)).getparent()
            
            # subelement factory that starts creating subelements where the source and destination hierarchies diverge
            et.SubElement(missing_parent, item.tag, item.attrib)
        else:
            pass
        
        # creates path string that ends in parent of element
        path_string = path_string+'/'+item.tag
    
    # if loop that attempts to insert the element at the end of the path_string
    if dest_root.find(path_string) != None:
        
        # finding the parent path and inserting using the lxml fucntion element.insert(sub_element) and write to file
        (dest_root.find(path_string)).insert(index_int, element)
        dest_tree.write(write_dest)
        
        # write to log file created in uber_maker
        log_var.write(filename+'\n'+element.tag+' written to: '+path_string+' at index: '+str(index_int)+'\n'*2)
        
        # print statement to aid in debugging
        print (filename+'\n'+element.tag+' written to: '+path_string+' at index: '+str(index_int))
    
    else:
        
        # debugging statement that writes that the file is not written to the dest_file to log.
        log_var.write(filename+'\n'+element.tag+' ###NOT### written to: '+path_string+'\n'*2)
        print (filename+'\n'+element.tag+' ###NOT### written to: '+path_string + '. Path not found in destination file')
            

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
    
