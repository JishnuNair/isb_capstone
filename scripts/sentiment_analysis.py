import argparse
import glob
import os
import re
import sqlite3
from nltk.stem import PorterStemmer

"""
This python script is to get the various initial risk statistics and sentiment, tones for the risk factors mentioned 
in 10-K documents for each organization. 
The initial metrics are the following:
	* Number of risk titles
	* Number of words in each risk title
	* Number of words in paragraphs under each title
	* Total number of words

The extracted sentiment/tones are the following:
	* Positive
	* Negative
	* Constraining
	* Litigious
	* Modality
	* Uncertainty
The number of words with each tone mentioned above is extracted, and the proportion of each tonal category
is used to ascertain the overall sentiment of each document. The word dictionaries provided by Loughran and Macdonald 
are used to find the tones and remove stopwords.

The extracted stats are uploaded to a sqlite database.

Parameters:
	* Repo directory with extracted content
	 These directories have "headers" and "contents" files under sub diectories named based on company ticker
"""

parser = argparse.ArgumentParser()
parser.add_argument("-d","--dir",help="Directory with extracted contents",required=True)
args = parser.parse_args()

def get_files(repo_dir,year,file_type):
	repo_dir = os.path.join(repo_dir,year)
	dict_ = {}
	for filename in glob.iglob('{0}/**/{1}'.format(repo_dir,file_type),recursive=True):
		key = re.search('/(\w+)/{0}'.format(file_type),filename).group(1)
		dict_[key] = filename
	return dict_

def get_stats(header_dict,para_dict):
	stats_dict = {}
	# Iterating through all companies
	for key,value in header_dict.items():
		# Reading each header file
		with open(value,'r') as filein:
			header_contents = filein.read()
		# Extracting headers as list
		headers = re.split('\nHEADER_\d+:\n',header_contents)
		# Reading each contents file
		with open(para_dict[key],'r') as filein:
			para_contents = filein.read()
		# Extracting contents as list
		paragraphs = re.split('\nCONTENT_\d+:\n',header_contents)
		# Fetching required stats for current company
		stats_dict[key] = parse_header_contents(headers,paragraphs)
	return stats_dict

def get_sentiments(header_dict,para_dict):
	senti_dict = {}
	# Iterating through all companies
	for key,value in header_dict.items():
		# Reading each header file
		with open(value,'r') as filein:
			header_contents = filein.read()
		# Extracting headers as list
		headers = re.split('\nHEADER_\d+:\n',header_contents)
		# Reading each contents file
		with open(para_dict[key],'r') as filein:
			para_contents = filein.read()
		# Extracting contents as list
		paragraphs = re.split('\nCONTENT_\d+:\n',header_contents)
		# Fetching sentiment word counts
		senti_dict[key] = senti_counts(headers,paragraphs)
	return senti_dict

def senti_counts(headers,paragraphs):
	lou_mac_dir = '/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/loughran_macdonald'
	files_dict,words_dict = {},{}
	files_dict['negative'] = '{0}/negative.txt'.format(lou_mac_dir)
	files_dict['positive'] = '{0}/positive.txt'.format(lou_mac_dir)
	files_dict['constraining'] = '{0}/constraining.txt'.format(lou_mac_dir)
	files_dict['litigious'] = '{0}/litigious.txt'.format(lou_mac_dir)
	files_dict['uncertainty'] = '{0}/uncertainty.txt'.format(lou_mac_dir)
	files_dict['modal_strong'] = '{0}/modal_strong.txt'.format(lou_mac_dir)
	files_dict['modal_moderate'] = '{0}/modal_moderate.txt'.format(lou_mac_dir)
	files_dict['modal_weak'] = '{0}/modal_weak.txt'.format(lou_mac_dir)
	files_dict['stopwords'] = '{0}/stopwords.txt'.format(lou_mac_dir)
	# Reading files into lists
	for key,value in files_dict.items():
		with open(value,'r') as filein:
			contents = filein.read()
		words_dict[key] = contents.split('\n')
	# Splitting headers and paragraphs to list of words
	headers = [word.upper() for word in " ".join(headers).split()]
	paragraphs = [word.upper() for word in " ".join(paragraphs).split()]
	# Merging header and paragraphs lists, and converting to upper case, removing stop words
	words = [*headers,*paragraphs]
	words = [word.upper() for word in words if word not in words_dict['stopwords']]
	#print(headers)
	#print(paragraphs)
	#print(words)
	# Counting occurences of words of each sentiment type
	senti_counts = {}
	for key,values in words_dict.items():
		if key != 'stopwords':
			senti_counts[key] = len([word for word in words if word in values])
	# Fetching total count of words, excluding stopwords
	senti_counts['total_words'] = len(words)
	return list(senti_counts.values())


def parse_header_contents(headers,paragraphs):
	# Getting count of headers
	header_count = len(headers)
	
	# Getting total count of words in headers
	header_word_list = re.findall(r'\w+',' '.join(headers))
	# Stemming words
	ps = PorterStemmer()
	header_word_list = [ps.stem(word) for word in header_word_list]
	# Counting unique stemmed words
	header_word_count = len(set(header_word_list))

	# Getting count of words in paragraphs
	para_word_list = re.findall(r'\w+',' '.join(paragraphs))
	# Stemming words
	para_word_list = [ps.stem(word) for word in para_word_list]
	# Counting unique stemmed words
	para_word_count = len(set(para_word_list))

	return [header_count,header_word_count,para_word_count]

def write_db(repo_dir,years_stats_dict,years_senti_dict):
	# Creating/Connecting sqlite database
	conn = sqlite3.connect('{0}/stats.db'.format(repo_dir))
	# Creating table if not exists
	conn.execute("""CREATE TABLE IF NOT EXISTS STATS_SENTI
		(TICKER CHAR(25) NOT  NULL,
		 YEAR INT NOT NULL,
		 HEADER_CNT INT NOT NULL,
		 HEADER_WORD_CNT INT NOT NULL,
		 PARA_WORD_CNT INT NOT NULL,
		 NEG_CNT INT,
		 POS_CNT INT,
		 CONSTR_CNT INT,
		 LITI_CNT INT,
		 UNCERT_CNT INT,
		 MODAL_STR_CNT INT,
		 MODAL_MOD_CNT INT,
		 MODAL_WEA_CNT INT,
		 TOT_CNT INT,
		 PRIMARY KEY (TICKER,YEAR)
		);	
		""")
	# Inserting records
	for year,stats_dict in years_stats_dict.items():
		for key,value in stats_dict.items():
			print("INSERTING '{0}',{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}".format(key,year,value[0],value[1],value[2],
					years_senti_dict[year][key][0],years_senti_dict[year][key][1],years_senti_dict[year][key][2],
					years_senti_dict[year][key][3],years_senti_dict[year][key][4],years_senti_dict[year][key][5],
					years_senti_dict[year][key][6],years_senti_dict[year][key][7],years_senti_dict[year][key][8]))
			conn.execute("""INSERT OR REPLACE INTO STATS_SENTI (TICKER,YEAR,HEADER_CNT,HEADER_WORD_CNT,PARA_WORD_CNT,
				NEG_CNT,POS_CNT,CONSTR_CNT,LITI_CNT,UNCERT_CNT,MODAL_STR_CNT,MODAL_MOD_CNT,MODAL_WEA_CNT,TOT_CNT)
				VALUES ('{0}',{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13});
				""".format(key,year,value[0],value[1],value[2],
					years_senti_dict[year][key][0],years_senti_dict[year][key][1],years_senti_dict[year][key][2],
					years_senti_dict[year][key][3],years_senti_dict[year][key][4],years_senti_dict[year][key][5],
					years_senti_dict[year][key][6],years_senti_dict[year][key][7],years_senti_dict[year][key][8]))
	conn.commit()
	conn.close()


def main(args):
	repo_dir = args.dir
	repo_dir = os.path.abspath(repo_dir)

	# Fetching years in repo directory
	years = []
	for dir in glob.glob('{0}/*/'.format(repo_dir)):
		years.append(re.search('/(\d{4})/',dir).group(1))

	years_data_dict = {}
	years_stats_dict = {}
	years_senti_dict = {}
	for year in years:
		# Creating list of header and contents files in directory
		header_dict,para_dict = {},{}
		# Fetching header files as dict
		header_dict = get_files(repo_dir,year,'headers')
		# Fetching paragraph files as dict
		para_dict = get_files(repo_dir,year,'contents')
		# Keeping list of headers and paragraph dicts for each year
		years_data_dict[year] = [header_dict,para_dict]

		# Extracting basic stats for headers and contents
		stats_dict = {}
		# Creating dict with company ticker as key and list of header counts,word counts in headers
		# and word counts in paragraphs as value
		stats_dict = get_stats(header_dict,para_dict)
		# Keeping stats dict for each year
		years_stats_dict[year] = stats_dict

		# Extracting sentiments for each document
		senti_dict = {}
		# Creating dict with company ticker as key and list of sentiment counts as value
		senti_dict = get_sentiments(header_dict,para_dict)
		# Keeping sentiment dicts for each year
		years_senti_dict[year] = senti_dict

	# # Creating list of header and contents files in directory
	# header_dict,para_dict = {},{}
	# # Fetching header files as dict
	# header_dict = get_files(repo_dir,'headers')
	# # Fetching paragraph files as dict
	# para_dict = get_files(repo_dir,'contents')

	# # Extracting basic stats for headers and contents
	# stats_dict = {}
	# # Creating dict with company ticker as key and list of header counts,word counts in headers
	# # and word counts in paragraphs as value
	# stats_dict = get_stats(header_dict,para_dict)

	# Writing entries to sqlite database
	write_db(repo_dir,years_stats_dict,years_senti_dict)

if __name__ == '__main__':
	main(args)