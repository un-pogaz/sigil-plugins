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
    
    for manifest_id, href, media_type in bk.manifest_iter():
        if (
        'kobo.js' in href or
        'kobo-android.js' in href or
        'jquery-2.0.0.min.js' in href or
        'togglenotes23.js' in href
        ):
            bk.deletefile(manifest_id)
    
    print('')
    print('Kepub Artifact Removal complete.')
    
    return 0

## Specifique

def Traitement(text):
    
    text = regex.loop(r'\s*<script[^>]*>[^<]*</script>', '', text)
    text = regex.loop(r'\s*<script[^>]*/>', '', text)
    
    text = regex.loop(r'\s*<!--\s*kobo-style\s*-->', '', text)
    
    text = regex.loop(r'\s*<style[^>]*>\s*.koboSpan\s*\{\s*-webkit-text-combine:\s*inherit;\s*\}\s*</style>', '', text)
    
    text = regex.loop(r'<span\s+class="kobo[Ss]pan\d*"[^>]*>([^<]*)</span>', r'\1', text)
    
    text = regex.loop(r'\s+xmlns:xml="http://www\.w3\.org/XML/1998/namespace"', '', text)
    
    text = regex.loop(r'<(?!html)(\w+)\s+xmlns="http://www\.w3\.org/1999/xhtml"', r'<\1', text)
    text = regex.loop(r'<(?!html)(\w+)(\s*[^>]*?)\s*xmlns="http://www\.w3\.org/1999/xhtml"(\s*[^>]*?)>', r'<\1\2\3>', text)
    text = regex.loop(r'<([^>]*)\s{2,}([^>]*)>', r'<\1 \2>', text)
    
    return text

def main():
    print('I reached main when I should not have\n')
    return -1

if __name__ == '__main__':
    sys.exit(main())
