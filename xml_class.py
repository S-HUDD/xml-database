'''
This designs a class that accepts a string containing the location of an xml file and creates a series of instances that collect parsed data from the file.
At the moment this class relies heavily on the XPath functinality of etree, whether this is the most appropirate library to use is unkown at the time of writing. Beautiful Soup 4 may be another module worth looking at.

As of 2018-08-17 This file contains instances for:

# self.case_name - returns the text of the <fullCaseName> tag as a string
# self.docket_number - returns a string containing just the number (e.g. 46-98)
# self.lexis_ID - returns a string containing the 28 character lexis ID
# self.page_sceheme_citations - returns a dictionary of the text and attributes of the children in the <citations> tag of the <courtCaseHead> root element in the form of {subelement text:subelement attribute}
# self.date_decide - returns a dictionary of the text and attributes of the <decisionDate> tag in the form of {element text:element attributes}
# self.date_argue - returns a dictionary of the text and attributes of the <argueDate> tag in the form of {element text:element attributes}
# self.case_history - returns a dictionary of {text of caseHistory element: {dict of attributes of caseHistory element}}
# self.case_history_citations - returns a dictionary of {text of each citation in caseHistory element: {dict of attribute of each citation in caseHistory element}}
# self.case_summaries - returns a dictionary of {text of caseSummary element: {dict of attributes of caseSummary element}}
# self.case_summaries_citations - returns a dictionary of {text of each citation in caseSummary element: {dict of attribute of each citation in caseSummary element}}
# self.judges - returns a dictionary of the text and an attempted list of the <judges> tag in the form of {element text:split of the element text using ","(only works with lists of only judges)}
# self.judge_opinion - returns a dictionary of {[text of <caseOpinionBy>]:[attribute value of opinionType in <opinion>]} for every subelement of <caseOpinions>
# self.opinion_text - returns a dictionary of {[attribute value of opinionType in <opinion>]:[iterative text of all child elements of the opinion]} for all children in <opinions>
# self.opinion_text_formatted = returns the same dictionary as self.opinion_text but inclueds paragraph and anchor breaks
# self.opinion_citations - returns a dictioary of {[attribute value of opinionType in <opinion>]:[list of dictioaries {citation text:citation attribute} for all citations of that opinion type]} for all children in <opinions>
# self.related_content - returns a dictionary of {[text of each relatedContent item]:{[relateContent item tag]:{relatedContent item attributes}}}
# self.classification_items - returns a dictionary of {[className text]:[classCode text]} for each item in classification items
# self.all_citations - returns a dictionary of {citation text:citation attribute} for all citations in the .xml
# self.opinion_text_count - returns a dictioary of {[opinionType]:[list of ordered pair of word count in that text block]} (e.g. {'majority':[('the', 365),('it', 220),('a', 150)...]})
# self.opinion_citations_count - returns a dictionary of {opinionType:(citation_attribute,citation attribute count)} for each citation in each opinion type
# self.all_citations_count - similar to self.opinion_citations_count but counts for all citations in the entire .xml file


todo:
opinion signtures

"caseId","docketId","caseIssuesId","voteId","dateDecision","decisionType","usCite","sctCite","ledCite","lexisCite","term","naturalCourt","chief","docket","caseName","dateArgument","dateRearg","petitioner","petitionerState","respondent","respondentState","jurisdiction","adminAction","adminActionState","threeJudgeFdc","caseOrigin","caseOriginState","caseSource","caseSourceState","lcDisagreement","certReason","lcDisposition","lcDispositionDirection","declarationUncon","caseDisposition","caseDispositionUnusual","partyWinning","precedentAlteration","voteUnclear","issue","issueArea","decisionDirection","decisionDirectionDissent","authorityDecision1","authorityDecision2","lawType","lawSupp","lawMinor","majOpinWriter","majOpinAssigner","splitVote","majVotes","minVotes","justice","justiceName","vote","opinion","direction","majority","firstAgreement","secondAgreement"
"1946-001","1946-001-01","1946-001-01-01","1946-001-01-01-01-01",11/18/1946,1,"329 U.S. 1","67 S. Ct. 6","91 L. Ed. 3","1946 U.S. LEXIS 1724",1946,1301,"Vinson","24","HALLIBURTON OIL WELL CEMENTING CO. v. WALKER et al., DOING BUSINESS AS DEPTHOGRAPH CO.",1/9/1946,10/23/1946,198,,172,,6,,,0,51,6,29,,0,11,2,1,1,3,0,1,1,0,80180,8,2,0,4,,6,600,"35 U.S.C. � 33",78,78,1,8,1,86,"HHBurton",2,1,1,1,,


'''

from lxml import etree as et
import pandas as pd
import os
import datetime as dt

# Dictionaries used to get string response for SCDB codes

vote_dict = {1 : "voted with majority or plurality", 2 : "dissent", 3 : "regular concurrence", 4 : "special concurrence", 5 : "judgment of the Court", 6 : "dissent from a denial or dismissal of certiorari , or dissent from summary affirmation of an appeal", 7 : "jurisdictional dissent", 8 : "justice participated in an equally divided vote"}
opinion_dict = {1:"justice wrote no opinion", 2:"justice wrote an opinion", 3:"justice co-authored an opinion"}
direction_dict = {1:"conservative", 2:"liberal"}
majority_dict = {1:"dissent", 2:"majority"}
Agreement_dict = {1: 'JJay', 2: 'JRutledge', 3: 'WCushing', 4: 'JWilson', 5: 'JBlair', 6: 'JIredell', 7: 'TJohnson', 8: 'WPaterson', 9: 'JRutledge', 10: 'SChase', 11: 'OEllsworth', 12: 'BWashington', 13: 'AMoore', 14: 'JMarshall', 15: 'WJohnson', 16: 'HBLivingston', 17: 'TTodd', 18: 'GDuvall', 19: 'JStory', 20: 'SThompson', 21: 'RTrimble', 22: 'JMcLean', 23: 'HBaldwin', 24: 'JMWayne', 25: 'RBTaney', 26: 'PPBarbour', 27: 'JCatron', 28: 'JMcKinley', 29: 'PVDaniel', 30: 'SNelson', 31: 'LWoodbury', 32: 'RCGrier', 33: 'BRCurtis', 34: 'JACampbell', 35: 'NClifford', 36: 'NHSwayne', 37: 'SFMiller', 38: 'DDavis', 39: 'SJField', 40: 'SPChase', 41: 'WStrong', 42: 'JPBradley', 43: 'WHunt', 44: 'MRWaite', 45: 'JHarlan1', 46: 'WBWoods', 47: 'SMatthews', 48: 'HGray', 49: 'SBlatchford', 50: 'LQLamar', 51: 'MWFuller', 52: 'DJBrewer', 53: 'HBBrown', 54: 'GShiras', 55: 'HEJackson', 56: 'EDEWhite', 57: 'RWPeckham', 58: 'JMcKenna', 59: 'OWHolmes', 60: 'WRDay', 61: 'WHMoody', 62: 'HHLurton', 63: 'CEHughes1', 64: 'WVanDevanter', 65: 'JRLamar', 66: 'MPitney', 67: 'JCMcReynolds', 68: 'LDBrandeis', 69: 'JHClarke', 70: 'WHTaft', 71: 'GSutherland', 72: 'PButler', 73: 'ETSanford', 74: 'HFStone', 75: 'CEHughes2', 76: 'OJRoberts', 77: 'BNCardozo', 78: 'HLBlack', 79: 'SFReed', 80: 'FFrankfurter', 81: 'WODouglas', 82: 'FMurphy', 83: 'JFByrnes', 84: 'RHJackson', 85: 'WBRutledge', 86: 'HHBurton', 87: 'FMVinson', 88: 'TCClark', 89: 'SMinton', 90: 'EWarren', 91: 'JHarlan2', 92: 'WJBrennan', 93: 'CEWhittaker', 94: 'PStewart', 95: 'BRWhite', 96: 'AJGoldberg', 97: 'AFortas', 98: 'TMarshall', 99: 'WEBurger', 100: 'HABlackmun', 101: 'LFPowell', 102: 'WHRehnquist', 103: 'JPStevens', 104: 'SDOConnor', 105: 'AScalia', 106: 'AMKennedy', 107: 'DHSouter', 108: 'CThomas', 109: 'RBGinsburg', 110: 'SGBreyer', 111: 'JGRoberts', 112: 'SAAlito', 113: 'SSotomayor', 114: 'EKagan', 115: 'NMGorsuch'}



# instances of xml_class are created by calling xml_class(xml) where xml is the path to an uber_xml case file
class xml_class:
    def __init__(self, uber_xml,db_dir):
        try:
            ###UBERROOT###
            # creating an attribute self.uber_xml and an internal variable uber_root
            self.uber_xml = uber_xml
            uber_root = et.parse(uber_xml).getroot()
            
            
            ###HEADING###
            
            ##Indexing##
            self.case_name = uber_root.find('.//fullCaseName').text
            self.docket_number = uber_root.findtext('.//docketNumber').replace('No. ','')
            self.lexis_ID = uber_xml[len(uber_xml)-32:len(uber_xml)-4] #due to the "dc:" prefix on the subelements of the '<dc:metadata>' element, the dc:identifier child can't be parsed by lxml to extract the lexis cite. Might be a work-around for it but this solution works for now, even if it's not elegant.
            
            ##Heading Citations, decision/argue dates##
            self.page_sceheme_citations = {element.text:element.attrib for element in uber_root.findall('.//citeForThisResource')}
            self.date_decide = uber_root.find('.//decisionDate').attrib
            date_decide_formatted = (self.date_decide.get('month')).replace('0','')+'/'+self.date_decide.get('day')+'/'+self.date_decide.get('year')
            self.date_argue = uber_root.find('.//arguedDate').attrib
            
            ##DATABASE##
            if int(self.date_decide.get('year')) >= 1946:
                scdb = pd.read_csv(db_dir+'SCDB_Modern_justiceCentered_Docket.csv',dtype=str, encoding = 'latin-1')
            else:
                scdb = pd.read_csv(db_dir+'SCDB_Legacy_justiceCentered_Citation.csv',dtype=str,encoding = 'latin-1')
            scdb = scdb[(scdb.dateDecision == date_decide_formatted) & (scdb.docket == self.docket_number)]
            # self.db_rows = [str(row) for index, row in scdb.iterrows()]
            
            ##History and summaries##
            self.case_history = {''.join(subelement.itertext()).encode('utf-8'):subelement.attrib for subelement in uber_root.find('.//*caseHistory')}
            self.case_history_citations = {''.join(subelement.itertext()).encode('utf-8'):subelement.attrib for subelement in uber_root.findall('.//caseHistory//citation')}
            self.case_summaries = {subelement.tag:''.join(subelement.itertext()).encode('utf-8') for subelement in uber_root.find('.//*summaries')}
            self.case_summaries_citations = {''.join(subelement.itertext()).encode('utf-8'):subelement.attrib for subelement in uber_root.findall('.//summaries//citation')}
            
            ###BODY###
            
            
            ##Justices##
            self.judges = [row.justiceName for index, row in scdb.iterrows()]
                
            
            ##Opinion Type and the justices that wrote them##
            self.judge_opinion = {element.get('opinionType'):element.findtext('.//caseOpinionBy') for element in uber_root.findall('.//caseOpinions/opinion')}
            
            ##Judge Name and their opinion from the Supreme Court Database
            self.judge_opinion_db = {}
            for index, row in scdb.iterrows():
                    self.judge_opinion_db.update({row['justiceName']:{"vote":row["vote"], "opinion":row["opinion"],"direction":row["direction"],"majority":row["majority"],"firstAgreement":row["firstAgreement"],"secondAgreement":row["secondAgreement"]}})
                
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
            # these class attributes create dictionaries of ordered pairs counting instances of words and citations
            
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
        except AttributeError:
            print('Attribute Error, pass')
            
            
 
# test1 = xml_class('uberfiles/uber5K3P-VXF1-F04K-F1HS-00000-00.xml','xml-database/SCDB/')
# log = open('xml-database/logs/class_log.txt','w', encoding = 'utf-8')
# log_list = [item+"\n"+str(getattr(test1,item))+"\n"*2 for item in vars(test1).keys()]
# for item in log_list:
#     log.write(item)


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
