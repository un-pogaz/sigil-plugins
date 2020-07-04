#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, re

# from Common import *

##
## Common
##
reFlag = re.ASCII + re.MULTILINE + re.DOTALL;

def CleanBasic(text):
	
	text = RegexLoop(r"(&#x202F;|&#8239;)", "\u202F", text);
	text = RegexLoop(r"&#xA0;", "&#160;", text);
	text = RegexLoop("\u00A0", "&#160;", text);
	
	
	if ("><p" or "><blockquote") in text :
		text = RegexLoop(r"><(p|div|h\d|li|ul|ol|blockquote)", r">\n<\1", text);
		
	# line
	text = text.replace("\r\n", "\n").replace("\r", "\n");
	text = RegexLoop(r"( |\t)+\n", "\n", text);
	text = RegexLoop("\n\n\n", "\n\n", text);
	
	# entity
	text = RegexLoop("&#38;", "&amp;", text);
	text = RegexLoop("&#60;", "&lt;", text);
	text = RegexLoop("&#62;", "&gt;", text);
	
	text = RegexLoop("(\u00A0|&nbsp;)", r"&#160;", text);
	
	text = RegexLoop("(&mdash;|&#8212;)", "—", text);
	text = RegexLoop("(&ndash;|&#8211;)", "–", text);
	text = RegexLoop("(&laquo;|&#171;)", "«", text);
	text = RegexLoop("(&raquo;|&#187;)", "»", text);
	text = RegexLoop("(&hellip;|&#8230;)", "…", text);
	text = RegexLoop("(&rsquo;|&#8217;)", "’", text);
	
	# xml format
	text = RegexLoop(r"<([^<>]+)\s{2,}([^<>]+)>", r"<\1 \2>", text);
	text = RegexLoop(r"\s+(|/|\?)\s*>", r"\1>", text);
	text = RegexLoop(r"<\s*(|/|!|\?)\s+", r"<\1", text);
	
	text = RegexSimple(r"(&#160;|\s)+</body>", r"\n</body>", text);
	
	# inline vide
	innerSpace = r"<(i|b|em|strong)(| [^>]*)>\s+</\1>";
	innerEmpty = r"<(i|b|em|strong)(| [^>]*)></\1>";
	outerSpace = r"</(i|b|em|strong)(| [^>]*)>\s+<\1(| [^>]*)>";
	outerEmpty = r"</(i|b|em|strong)(| [^>]*)><\1(| [^>]*)>";
	
	while (RegexSearch(innerSpace, text) or
		RegexSearch(innerEmpty, text) or
		RegexSearch(outerSpace, text) or
		RegexSearch(outerEmpty, text)):
		
		text = RegexLoop(innerSpace, r" ", text);
		text = RegexLoop(innerEmpty, r"", text);
		
		text = RegexLoop(outerSpace, r" ", text);
		text = RegexLoop(outerEmpty, r"", text);
	
	# double espace et tab dans paragraphe
	text = RegexLoop(r"(<(p|h\d)(?:| [^>]*)>(?:.(?!</\2>))*?)(\t|( ){2,})", r"\1 ", text);
	# tab pour l'indentation
	text = RegexLoop(r"^( *)\t(\s*<)", r"\1  \2", text);
	
	#strip span
	text = RegexLoop(r"<span\s*>([^<]*)</span>", r"\1", text);
	
	# remplace les triple point invalide
	text = RegexSimple(r"\.\s*\.\s*\.", r"…", text);
	
	# remplace les triple point invalide
	text = RegexLoop(r"<a class=""footnotecall"" id=""bodyftn(\d+)"" href=""#ftn\1"">\1</a>", r"<a class=""footnotecall"" id=""bodyftn\1"" href=""#ftn\1"">[\1]</a>", text);
	
	return text;

def RegexSimple(pattern, repl, string):
	return re.sub(pattern, repl, string, 0, reFlag);

def RegexSearch(pattern, string):
	return re.search(pattern, string, reFlag);

def RegexLoop(pattern, repl, string):
	
	while RegexSearch(pattern, string):
		string = RegexSimple(pattern, repl, string);
	
	return string;
