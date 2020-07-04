#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

# target script

import sys
import string
import uuid
import re
import os
import Tkinter
import tkMessageBox

def test(condition, msg):
    if condition:
        print msg, " Passed"
    else:
        print msg, " Failed"
        raise Exception(msg + ' Failed')
    return

def get_meta(str):
    content = ""
	name = ""
	
	res = re.search( r"<meta.*content=\"(.*)\".*name=\"(.*)\".*/>", str)
	if res: 
        content = res.group(1).encode("ascii")
		name = res.group(2).encode("ascii")
    else: 
	    res = re.search( r"<meta.*name=\"(.*)\".*content=\"(.*)\".*/>", str)
		if res:
            content = res.group(2).encode("ascii")
		    name = res.group(1).encode("ascii")
	
	lname = name.lower()
	return {"name" : name, "content" : content, "lname" : lname}
	
def run(bk):
	
	insertSeries = True
    root = Tkinter.Tk()
    root.withdraw()
	
	if tkMessageBox.askyesno("Series", "Insert series elements?"):
        insertSeries = True
	else:
        insertSeries = False	
   	
	bookid = str(uuid.uuid4())
	isbn = ""
    asin = ""
	sernam = ""
	serinx = ""
	
    new_package = "<package xmlns=\"http://www.idpf.org/2007/opf\" unique-identifier=\"BookId\" version=\"2.0\">\n"	
	
	new_xml = ["<metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">"]
    new_xml.append( "<dc:identifier id=\"BookId\" opf:scheme=\"UUID\">"+bookid+"</dc:identifier>" )
			
    old_xml = bk.getmetadataxml().splitlines()

	print "--- Old metadata ---"
    for line in old_xml:
	    copy = True
    	print line
		if re.search( r"<metadata.*>",line):
            copy = False
		if re.search( r"</metadata>", line ):
		    copy = False
		if line[0:6] == "<meta ":
            dict = get_meta( line )
		   
		    if dict["lname"] == "calibre:series":
     		    sernam = dict["content"]
			    copy = False
                insertSeries = True
            elif dict["lname"] == "calibre:series_index":
                serinx = dict["content"]
			    copy = False
	            insertSeries = True
		    else: 
		        cal = dict["lname"]
			    if cal[0:8] == "calibre:":
                    copy = False		   
			   
		sobj = re.search( r"<dc:identifier.*opf:scheme=\"ISBN\".*>(.*)</dc:identifier>", line )
        if sobj:
            isbn = sobj.group(1).encode("ascii")
            copy = False			

		sobj = re.search( r"<dc:identifier.*opf:scheme=\"ASIN\".*>(.*)</dc:identifier>", line )
        if sobj:
            asin = sobj.group(1).encode("ascii")
            copy = False		
			
		if re.search( r"<dc:identifier.*>", line ):
            copy = False	
			
		if re.search( r"<dc:contributor.*calibre.*>", line ):	
            copy = False
			
		if re.search( r"<dc:type.*>", line ):	
            copy = False

		if re.search( r"<dc:rights.*>", line ):	
            copy = False

		if re.search( r"<dc:date.*>", line ):	
            copy = False

		if re.search( r"<dc:publisher.*>", line ):	
            copy = False

	    if re.search( r"<dc:genre.*>", line ):
            copy = False		

	    if re.search( r"<dc:subject.*>", line ):
            copy = False		
			
		if copy:
            new_xml.append(line)		
		
	if len(isbn) > 0:
      new_xml.append("<dc:identifier opf:scheme=\"ISBN\">"+isbn+"</dc:identifier>")

	if len(asin) > 0:
      new_xml.append("<dc:identifier opf:scheme=\"ISBN\">"+asin+"</dc:identifier>")
	  
	if insertSeries:
	    if len(sernam) == 0:
	        new_xml.append( "<meta content=\"\" name=\"calibre:series\"/>" )
		else:
	        new_xml.append( "<meta content=\""+sernam+"\" name=\"calibre:series\"/>" )
		if len(serinx) == 0:
            new_xml.append( "<meta content=\"\" name=\"calibre:series_index\"/>" )
		else:  
            new_xml.append( "<meta content=\""+serinx+"\" name=\"calibre:series_index\"/>" )
	  
	new_xml.append("</metadata>\n")
		
	print "--- New metadata ---"
	xml = "\n".join(new_xml)
    print xml
	  
    bk.setmetadataxml( xml )	 
    bk.setpackagetag( new_package ) 
	
    # check for invalid MIME types for fonts
	for (id, href, mime) in bk.font_iter():
          
        if href.endswith('ttf') and mime <> "application/x-font-ttf":
            fontdata = bk.readfile(id)
            bk.deletefile(id)
            bk.addfile(id, os.path.basename(href), fontdata, 'application/x-font-ttf')
            print 'MIME type updated: ' + os.path.basename(href)
			
        if href.endswith('otf') and mime <> "application/vnd.ms-opentype":
            fontdata = bk.readfile(id)
            bk.deletefile(id)
            bk.addfile(id, os.path.basename(href), fontdata, 'application/vnd.ms-opentype')
            print 'MIME type updated: ' + os.path.basename(href)

        if href.endswith('ttc') and mime <> "application/x-font-truetype-collection":
            fontdata = bk.readfile(id)
            bk.deletefile(id)
            bk.addfile(id, os.path.basename(href), fontdata, 'application/x-font-truetype-collection')
            print 'MIME type updated: ' + os.path.basename(href)

		if href.endswith('woff') and mime <> "application/font-woff":
            fontdata = bk.readfile(id)
            bk.deletefile(id)
            bk.addfile(id, os.path.basename(href), fontdata, 'application/font-woff')
            print 'MIME type updated: ' + os.path.basename(href)
			
	return 0
 
def main():
    print "I reached main when I should not have\n"
    return -1
    
if __name__ == "__main__":
    sys.exit(main())
