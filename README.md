# xml-database

## Overview

The purpose of this project is to create a program that, when given a series of similarly named US Court files as an input will process the information into a python class-object. The program will then output an easily referenceable database with information about each of the case-objects.

At the time of writing, the program is broken up into 4 major processes.
1. Extracting the .xml files from their consolidated form and writing them to an ordered directory. (exe_parser.py)
2. Files are seperated into the "uber" file and the "source" files that are similar in content and name. Differences between the source files are inserted into the destination uberfile at the proper point in the xml hierarchy. (uber_maker.py and index_insert.py)
3. Each uberfile is assigned an object "xml_class" where useful information is stored as class attributes. (xml_class.py)
4. Each instance of xml_class is added to a pandas database where each row is a case and each column is an xml_class attribute. (dataframe_maker.py)

Each of the functions is commented in detail but a general review of each is given below.

## Setup
Code was written and tested with [Anaconda3](https://conda.io/docs/user-guide/install/download.html)'s python libraries and includes the use of the [pandas](https://pandas.pydata.org/) and [lxml](https://lxml.de/) modules.

The simplest method to install lxml is via pip in the command line:
```
>>> pip install lxml
```
## Program Components
Below are the general descriptions of the python scripts that make up the xml-database program.

### exe_parser.py

exe_parser.py is an iterative script to parse through the large native ".exe" files. The script will parse through a single large_file attempting to find the line with the lexis ID saving it as the variable "filename" it will then proceed through the lines until it finds a line containing an xml string. Lexis keeps each updated version of the file, so there will be almost exact copies of a case file with very minor differences. Each of these copies will be placed in a folder named after the lexis ID and the entire xml string is written to a .xml file with the name "filename.xml" or "filename_n.xml", where n is the number of files that are already in the filename directory.

e.g. string with the ID "ABC" is placed in a folder with the same name where there are already 3 "ABC" xml files

1. string named ABC to folder ABC containing: ABC.xml, ABC_1.xml, ABC_2.xml
2. string ABC becomes ABC_3.xml and is added to folder ABC
3. folder ABC becomes: ABC.xml, ABC_1.xml, ABC_2.xml, ABC_3.xml

Example of the header and a truncated xml lines:

```
	1 --yytet00pubSubBoundary00tetyy
	2 Content-ID: urn:contentItem:3RJ6-FCK0-003B-R0KR-00000-00@lexisnexis.com
	3 Content-Type: application/vnd.courtcasedoc-newlexis+xml
	4 Content-Length: 78755
	5 <?xml version="1.0" encoding="UTF-8"?><!--Transformation version 1.1--><courtCaseDoc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.lexisnexis.com/xmlschemas/content/public/courtcasedoc/1/" schemaVersion="1.0"><courtCaseDocHead><caseInfo><caseName><fullCaseName/><shortCaseName>Feist Publ'ns, Inc. v. Rural Tel. Serv. C ... </courtCaseDoc>
```

The portion of line 2 named "3RJ6-FCK0-003B-R0KR-00000-00" is what will become the filename variable.

The program searches for 'courtCaseDoc' within the string to determine whether a line is an xml or not.
  
### uber_maker.py and insert_index.py
uber_maker.py and insert_index.py are used in tandem to create the "uberfile" and to insert missing elements into the uberfile from similar files.

#### uber_maker.py
This script uses the lxml library to parse a directory of folders containing .xml files with similar names and content.
This is accomplished in the following steps:

1. Determining which of the files, if any, have publicationstatus="full" attribute, hereby referred to as the "primary" file
2. Saving the primary file as the base for a new master file that will contain all the disparate subelements, hereby referred to as the "uberfile"
3. To iterate through the rest of the files and find the necessary subelements, and  then writing them to the uberfile at the proper hierarchy position*

	**step 3 is done with the help of the index_inserter function found in index_inserter.py*

To decrease runtime, the program uses exclusion tags. These are the tags of missing elements that appeared during the preliminary runs of this program when it ran every element in the source_file against every element in the dest_file. Now only the elements with the exclusion tags will be compared. In order to improve the exclusion list, 1 in every n tags is let in randomly to see if it is a missing tag. If the element is indeed missing from the dest_file it is added to the exclusion list as a new tag.

#### index_inserter.py
This script is designed to work as a part of the uber_maker() function. The process is as follows:
1. Accepting information about an element missing from the destination file
2. Locating it's proper bottom-level position in the source .xml hierarchy using the lxml functions ```element.getparent()
``` and ```element.index(sub_elemenet)```
3. Using a while loop to create a list of all the parent tags immediately above it
4. Constructing a path out of the element tags starting immediately below the root
    4a. If the path doesn't exist within the destination file, it is constructed using the same path list
5. Inserting that element into the matching path hierarchy of the destination .xml file

### xml_class.py
This designs a class that accepts a string containing the location of an xml file and creates a series of instances that collect parsed data from the file.
At the moment this class relies heavily on the XPath functinality of etree, whether this is the most appropirate library to use is unkown at the time of writing. Beautiful Soup 4 may be another module worth looking at.

As of 2018-08-17 This file contains instances for:
```python
self.case_name - returns the text of the <fullCaseName> tag as a string
self.docket_number - returns a string containing just the number (e.g. 46-98)
self.lexis_ID - returns a string containing the 28 character lexis ID
self.page_sceheme_citations - returns a dictionary of the text and attributes of the children in the <citations> tag of the <courtCaseHead> root element in the form of {subelement text:subelement attribute}
self.date_decide - returns a dictionary of the text and attributes of the <decisionDate> tag in the form of {element text:element attributes}
self.date_argue - returns a dictionary of the text and attributes of the <argueDate> tag in the form of {element text:element attributes}
self.case_history - returns a dictionary of {text of caseHistory element: {dict of attributes of caseHistory element}}
self.case_history_citations - returns a dictionary of {text of each citation in caseHistory element: {dict of attribute of each citation in caseHistory element}}
self.case_summaries - returns a dictionary of {text of caseSummary element: {dict of attributes of caseSummary element}}
self.case_summaries_citations - returns a dictionary of {text of each citation in caseSummary element: {dict of attribute of each citation in caseSummary element}}
self.judges - returns a dictionary of the text and an attempted list of the <judges> tag in the form of {element text:split of the element text using ","(only works with lists of only judges)}
self.judge_opinion - returns a dictionary of {[text of <caseOpinionBy>]:[attribute value of opinionType in <opinion>]} for every subelement of <caseOpinions>
self.opinion_text - returns a dictionary of {[attribute value of opinionType in <opinion>]:[iterative text of all child elements of the opinion]} for all children in <opinions>
self.opinion_text_formatted = returns the same dictionary as self.opinion_text but inclueds paragraph and anchor breaks
self.opinion_citations - returns a dictioary of {[attribute value of opinionType in <opinion>]:[list of dictioaries {citation text:citation attribute} for all citations of that opinion type]} for all children in <opinions>
self.related_content - returns a dictionary of {[text of each relatedContent item]:{[relateContent item tag]:{relatedContent item attributes}}}
self.classification_items - returns a dictionary of {[className text]:[classCode text]} for each item in classification items
self.all_citations - returns a dictionary of {citation text:citation attribute} for all citations in the .xml
self.opinion_text_count - returns a dictioary of {[opinionType]:[list of ordered pair of word count in that text block]} (e.g. {'majority':[('the', 365),('it', 220),('a', 150)...]}) 
self.opinion_citations_count - returns a dictionary of {opinionType:(citation_attribute,citation attribute count)} for each citation in each opinion type
self.all_citations_count - similar to self.opinion_citations_count but counts for all citations in the entire .xml file
```
### dataframe_maker.py
This is a simple script that incorporates the xml_class to make a dataframe.
1. The function accepts a directory that contains 1 or more uber_files
2. Each file is converted into an xml_class object
3. Each file is imported into a dataframe of uberfiles where each row is a case and the columns are the xml_class attributes
4. The dataframe is exported to .csv when complete
