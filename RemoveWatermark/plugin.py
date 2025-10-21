#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, re

from common import *

# main routine
def run(bk):

    # iterate over all html files
    for html_id, href in bk.text_iter():
        
        print('File being processed: ' + os.path.basename(href))
        # read orignal html code from file
        text = bk.readfile(html_id)
        
        text = Traitement(text)
        
        # write modified html code to file
        bk.writefile(html_id, text)
    
    
    print('')
    print('Watermark removed.')
    
    return 0

## Specifique

def Traitement(text):
    
    #7switch
    text = regex.loop(r'\s*<p(| [^>]*)>[^<]*&lt;[^<]*@[^<]*&gt;</p>\s*<!--[^>]*-->', r'', text)
    
    #Adobe
    text = regex.loop(r'\s*<meta(\s+(name="Adept.expected.resource"|content="urn:uuid:[^"]*")){1,}\s*/>', r'', text)
    
    #Cultura
    text = regex.loop(r'\s*<!--[^>]*&lt;[^>]*@[^>]*&gt;[^>]*-->\s*<!--[^>]*customer[^>]*-->', r'', text)
    text = regex.loop(r'\s*<!--[^>]*customer[^>]*-->', r'', text)
    
    return text

def main():
    print('I reached main when I should not have\n')
    return -1

if __name__ == '__main__':
    sys.exit(main())
