# Text Analytics on Risk Disclosures

## Folder Descriptions

* **repo :** Contains sample of Form 10-K documents in xbrl format from years 2015 to 2018. The downloaded files are organized in directories with company ticker as the directory names. The _stats.db_ sqlite database contains the calculated basic stats and sentiments for extracted content

* **scripts :** Contains scripts used for downloading Form 10-K documents, and those used for extracting headers and contents for Section 1-A.
	* _download_index.py :_ For downloading all the xbrl file url's based on at start year. The url's are saved in a sqlite database.
	* _download_filings.py :_ For downloading the xbrl form 10-K files by selecting from the sqlite database. The downloaded files are saved with company ticker as directory name.
	* _parse_xbrl.py :_ Reads all xbrl files in input directory and sub-directories, and extracts Section 1-A as html. After writing extracted content to a seperate file, this script then extracts the headers and contents to seperate files in the same directory as each xbrl file. Those files for which extracting Section 1A has failed are copied over to "failed_files" directory.
	* _initial_analysis.py :_ The basic stats of the extracted headers and contents are calculated, and written to a sqlite database.
	* _sentiment_analysis.py :_ This script utilizes the Loughran McDonald financial sentiment word lists and stopwords to find the count of occurrences of words with the following tones : Positive, Negative, Ucertainty, Litigious, Modal and Constraining. The extracted counts and basic stats are written to a sqlite database in _repo_ directory.
	* _distance_metric.py :_ This script calculates the pairwise cosine distance between all pairs of documents. The Document Term matrix is generated after removing stopwords from Loughran Macdonald dictionary and stemming the words. The TF-IDF values are stored in the document term matrix. The cosine distance is then calculated for pairs of documents using the vector of TF-IDF values. The pairwise cosine distance matrix is written to csv file(_cos_sim_matrix.csv_) and also to _stats.db_ sqlite database in _repo_ directory. 

* **failed_files :** Contains files for which extracting Section 1-A has failed. This should serve as reference for improving present extraction logic.
