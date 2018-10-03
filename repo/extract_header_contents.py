import unicodedata
import re
import os
import pathlib
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f","--file",help="Full path of extracted xbrl file",required=True)
parser.add_argument("-o","--outdir",help="Directory path for storing extracted content",required=True)
args = parser.parse_args()

def extract_headers(contents):
	# To extract headers
	soup = BeautifulSoup(contents,"html.parser")
	headers = []
	for item in soup.findAll("b"):
		headers.append(item.get_text())
	headers = [item.strip() for item in headers]
	return headers

def return_para(pattern1,pattern2,text):
	match = re.search(r'{0}(.*){1}'.format(pattern1,pattern2),text,re.DOTALL).group(1)
	# Removing tags and new lines
	match = re.sub(r'<[^<>]*>','',match).strip()
	# Removing non breaking space
	match = match.replace('&nbsp;',' ').strip()
	return match

def extract_contents(headers,contents,dir_path):
	# paragraphs = []
	# for idx,header in enumerate(headers):
	# 	try:
	# 		paragraphs.append(return_para(headers[idx],headers[idx+1],contents))
	# 	except IndexError:
	# 		try:
	# 			paragraphs.append(return_para(headers[idx],'.',contents))
	# 		except:
	# 			paragraphs.append('')
	# 	except :
	# 		paragraphs.append('')
	content_file = '{0}/contents'.format(dir_path)
	soup = BeautifulSoup(contents,"html.parser")
	items = soup.findAll("p")
	with open(content_file,'w') as fileout:
		count = 1
		for idx,item in enumerate(items):
			if any(header in str(item) for header in headers):
				fileout.write("\nCONTENT_{0}:\n".format(count))
				count = count + 1
			else:
				fileout.write(str(item))


def write_headers_contents(headers,dir_path):
	header_file = '{0}/headers'.format(dir_path)
	#content_file = '{0}/contents'.format(dir_path)

	# Writing headers file
	with open(header_file,'w') as fileout:
		for idx,header in enumerate(headers):
			fileout.write('HEADER_{0}:\n{1}\n'.format(idx+1,headers[idx]))

	# # Writing contents file
	# with open(content_file,'w') as fileout:
	# 	for idx,paragraph in enumerate(paragraphs):
	# 		fileout.write('CONTENT_{0}:\n{1}\n'.format(idx+1,paragraphs[idx]))

def main(args):
	# Setting up directory for writing files
	dir_path = os.path.dirname(os.path.realpath(args.file))
	sub_dir = re.search('/(\d{4}/\d{4})',dir_path).group(1)
	dir_path = os.path.join(args.outdir,sub_dir)

	# Creating directory if it does not exist
	if not os.path.exists(dir_path):
		pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)

	with open(args.file,'r') as filein:
		contents = filein.read()

	# Using normal form of unicode string
	contents = unicodedata.normalize("NFKD",contents)

	# Extracting headers
	headers = extract_headers(contents)
	headers = [item for item in headers if item != '']

	# Extracting contents under each header
	paragraphs = extract_contents(headers,contents,dir_path)
	# paragraphs = []

	# Writing headers and contents to local files
	write_headers_contents(headers,dir_path)

if __name__ == '__main__':
	main(args)




	
