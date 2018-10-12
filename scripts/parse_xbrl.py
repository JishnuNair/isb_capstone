import re
import os
import shutil
from glob import glob
from bs4 import BeautifulSoup

def return_files(REPO_DIR):
	files = []
	for dir,_,_ in os.walk(REPO_DIR):
		files.extend(glob(os.path.join(dir,'*.xbrl')))
	return files

def extract_section1a(file):
	print("Processing file : {0}".format(file))
	with open(file,'r') as filein:
		contents = filein.read()
	
	soup = BeautifulSoup(contents,features="lxml")
	href_dict = {'1a' : '', '1b' : ''}
	for a in soup.find_all(['a','A'], href=True):
		if 'RISK FACTORS' in a.get_text().upper():
			href_dict['1a'] = a['href']
		if 'UNRESOLVED STAFF COMMENTS' in a.get_text().upper():
			href_dict['1b'] = a['href']

	extracted = re.findall(r'<[Aa] [Nn][Aa][Mm][Ee]="{0}"(.*)<[Aa] [Nn][Aa][Mm][Ee]="{1}"'.format(href_dict['1a'][1:],href_dict['1b'][1:]), contents, re.DOTALL)
	if len(extracted) == 0:
		print("ERROR : Extraction failed for {0}".format(file))
		shutil.copy2(file,'/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/failed_files')
		return None
	
	extracted = extracted[0]
	file_name = re.sub('.xbrl','_1a.html',file)
	with open(file_name,'w') as fileout:
		fileout.write(extracted)

	return extracted

def extract_headers(extracted,file):
	"""
	Extracting headers by considering headers as those sentences which are either bold or italic
	and greater than or equal to three words
	"""
	headers = []
	soup = BeautifulSoup(extracted,features = "lxml")
	for i in soup.find_all('font',style = lambda x:x and any(font in x.upper() for font in ['ITALIC','BOLD'])):
		if len(re.findall(r'[a-zA-Z]+', i.get_text())) > 3:
			headers.append(i.get_text())

	if len(headers) == 0:
		for i in soup.find_all(['b','i']):
			if len(re.findall(r'[a-zA-Z]+', i.get_text())) >= 3:
				headers.append(i.get_text())

	if len(headers) == 0:
		print("ERROR : Extracting headers for file : {0}".format(file))
	else:
		# Writing headers file
		dir_path = os.path.dirname(os.path.realpath(file))
		file_name = os.path.join(dir_path,'headers')
		with open(file_name,'w') as fileout:
			for idx,header in enumerate(headers):
				fileout.write('HEADER_{0}:\n{1}\n'.format(idx+1,headers[idx]))

	return headers

def return_para(pattern1,pattern2,text):
	match = re.search(r'{0}(.*){1}'.format(pattern1,pattern2),text,re.DOTALL).group(1)
	# Removing tags and new lines
	match = re.sub(r'<[^<>]*>','',match).strip()
	# Removing non breaking space
	match = match.replace('&nbsp;',' ').strip()
	return match

def write_contents(paragraphs,file):
	dir_path = os.path.dirname(os.path.realpath(file))
	file_name = os.path.join(dir_path,'contents')

	# # Writing contents file
	with open(file_name,'w') as fileout:
		for idx,paragraph in enumerate(paragraphs):
			fileout.write('CONTENT_{0}:\n{1}\n'.format(idx+1,paragraphs[idx]))

def main():
	REPO_DIR = '/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/repo'

	files = return_files(REPO_DIR)

	for file in files:
		extracted = extract_section1a(file)
		if extracted is not None:
			# Extracting headers
			headers = []
			headers = extract_headers(extracted,file)
			paragraphs = []
			for idx,header in enumerate(headers):
				try:
					paragraphs.append(return_para(headers[idx],headers[idx+1],extracted))
				except IndexError:
					try:
						paragraphs.append(return_para(headers[idx],'.',extracted))
					except:
						paragraphs.append('')
				except :
					paragraphs.append('')
			write_contents(paragraphs,file)
		else:
			continue

if __name__ == '__main__':
	main()

