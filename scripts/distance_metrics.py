import argparse
import os
import glob
import re
# import shorttext
import sqlite3
import pandas as pd
import numpy as np
from nltk.stem import PorterStemmer
# from numpy import dot
# from numpy.linalg import norm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
"""
This python script is used to calculate the similarity/distance metrics for pairs of 10-K documents.

The distance metrics used are:
	* Cosine distance
	* Jaccard dictance

The documents are represented as TF-IDF vector, and distance calculation is done using these vectors.

Calculating TF-IDF:
-------------------
TF-IDF of word x in document d, x_w = [TF(w|d) * IDF(w)] / Sqrt {Summation for all words, [TF(w'|d) * IDF(w')]^2 }

where Document Term Frequency, TF(w|d) = log(1 + N(W|d))
	  Inverse Document Frequency, IDF(w) = log(N/N(w))

The corpus used for calculating the TF-IDF values will be the entire list of Section 1-A from all 10-K documents
under consideration. Stop words will be removed based on stopwords from the Loughran Macdonald dictionary. 
The words will be stemmed before analysis.

Things to be calculated:
	* Term Document Matrix : Check out available packages.
	  Create a pandas dataframe for the Term Document Matrix, with words as the rows and documents as columns.
	  This will be a large dataframe, bound to face performance issues.
	  Available packages : shorttext, scikit-learn(CountVectorizer), textmining
	  shorttext package looks useful. Creating a pandas dataframe is not necessary if this works.

	 * EDIT : shorttext package replaced with TfIdfVectorizer from scikit learn
"""

parser = argparse.ArgumentParser()
parser.add_argument("-d","--dir",help="Directory path of repo with extracted content",required=True)
args = parser.parse_args()

def get_docs_dict(repo_dir):
	"""
	Returns a list of document contents for all documents in repo directory. The documents are
	present as "headers" and "contents" files in each subdirectory. These have to be merged to
	create one string for each document.

	In addition to this, stopwords have to be removed, and words stemmed.
	"""
	doc_dict = {}
	ps = PorterStemmer()
	header_dict,content_dict = {},{}
	# Fetching header words as dict with company ticker as key
	for header_file in glob.iglob('{0}/**/{1}'.format(repo_dir,'headers'),recursive=True):
		match = re.search(r'/(\d{4})/([a-zA-Z]+)/headers',header_file)
		key = '{0}_{1}'.format(match.group(1),match.group(2))
		with open(header_file,'r') as filein:
			contents = filein.read()
		header_word_list = re.findall(r'[a-zA-Z]+',contents)
		header_word_list = preprocess(header_word_list)
		header_dict[key] = header_word_list
	# Fetching content words as dict with company ticker as key
	for content_file in glob.iglob('{0}/**/{1}'.format(repo_dir,'contents'),recursive=True):
		match = re.search(r'/(\d{4})/([a-zA-Z]+)/contents',content_file)
		key = '{0}_{1}'.format(match.group(1),match.group(2))
		with open(content_file,'r') as filein:
			contents = filein.read()
		content_word_list = re.findall(r'[a-zA-Z]+',contents)
		content_word_list = preprocess(content_word_list)
		content_dict[key] = content_word_list
	# Creating doc dict
	for key,values in header_dict.items():
		doc_dict[key] = " ".join([*values,*content_dict[key]])
	return doc_dict

def preprocess(words):
	ps = PorterStemmer()
	# Fetching list of stopwords
	stopwords = get_stopwords()
	# Stemming words, changing to upper case
	words = [ps.stem(word).upper() for word in words if word.upper() not in stopwords]
	# Removing "HEADER_" AND "CONTENT_"
	words = [word for word in words if not any(substr in word for substr in ['HEADER_','CONTENT_'])]
	return words

def get_stopwords():
	"""
	Returns list of stopwords from loughran and macdonald dictionary for financial terms.
	"""
	stopwords_file = '/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/loughran_macdonald/stopwords.txt'
	with open(stopwords_file,'r') as filein:
		contents = filein.read()
	return contents.split('\n')

def get_dtm(docs):
	"""
	Returns Docids and Document term matrix for dictionary where keys are document names and values are
	string of preprocessed word tokens
	"""
	docids = sorted(docs.keys())
	corpus = [docs[docid] for docid in docids]
	# dtm = shorttext.utils.DocumentTermMatrix(corpus, docids=docids,tfidf=True)
	vectorizer = TfidfVectorizer()
	dtm = vectorizer.fit_transform(corpus)
	return docids,dtm

# def cosine_sim(doc_dict1,doc_dict2):
# 	"""
# 	Finds cosine similarity between document pairs represented as dict of word tokens and tf/tf-idf scores
# 	"""
# 	keys = sorted(list(set(doc_dict1.keys()) | set(doc_dict2.keys())))
# 	doc_list1 = [doc_dict1.get(key,0) for key in keys]
# 	doc_list2 = [doc_dict2.get(key,0) for key in keys]
# 	return dot(doc_list1, doc_list2)/(norm(doc_list2)*norm(doc_list2))

def pair_sim(idx,docid,docids,dtm):
	"""
	Returns pandas dataframe which holds document name and pairwise cosine similarities 
	for document with all other documents in the Document term matrix.
	"""
	# Calculating cosine similarity of current doc with all other docs
	sim_array = linear_kernel(dtm[idx], dtm).flatten()
	# Converting array of similarities to dict 
	cos_dict = dict(zip(docids,sim_array))
	cos_dict['Document'] = docid
	# for doc in dtm.docids:
	# 	doc_dict1 = dtm.get_doc_tokens(docid)
	# 	doc_dict2 = dtm.get_doc_tokens(doc)
	# 	cos_dict[doc] = cosine_sim(doc_dict1,doc_dict2)
	return cos_dict

def write_db(repo_dir,sim_matrix):
	# Creating/Connecting sqlite database
	conn = sqlite3.connect('{0}/stats.db'.format(repo_dir))
	sim_matrix.to_sql('cos_sim_matrix', con=conn, if_exists='replace', index=False)
	conn.commit()
	conn.close()

def main(args):
	repo_dir = args.dir
	repo_dir = os.path.abspath(repo_dir)

	# Return dict of all documents, with key being the company ticker and year, value being the list of 
	# preprocessed word tokens.
	# Remove stopwords and stem the words before returning as list
	docs = get_docs_dict(repo_dir)

	# Creating Document Term Matrix using shorttext package
	# EDIT : Changed to scikit-learn TfIdfVectorizer
	docids,dtm = get_dtm(docs)

	# Calculating the pairwise cosine similarities using the computed tf-idf values.
	# For N documents in the corpus, an N*N matrix is to be generated, which stores the pairwise
	# similarities for all pairs of documents.
	# The results are stored in a pandas dataframe, and also written to local file
	sim_matrix = pd.DataFrame(columns=['Document'] + docids)
	# Iterating through documents,and finding pairwise similarities
	for idx,docid in enumerate(docids):
		row_dict = pair_sim(idx,docid,docids,dtm)
		sim_matrix = sim_matrix.append(row_dict,ignore_index=True)
	# Writing calculated similarity matrix to csv file
	sim_matrix.to_csv('{0}/cosine_sim_matrix.csv'.format(repo_dir),index=False)
	# Writing calculated similarity matrix to sqlite database
	write_db(repo_dir,sim_matrix)



if __name__ == '__main__':
	main(args)