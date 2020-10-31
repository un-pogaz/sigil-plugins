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
		
		text = Traitement(text);
		
		# write modified html code to file
		bk.writefile(html_id, text);
	
	
	print("");
	print("Watermark removed.");
	
	return 0

## Specifique

def Traitement(text):
	
	#7switch
	text = RegexLoop(r'\s*<p(| [^>]*)>[^<]*&lt;[^<]*@[^<]*&gt;</p>\s*<!--[^>]*-->', r'', text);
	
	#Adobe
	text = RegexLoop(r'\s*<meta(\s+(name="Adept.expected.resource"|content="urn:uuid:[^"]*")){1,}\s*/>', r'', text);
	
	#Cultura
	text = RegexLoop(r'\s*<!--[^>]*&lt;[^>]*@[^>]*&gt;[^>]*-->\s*<!--[^>]*customer[^>]*-->', r'', text);
	text = RegexLoop(r'\s*<!--[^>]*customer[^>]*-->', r'', text);
	
	return text;

def main():
	print("I reached main when I should not have\n");
	return -1;

if __name__ == "__main__":
	sys.exit(main())
