#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, re

from Common import *

# main routine
def run(bk):

	# iterate over all html files
	for html_id, href in bk.text_iter():
		
		print("File being processed: " + os.path.basename(href));
		# read orignal html code from file
		text = bk.readfile(html_id);
		
		text = CleanBasic(text);
		
		text = Traitement(text);
		
		text = CleanBasic(text);
		
		# write modified html code to file
		bk.writefile(html_id, text);
	
	for manifest_id, href, media_type in bk.manifest_iter():
		if ("colorschememapping.xml" in href or 
			"filelist.xml" in href or
			"themedata.xml" in href or
			"themedata.thmx" in href or
			"jacket." in href):
			bk.deletefile(manifest_id);
	
	print("");
	print("MSO Artifact Removal complete.");
	
	return 0

## Specifique

def Traitement(text):
	
	text = regex.loop(r"@font-face\s*\{[^\}>]*\}\s*", "", text);
	
	text = regex.loop(r"<ins[^>]*>(.*?)</ins>", r"\1", text);
	
	text = regex.loop(r"\s*xmlns:v=\"urn:schemas-microsoft-com:vml\"", "", text);
	text = regex.loop(r"\s*xmlns:o=\"urn:schemas-microsoft-com:office:office\"", "", text);
	text = regex.loop(r"\s*xmlns:w=\"urn:schemas-microsoft-com:office:word\"", "", text);
	text = regex.loop(r"\s*xmlns:m=\"http://schemas.microsoft.com/office/2004/12/omml\"", "", text);
	
	text = regex.loop(r"\s(v|o|w|m):[^=>]*=\"[^\">]*\"", "", text);
	
	text = regex.loop(r"\s*<!--\s*\[if[^\]>]*\]>.*?<!\[endif\]\s*-->", "", text);
	text = regex.loop(r"\s*<!--\s*\[if !(vml|supportAnnotations|supportLineBreakNewLine|supportFootnotes)\]\s*-->", "", text);
	
	text = regex.loop(r"\s(vlink|link)=\"[^\">]*\"", "", text);
	
	text = regex.loop(r"\s*<meta( (content=\"Word.Document\"|name=\"ProgId\")){2}/>", "", text);
	
	text = regex.loop(r"\s*<meta( (content=\"Microsoft Word[^\"]*\"|name=\"(Generator|Originator)\")){2}/>", "", text);
	
	text = regex.loop(r"\s*<link( (href=\"[^\"]+.(xml|mso|thmx)\"|rel=\"(File-List|Edit-Time-Data|themeData|colorSchemeMapping)\")){2}/>", "", text);
	
	return text;

def main():
	print("I reached main when I should not have\n");
	return -1;

if __name__ == "__main__":
	sys.exit(main())
