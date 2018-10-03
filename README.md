# Text Analytics on Risk Disclosures

## Folder Descriptions

* **repo :** Contains sample of Form 10-K documents in xbrl format from years 2015 to 2018. The downloaded files are organized in directories with company ticker as the directory names

* **scripts :** Contains scripts used for downloading Form 10-K documents, and those used for extracting headers and contents for Section 1-A.
	* _download_index.py :_ For downloading all the xbrl file url's based on at start year. The url's are saved in a sqlite database
	* _download_filings.py :_ For downloading the xbrl form 10-K files by selecting from the sqlite database. The downloaded files are saved with company ticker as directory name
	* _parse_xbrl.sh :_ Reads all xbrl files in input directory and sub-directories, and extracts Section 1-A html. After writing extracted content to a seperate file, this script calls the _extract_header_contents_ python script for extracting header and contents.
	* _extract_header_contents.py_ : For each html file passed to this script, the bold sections are extracted as headers, and any content which comes between headers are extracted seperately as paragraph content. The extracted header and contents are saved in separate directories as delimited text files.

* **extracted_filings :** Contains extracted headers and contents as text files, for the document samples in repo directory. The extracted headers and contents text files are organized by year and company ticker.
