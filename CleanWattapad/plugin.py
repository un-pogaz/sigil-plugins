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
	
	text = regex.loop(r"<pre>|</pre>", "", text);
	text = regex.loop(r"data-p-id=\"[^\"]+\"", "", text);
	text = regex.loop(r"( )+<p", "<p", text);
	
	text = regex.loop(r"<span class=\"num-comment\">[^<]+</span>", "", text);
	text = regex.loop(r"<span class=\"comment-marker (hide-marker |)on-inline-comments-modal\">[^<]+<span[^<]+</span>[^<]+</span>", "", text);
	
	text = regex.loop(r"( |\n)+</p", r"</p", text);
	text = regex.loop(r"([^>])&#160;\s*</p", r"\1</p", text);
	text = regex.loop(r"<br>", r"<br/>", text);
	
	return text;

def main():
	print("I reached main when I should not have\n");
	return -1;

if __name__ == "__main__":
	sys.exit(main())
