import pickle
from Uber2Object import xml_class

unpickle_dir = "PSULawProject/class_dump.pkl"
unpickle_file = open(unpickle_dir, 'rb')

pickle.load(unpickle_file)