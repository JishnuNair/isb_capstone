#!/bin/bash
repo='/media/jishnu/prasath/ISB/repo/filings'
outdir='/media/jishnu/prasath/ISB/repo/extracted_filings/'
extract_header_contents='/home/jishnu/Documents/ISB/Term3/capstone/repo/parse_xbrl/extract_header_contents.py'
# Iterate over subdirectories
#for d in $(find $repo -maxdepth 1 -type d); do
#	find $d -type f -name "*.xbrl" -maxdepth 1
#done

for xbrl_file in $(find "$repo" -type f -name "*.xbrl")
do
	echo $xbrl_file
	# Replacing instances where "ITEM" and "1A" or "1B" or "2" are in separate lines
	sed -i ':begin;$!N;s/ITEM\n1A/ITEM 1A/;tbegin;P;D' "$xbrl_file"
	sed -i ':begin;$!N;s/ITEM\n1B/ITEM 1B/;tbegin;P;D' "$xbrl_file"
	sed -i ':begin;$!N;s/ITEM\n2/ITEM 2/;tbegin;P;D' "$xbrl_file"
	# To extract Item 1A
	sed -n '/ITEM 1A/,/\(ITEM 1B\|ITEM 2\)/p;' "$xbrl_file" > "${xbrl_file}.extracted.html"
	# Remove first and last line
	sed -i '1d;$d' "${xbrl_file}.extracted.html"
	# Remove all lines upto first header
	sed -i -n '/<[Bb]>/,$p' "${xbrl_file}.extracted.html"
	# Extracting header and contents
	python $extract_header_contents -f "${xbrl_file}.extracted.html" -o "$outdir"
done
