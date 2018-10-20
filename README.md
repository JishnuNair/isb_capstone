# Text Analytics on Risk Disclosures

## Folder Descriptions

* **repo :** Contains sample of Form 10-K documents in xbrl format from years 2015 to 2018. The downloaded files are organized in directories with company ticker as the directory names. The _stats.db_ sqlite database contains the calculated basic stats for extracted content

* **scripts :** Contains scripts used for downloading Form 10-K documents, and those used for extracting headers and contents for Section 1-A.
	* _download_index.py :_ For downloading all the xbrl file url's based on at start year. The url's are saved in a sqlite database
	* _download_filings.py :_ For downloading the xbrl form 10-K files by selecting from the sqlite database. The downloaded files are saved with company ticker as directory name
	* _parse_xbrl.py :_ Reads all xbrl files in input directory and sub-directories, and extracts Section 1-A as html. After writing extracted content to a seperate file, this script then extracts the headers and contents to seperate files in the same directory as each xbrl file. Those files for which extracting Section 1A has failed are copied over to "failed_files" directory
	* _initial_analysis.py :_ The basic stats of the extracted headers and contents are calculated, and written to a sqlite database

* **failed_files :** Contains files for which extracting Section 1-A has failed. This should serve as reference for improving present extraction logic.
