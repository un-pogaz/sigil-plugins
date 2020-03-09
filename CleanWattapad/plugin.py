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
	
	print("");
	print("Wattapad Artifact Removal complete.");
	
	return 0

## Specifique

def Traitement(text):
	
	text = RegexLoop(r"<pre>|</pre>", "", text);
	text = RegexLoop(r"data-p-id=\"[^\"]+\"", "", text);
	text = RegexLoop(r"( )+<p", "<p", text);
	
	text = RegexLoop(r"<span class=\"num-comment\">[^<]+</span>", "", text);
	text = RegexLoop(r"<span class=\"comment-marker (hide-marker |)on-inline-comments-modal\">[^<]+<span[^<]+</span>[^<]+</span>", "", text);
	
	text = RegexLoop(r"( |\n)+</p", r"</p", text);
	text = RegexLoop(r"([^>])&#160;</p", r"\1</p", text);
	
	return text;

def main():
	print("I reached main when I should not have\n");
	return -1;

if __name__ == "__main__":
	sys.exit(main())
