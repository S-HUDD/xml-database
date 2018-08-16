'''
This designs a class that accepts a string containing the location of an xml file and creates a series of instances that collect parsed data from the file.
This file will likely be combined with pandas or pickle to preserve the data.
At the moment this class relies heavily on the XPath functinality of etree, whether this is the most appropirate library to use is debatable. Beautiful Soup 4 may be another module worth looking at.

As of 2018-07-31 This file contains instances for:
# self.case_name - returns the text of the <fullCaseName> tag as a string
# self.page_sceheme_citations - returns a dictionary of the text and attributes of the children in the <citations> tag of the <courtCaseHead> root element in the form of {subelement text:subelement attribute}
# self.date_decide - returns a dictionary of the text and attributes of the <decisionDate> tag in the form of {element text:element attributes}
# self.date_argue - returns a dictionary of the text and attributes of the <argueDate> tag in the form of {element text:element attributes}
# self.judges - returns a dictionary of the text and an attempted list of the <judges> tag in the form of {element text:split of the element text using ","(only works with lists of only judges)}
# self.judge_opinion - returns a dictionary of {[text of <caseOpinionBy>]:[attribute value of opinionType in <opinion>]} for every subelement of <caseOpinions>
# self.opinion_text - returns a dictionary of {[attribute value of opinionType in <opinion>]:[iterative text of all child elements of the opinion]} for all children in <opinions>
# self.opinion_citations - returns a dictioary of {[attribute value of opinionType in <opinion>]:[list of dictioaries {citation text:citation attribute} for all citations of that opinion type]} for all children in <opinions>

Add
# metadata (done)
# docket number (done)
# case history (done)
# case summaries (done)
who signed opinions
'''

from lxml import etree as et
import pandas as pd
import os

class xml_class:
    def __init__(self, uber_xml):
        ###UBERROOT###
        ##Uber_xml##
        self.uber_xml = uber_xml
        uber_root = et.parse(uber_xml).getroot()
        
        ###HEADING###
        ##Indexing##
        self.case_name = uber_root.find('.//fullCaseName').text
        self.docket_number = uber_root.findtext('.//docketNumber').replace('No. ','')
        self.lexis_cite = uber_xml[len(uber_xml)-32:len(uber_xml)-4] #due to the "dc:" prefix on the subelements of the '<dc:metadata>' element, the dc:identifier child can't be parsed by lxml to extract the lexis cite. Might be a work-around for it but this solution works for now, even if it's not elegant.
        ##Heading Citations, decision/argue dates##
        self.page_sceheme_citations = {element.text:element.attrib for element in uber_root.findall('.//citeForThisResource')}
        self.date_decide = uber_root.find('.//decisionDate').attrib
        date_decide_formatted = self.date_decide.get('month')+'/'+self.date_decide.get('day')+'/'+self.date_decide.get('year')
        self.date_argue = uber_root.find('.//arguedDate').attrib
        ##History and summaries##
        self.case_history = {''.join(subelement.itertext()).encode('utf-8'):subelement.attrib for subelement in uber_root.find('.//*caseHistory')}
#         self.case_history_citations = {''.join(subelement.itertext()).encode('utf-8'):subelement.attrib for subelement in uber_root.findall('.//caseHistory//citation')}
        self.case_summaries = {subelement.tag:''.join(subelement.itertext()).encode('utf-8') for subelement in uber_root.find('.//*summaries')}
        self.case_summaries_citations = {''.join(subelement.itertext()).encode('utf-8'):subelement.attrib for subelement in uber_root.findall('.//summaries//citation')}
        
        ###BODY###
        ##Justices##
        if uber_root.findtext('.//panel/judges') != None:
            self.judges = {uber_root.findtext('.//panel/judges'):uber_root.findtext('.//panel/judges').split(", ")}
        else:
            self.judges = ""
        
        ##Opinion Type and the justices that wrote them##
        self.judge_opinion = {element.get('opinionType'):element.findtext('.//caseOpinionBy') for element in uber_root.findall('.//caseOpinions/opinion')}
        
        ##Judge Name and their opinion from the Supreme Court Database
#         self.judge_opinion_db = {}
#         if int(self.date_decide.get('year')) >= 1946:
#             scdb = pd.read_csv('PSULawProject/SCDB/SSCDB_Modern_justiceCentered_Docket.csv',encoding = 'latin-1')
#         else:
#             scdb = pd.read_csv('PSULawProject/SCDB/SCDB_Legacy_justiceCentered_Citation.csv',dtype=str,encoding = 'latin-1')
#         scdb = scdb[scdb.docket == self.docket_number]
#         split_scdb = scdb[scdb.dateDecision == date_decide_formatted]
#         for index, row in split_scdb.iterrows():
#                 self.judge_opinion_db.update({row['justiceName']:row['vote']})
            
        ##Opinion Type and the entire text of the opinion##
        self.opinion_text = {element.get('opinionType'):''.join(element.itertext()).encode('utf-8') for element in uber_root.findall('.//caseOpinions/opinion')}
        
        ##Opinion Type and the entire text of the opinion with paragraph (#p#) and anchor ($$$attrib$$$) breaks
        self.opinion_text_formatted = {}
        for element in uber_root.findall('.//caseOpinions/opinion'):
            op_type = element.get('opinionType')
            op_text = str(element.find('.//caseOpinionBy').text)
            for paragraph in element.findall('.//bodyText/p'):
                if paragraph.itertext() == None:
                    op_text = op_text+' #p# '+' $$$ '+str(paragraph.find('.//anchor').attrib)+' $$$ ' + 'None'
                else:
                    op_text = op_text+' #p# '+' $$$ '+str(paragraph.find('.//anchor').attrib)+' $$$ '+''.join(paragraph.itertext())
            op_text.replace('{}','')
            self.opinion_text_formatted.update({op_type:op_text.encode('utf-8')})
        
        ##Opinion Type and each citation that appears in that opinion##
        self.opinion_citations = {}
        for element in uber_root.findall('.//*[@opinionType]'):
            opinion_citations = {}
            for subelement in element.findall('.//citation'):
                opinion_citations.update({''.join(subelement.itertext()).encode('utf-8'):subelement.attrib})
            self.opinion_citations.update({element.get('opinionType'):opinion_citations})
        
        ###METADATA###
        
        ##Related Content
        self.related_content = {}
        for element in uber_root.findall('.//metadata//relatedContentItem'):
            element_text = ''.join(element.itertext()).encode('utf-8')
            value_dict = {}
            for subelement in element.findall('.//*'):
                if subelement.attrib != {}:
                    value_dict.update({subelement.tag:str(subelement.attrib).encode('utf-8')})
                else:
                    pass
            self.related_content.update({element_text:value_dict})
        
        ##Classification Items##
        self.classification_items = {element.findtext('.//className'):element.findtext('.//classCode') for element in uber_root.findall('.//metadata//*classificationItem')}
            
            
        ###Counters###
        
        ##dict of every citation in the document##
        self.all_citations = {''.join(element.itertext()):element.attrib for element in uber_root.findall('.//citation')}
        
        ##dict of count of each word in every opinion type##
        self.opinion_text_count = {}
        for key in self.opinion_text:
            word_list = self.opinion_text.get(key).decode('utf-8').lower().split()
            word_count = []
            for word in word_list:
                word_freq = word_list.count(word)
                if (word,word_freq) not in word_count:
                    word_count.append((word, word_freq))
            self.opinion_text_count.update({key:sorted(word_count, key = lambda x:x[1], reverse = True)})
        
        ##dict of count of each citation id in every opinion type
        self.opinion_citations_count = {}
        for key in self.opinion_citations:
            cite_count = []
            cite_list = []
            for sub_key in self.opinion_citations.get(key):
                cite = self.opinion_citations.get(key).get(sub_key).get('id')
                cite_list.append(cite)
            for cite in cite_list:
                cite_freq = cite_list.count(cite)
                if (cite,cite_freq) not in cite_count:
                    cite_count.append((cite,cite_freq))
            self.opinion_citations_count.update({key:sorted(cite_count, key = lambda x:x[1], reverse = True)})
        
        ##All Citations Count##
        self.all_citations_count = []
        cite_list = []
        for key in self.all_citations:
            cite = self.all_citations.get(key).get('normalizedCite'), self.all_citations.get(key).get('id'), self.all_citations.get(key).get('type')
            cite_list.append(cite)
        for cite in cite_list:
            cite_freq = cite_list.count(cite)
            if (cite,cite_freq) not in cite_count:
                self.all_citations_count.append((cite,cite_freq))
        self.all_citations_count = sorted(self.all_citations_count, key = lambda x:x[1], reverse = True)
                
            
            
 
test1 = xml_class('PSULawProject/uberfiles/uber-3S4X-3SG0-003B-71N0-00000-00.xml')
log = open('PSULawProject/log/class_log.txt','w', encoding = 'utf-8')
log_list = [item+"\n"+str(getattr(test1,item))+"\n"*2 for item in vars(test1).keys()]
for item in log_list:
    log.write(item)


# import pickle

# uber_dir = "PSULawProject/uberfiles/"
# # uber_dataframe = pd.DataFrame()
# pickle_dir = "PSULawProject/class_dump.pkl"
# pickle_file = open(pickle_dir, 'wb')

# for file in os.listdir(uber_dir):
#     if file[len(file)-4:] == ".xml":
#         pickle.dump(xml_class(uber_dir+file), pickle_file)
#     else:
#         pass