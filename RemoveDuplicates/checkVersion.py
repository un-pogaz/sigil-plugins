#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This module contains a function, checkForUpdate(), that checks to see whether the latest version of
a Sigil plugin is installed by comparing the version number of the published plugin from the
webpage on which it is published with the version number of the installed plugin.

The function uses the Python interface provided with Sigil and therefore will work with Sigil
version 0.92 or higher.

The function takes two parameters:
url - this is the webpage that contains the plugin
searchPattern - this is the pattern that must be used to extract the version number from the zip file.

Example of use:

    searchPattern = r"ePubTidyTool_v(.*?).zip"
    url = "http://www.mobileread.com/forums/showthread.php?t=264378"
    
    checkForUpdate(url, searchPattern)
    
In this example ONE set of brackets is placed around the version number of the plugin.
The contents of the brackets are used to identify the published version of the plugin.
'''

from sigil_bs4 import BeautifulSoup
import re
import urllib.request as urlRead
import os, inspect	#needed to determine the plugin path

def checkForUpdate(url, searchPattern):
    PublishedVersion=None
    InstalledVersion = None

    try:
        r = urlRead.urlopen(url).read() #read the webpage named  in the parameter url
    except:
        print('Could not access ', url)
        return

    soup = BeautifulSoup(r, 'html.parser')
    soup.prettify() #I think this converts text to UTF-8????
    urltext=soup.get_text() #Get the text on the webpage
    
    m=re.search(searchPattern, urltext) #Search for the plugin and
    PublishedVersion=m.group(1)         #get its version number
    try:        
        #Get the path for the installed plugin
        pluginPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        pluginFile = os.path.join(pluginPath, 'plugin.xml')
    except:
        print('Cannot find the XML file for the plugin')
        return

    try:
        f=open(pluginFile, 'r', encoding='utf-8')               #Open the XML plugin file
    except IOError:
        print('Error opening the plugin file')
    else:
        xmlData=f.read()                                        #read the XML plugin file
        m=re.search(r'<version>([^<]*)</version>', xmlData)     #and search for the version number
        installedVersion=m.group(1)                             #store the version number
        f.close                                                 #and close the XML file
        
        print('Published version ', PublishedVersion)           #print version numbers of the published and
        print('Installed version ', installedVersion)           #installed plugins
        
        if installedVersion == PublishedVersion:                #compare the plugins 
            print('You have the latest version of this plugin')
        else:
            print('An update for this plugin is available at ',url)
                
def run(bk):

    searchPattern = r'ePubTidyTool_v(.*?).zip'
    url = 'http://www.mobileread.com/forums/showthread.php?t=264378'
    checkForUpdate(url, searchPattern)

    return 0						#0 - means success, anything else means failure
 
def main():
    print ('I reached main when I should not have\n')
    return -1
    
if __name__ == '__main__':
    sys.exit(main())
