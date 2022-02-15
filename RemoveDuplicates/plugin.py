#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, uuid;
from common import regex;



# main routine
def run(bk):
    print('Python Laucher Version:', bk.launcher_version())
    if bk.launcher_version() < 20151024:    #Check Sigil version is greater than 0.9.0....
        print("You need to use Sigil 0.9.1 or greater for this plugin")
        print('\n\nPlease click OK to close the Plugin Runner window.')
        return 0        #....and return if Sigil  is not greater than 0.9.0
    
    
    prefs = bk.getPrefs()        # Get preferences from json file
    
    ShowMainWindow(bk,prefs)            #show the main window
    
    print('\n\nPlease click OK to close the Plugin Runner window.')
    
    return 0        #0 - means success, anything else means failure

def ShowMainWindow(bk, prefs):
    """
    This function is called automatically by the main function
    This function displays the main window showing a listbox containing the html files in the ePub file.
    Files selected in Sigil are highlighted in this listbox.
    It contains buttons to enable the user to run required processes.
    After building the window with its widgets, centerWindow() is called to centre this window
    """
    
    root = Tk()
    root.withdraw()    #Hide window to avoid flashing when it is moved to the correct position

    prefs['DictFile']=GetDictPath()

    root.title("Epub tidy")
    mainframe = ttk.Frame(root, padding="15 15 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    ttk.Label(mainframe, text="Select parts to process").grid(column=0, row=0, sticky=W)
    ttk.Label(mainframe, text="Options").grid(column=3, row=1, sticky=W)
    
    optionFrame=ttk.Frame(mainframe,padding="5 5 5 5")
    optionFrame.grid(column=3, row=1, sticky=(N, W, E, S))

    lbox = Listbox(mainframe, height=15, width=50, selectmode=EXTENDED, exportselection=0)
    lbox.grid(column=0, row=1, sticky=(N,S,E,W))
    scroller = ttk.Scrollbar(mainframe, orient=VERTICAL, command=lbox.yview)
    scroller.grid(column=1, row=1, sticky=(N,S,W))
    lbox.configure(yscrollcommand=scroller.set)

    for (id, href) in bk.text_iter():                #For each html file in the 'text' section of the ePub
        lbox.insert(END, href)                        #Append the HTML file name to the list box

    for (id_type, id) in bk.selected_iter():        #Get files selected in Sigil
        if id_type == "manifest":
            href = bk.id_to_href(id, ow=None)
            mime = bk.id_to_mime(id, ow=None)
            if mime == "application/xhtml+xml":        #and if they are of type application/xhtml+xml
                i = lbox.get(0, END).index(href)    #get their index in the listbox
                lbox.selection_set(i)                #and highlight the name in the listbox

    chkJoinParagraphs = StringVar()
    chkReplaceHTMLCode = StringVar()
    chkProcessItalics = StringVar()
    chkProcessSpanTags = StringVar()
    chkDoManualCheck =  StringVar() 
    chkGreek = StringVar() 
    chkUseCSSFile =  StringVar()
    chkUseCSSFile =  StringVar()
    chkUseHunspellDict =  StringVar()
    
    chkJoinParagraphs.set(prefs['JoinParagraphs'])
    chkReplaceHTMLCode.set(prefs['ReplaceHTMLCode'])
    chkProcessItalics.set(prefs['ProcessItalics'])
    chkProcessSpanTags.set(prefs['ProcessSpanTags'])
    chkDoManualCheck.set(prefs['DoManualCheck']) 
    chkGreek.set(prefs['GreekLetters']) 
    chkUseCSSFile.set(prefs['UseCSSFile'])
    chkUseHunspellDict.set(prefs['useHunspellDict'])

    check = ttk.Checkbutton(optionFrame, text='Fix ALL broken line endings', 
        variable=chkJoinParagraphs,
        onvalue='Yes', offvalue='No').grid(column=3, row=1, sticky=W)

    check = ttk.Checkbutton(optionFrame, text='Replace HTML code eg &mdash;',
        variable=chkReplaceHTMLCode,
        onvalue='Yes', offvalue='No').grid(column=3, row=2, sticky=W)

    check = ttk.Checkbutton(optionFrame, text='Process italics', 
        variable=chkProcessItalics,
        onvalue='Yes', offvalue='No').grid(column=3, row=3, sticky=W)

    check = ttk.Checkbutton(optionFrame, text='Process span tags', 
        variable=chkProcessSpanTags,
        onvalue='Yes', offvalue='No').grid(column=3, row=4, sticky=W)

    check = ttk.Checkbutton(optionFrame, text='Do manual word check',  
        variable=chkDoManualCheck,
        onvalue='Yes', offvalue='No').grid(column=3, row=5, sticky=W)


    check = ttk.Checkbutton(optionFrame, text='Insert CSS file',  
        variable=chkUseCSSFile,
        onvalue='Yes', offvalue='No').grid(column=3, row=6, sticky=W)


    check = ttk.Checkbutton(optionFrame, text='Process Greek characters only', 
        variable=chkGreek,
        onvalue='Yes', offvalue='No').grid(column=3, row=7, sticky=W)

    ttk.Label(optionFrame, text="").grid(column=3, row=8, sticky=W,) #Blank row    
    
    check = ttk.Checkbutton(optionFrame, text='Use in-built dictionary', 
        variable=chkUseHunspellDict, command=lambda: chkUseHunspellChanged(chkUseHunspellDict,cbLanguages),
        onvalue='Yes', offvalue='No').grid(column=3, row=9, sticky=W)
        
    cbDictChoices=("English (UK)", "English (USA)", "French", "German", "Greek*", "Spanish")
    cbLanguages=ttk.Combobox(optionFrame, state="readonly", values=cbDictChoices,exportselection=0, width=35)
    cbLanguages.grid(column=3, row=10, sticky=W)
    cbLanguages.set(prefs['HunspellLanguage'])                    #Set language dictionary to use
    chkUseHunspellChanged(chkUseHunspellDict,cbLanguages)        #Set initial text in language combobox
        
    ttk.Label(optionFrame, text="").grid(column=3, row=20, sticky=W,) #Blank row    

    ttk.Button(optionFrame, text='Process header tags', command=lambda: GetHeaderTagOptions(root,  bk), width=30).grid(column=3, row=30, sticky=W)
    ttk.Button(optionFrame, text="Options for chapter titles", command=lambda: GetChapterOptions(root), width=30).grid(column=3, row=40, sticky=W)
    ttk.Button(optionFrame, text='Select files', command=lambda: getFileNames(root, prefs), width=30).grid(column=3, row=50, sticky=W)
    ttk.Button(mainframe, text='Resize image', command=lambda: showImageDialog(root,  bk)).grid(column=4, row=30, sticky=W)
    ttk.Button(mainframe, text="Process text", command=lambda: Go(root, lbox, bk, prefs)).grid(column=3, row=30, sticky=W)
    ttk.Button(mainframe, text="Close", command=root.quit).grid(column=0, row=30, sticky=W)
    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5) 
    GenUtils.centerWindow(root)        #Centre main window and show it
    root.mainloop()
    return ()


def main():
    print("I reached main when I should not have\n");
    return -1;

if __name__ == "__main__":
    sys.exit(main())