import argparse
import glob
import os
import re
import sqlite3
from nltk.stem import PorterStemmer

"""
This python script is to get the various initial risk statistics for the risk factors mentioned 
in 10-K documents for each organization. 
The initial metrics are the following:
	* Number of risk titles
	* Number of words in each risk title
	* Number of words in paragraphs under each title

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

def write_db(repo_dir,years_stats_dict):
	# Creating/Connecting sqlite database
	conn = sqlite3.connect('{0}/stats.db'.format(repo_dir))
	# Creating table if not exists
	conn.execute("""CREATE TABLE IF NOT EXISTS INITIAL_STATS
		(TICKER CHAR(25) NOT  NULL,
		 YEAR INT NOT NULL,
		 HEADER_CNT INT NOT NULL,
		 HEADER_WORD_CNT INT NOT NULL,
		 PARA_WORD_CNT INT NOT NULL,
		 PRIMARY KEY (TICKER,YEAR)
		);	
		""")
	# Inserting records
	for year,stats_dict in years_stats_dict.items():
		for key,value in stats_dict.items():
			print("INSERTING {0},{1},{2},{3},{4}".format(key,year,value[0],value[1],value[2]))
			conn.execute("""INSERT OR REPLACE INTO INITIAL_STATS (TICKER,YEAR,HEADER_CNT,HEADER_WORD_CNT,PARA_WORD_CNT)
				VALUES ('{0}',{1},{2},{3},{4});
				""".format(key,year,value[0],value[1],value[2]))
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
	write_db(repo_dir,years_stats_dict)

if __name__ == '__main__':
	main(args)