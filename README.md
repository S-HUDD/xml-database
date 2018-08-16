# xml-database

-Overview-

The purpose of this project is to create a program that, when given a series of similarly named US Court files as an input will process the information into a python class-object. The program will then output an easily referenceable database with information about each of the case-objects.

At the time of writing, the program is broken up into 4 major processes.
1. Extracting the .xml files from their consolidated form and writing them to an ordered directory. (exe_parser.py)
2. Files are seperated into the "uber" file and the "source" files that are similar in content and name. Differences between the source files are inserted into the destination uberfile at the proper point in the xml hierarchy. (uber_maker.py and index_insert.py)
3. Each uberfile is assigned an object "xml_class" where useful information is stored as class attributes. (xml_class.py)
4. Each instance of xml_class is added to a pandas database where each row is a case and each column is an xml_class attribute. (dataframe_maker.py)

Each of the scripts is commented but the specifics of each will be detailed below.
