#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module will resize an image in an ePub book. PILlow must be installed to use it.

This module tries to import Image and ImageTk from PIL. If it fails then the class for resizing
an image is not set up and the global importPILFlag is set to False. External modules can test this
flag to check whether the class dlgImage has been set up for use.

"""

global importPILFlag	#test this flag to check whether PIL loaded before using the class dlgImage

import tkinter as tk				#Essential for custom dialog box using tk. commands
import tkinter.ttk as tkinter_ttk	#Essential for ttk. commands
from tkinter import *				#Essential for root = Tk()
from tkinter import messagebox as tkMessageBox		#Essential for messagebox
import glob							#Needed for deleting files using wildcards
import os, inspect 					#needed to get plugin path
import GenUtils						#Need centerWindow()
from sys import platform as _platform	#Used to determine Operating system in use
from io import BytesIO				#Needed to convert the image data returned by bk.readfile()

#Import module for relevant OS to make MakeBeep() platform dependent
if _platform == "linux" or _platform == "linux2":
	import os   #Need to install sox
elif _platform == "darwin":
	pass # no need to import a sound - use default system beep
elif _platform == "win32":
	import winsound

def MakeBeep(frequency, duration):
	"""
	Produces a 'beep' with specified frequency and duration.
	Frequency is in Hz, duration in milliseconds
	"""
	if _platform == "linux" or _platform == "linux2":
		duration=int(duration / 1000) + (duration % 1000 > 0) #rounds duration up to nearest second for Linux
		os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, frequency))
	elif _platform == "darwin":
		os.system('afplay /System/Library/Sounds/Sosumi.aiff')
	elif _platform == "win32":
		winsound.Beep(frequency, duration)

try:
	from PIL import Image, ImageTk
except ImportError:
	print("Cannot import PIL library")
	importPILFlag=False
	print()
else:   #This code runs if the exception is not called and the class is set up
	importPILFlag=True

	class dlgImage: #class is only set up if the PIL is imported
		importPILFlag=False
		dlgTop=""
		def __init__(self):
			pass
		def ShowDialogBox(self, parent,bk):
			"""
			Called by an external module.
			Parent is the window that owns this dialog.
			bk is the parameter used in the Sigiil run(bk) function.
			"""
			self.top = tk.Toplevel(parent)
			dlgImage.dlgTop=self.top 		#Needed for external program to destroy the dialog window
			self.bk1=bk						#initialise internal variable
			self.pictureDict={}				#Clear dictionary to hold href and corresponding id for pictures
			self.imageResized=False			#Initialise flag for resizing image
											#Set to True onlly if an image is selected for changing
			self.requiredWidth = 480		#Required default width of image in pixels

			self.plugin_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

			self.top.grab_set() 				#Make dialog box modal
			self.top.title("Adjust image size") #Title for dialog box
			self.dlgframe = ttk.Frame(self.top, padding="15 15 12 12")
			self.dlgframe.grid(column=0, row=0, sticky=(N, W, E, S))
			self.dlgframe.columnconfigure(0, weight=1)
			self.dlgframe.rowconfigure(0, weight=1)

			self.CanvasFrame=ttk.Frame(self.dlgframe, padding="5 5 5 5", relief=SUNKEN)
			self.CanvasFrame.grid(column=1, row=0, sticky=(N, W, E, S))
			self.CanvasFrame.columnconfigure(0, weight=1, minsize=500)
			self.CanvasFrame.rowconfigure(0, weight=1, minsize=600)
        
			hScroller = tk.Scrollbar(self.CanvasFrame, orient=HORIZONTAL)
			hScroller.grid(column=0, row=1, columnspan=2, sticky=(N,E, S,W))
			vScroller = tk.Scrollbar(self.CanvasFrame, orient=VERTICAL)    
			vScroller.grid(column=1, row=0, sticky=(N,E,S,W))   
        
			self.canvas = Canvas(self.CanvasFrame, scrollregion=(0, 0, 1000, 1000), yscrollcommand=vScroller.set, xscrollcommand=hScroller.set)
			hScroller['command'] = self.canvas.xview
			vScroller['command'] = self.canvas.yview
			self.canvas.grid(column=0, row=0, sticky=(N,W,E,S))

			LeftFrame=ttk.Frame(self.dlgframe,padding="5 5 5 5", relief=SUNKEN)
			LeftFrame.grid(column=0, row=0, sticky=(N, W, E, S))

			tk.Label(LeftFrame, text="Select picture to process").grid(column=0, row=0, sticky=W)

			lbox = Listbox(LeftFrame, height=20, width=50, selectmode=SINGLE, exportselection=0)
			lbox.grid(column=0, columnspan=3, row=1, sticky=(N,S,E,W))
			scroller = ttk.Scrollbar(LeftFrame, orient=VERTICAL, command=lbox.yview)
			scroller.grid(column=3, row=1, sticky=(N,S,W))
			lbox.configure(yscrollcommand=scroller.set)
			#lbox.bind("<Double-Button-1>", self.pictureChosen)	#Calls pictureChosen() when user double clicks a list box item
			lbox.bind('<<ListboxSelect>>',self.pictureChosen)	#May want to offer the option of single click to select image to rezize?

			for (id, href, mime) in self.bk1.image_iter():
				lbox.insert(END, href)					#Append the image file name to the list box
				self.pictureDict[href] = id				#Store ids with picture name

			tk.Label(LeftFrame, text="").grid(column=0, row=2, sticky=W)	#Blank row

			tk.Label(LeftFrame, text="Image width in pixels:").grid(column=0, row=3, sticky=W)

			self.txtSize = StringVar()
			self.txtSize.set(self.requiredWidth)
			txtImgSize = Entry(LeftFrame, exportselection=False, textvariable=self.txtSize, width = 10)
			txtImgSize.grid(column=1, row=3, pady=10, sticky=EW)
			self.txtSize.trace('w', lambda nm, idx, mode, var=self.txtSize: validateInteger(var))

			tk.Button(LeftFrame, text="Show resized image", command=self.getPicture, width = 20).grid(column=1, row=4, ipadx=5, ipady=5, padx=5, pady=10,  sticky=W)

			tk.Label(LeftFrame, text="").grid(column=0, row=6, sticky=W)	#Blank row

			tk.Button(LeftFrame, text="OK", command=self.OK, width = 10).grid(column=0, row=7, sticky=E)
			tk.Button(LeftFrame, text="Cancel", command=self.Cancel, width = 10).grid(column=1, row=7, sticky=W)

			GenUtils.centerWindow(self.top)

			self.currentValue = self.requiredWidth

			def validateInteger(var):
				new_value = var.get()
				try:
					new_value == '' or int(new_value)
					self.currentValue = new_value
					return (self.currentValue)
				except:
					var.set(self.currentValue)
					MakeBeep(1200,300)

		def getPicture(self):
			"""
			This method is called by pictureChosen()
			It gets the selected picture and save it to disc; 
			If saved to disc successfully, it calls resizeImage()  
			"""

			bkImage = self.bk1.readfile(self.pictureDict[self.pictureName])	#Look up ID for picture name in dictionary and read into bkImage
			self.img = Image.open(BytesIO(bkImage))
			self.requiredWidth=int(self.txtSize.get())	#Get image size from textbox and convert to integer
			if self.requiredWidth>1000:
				self.requiredWidth=1000
			incrementalFactor = (self.requiredWidth / float(self.img.size[0])) #calculate percentage increase in width
			newHeight = int((float(self.img.size[1]) * float(incrementalFactor)))	#Calculate new height
			self.img = self.img.resize((self.requiredWidth, newHeight),Image.ANTIALIAS)	#Resize image
			self.photo = ImageTk.PhotoImage(self.img)
			canvasImageId = self.canvas.create_image(0, 0, anchor=NW, image=self.photo)
			self.imageResized=True

		def pictureChosen(self, event):
			#This method is called when the user clicks the name of a picture in the list box
			widget = event.widget	#widget references the widget that sent the (click) event; saves using self.lbox
			selectedPicture=widget.curselection()				#get index number of selected picture in listbox
			self.pictureName = widget.get(selectedPicture[0])	#get text for selected picture in listbox
			self.getPicture()  

		def OKPressed(self, event):
			self.OK()

		def EscapePressed(self, event):
			self.Cancel()
			
		def Cancel(self):
			"""
			Called when the user clicks the "Cancle" button
			"""
			self.top.destroy()
	
		def OK(self):
			"""
			Called when the user clicks the "OK" button
			This uses the flag self.imageResized to check whether the image has been resized successfuly.
			If so, it writes the resized window to the ePub book and then destroys the Adjust image size dialog
			If not, it shows a warning message
			"""
			if not self.imageResized:
				tkMessageBox.showerror(title='WARNING', message='You must select an image from the list\nor press Cancel', icon='warning')
				return

			dotPos=self.pictureName.rfind('.')		#Find the position of the dot in the filename
			dotPos= dotPos-len(self.pictureName)+1	#Calculate the position of the dot from the left hand side
			fileExtn=self.pictureName[dotPos:]	#and get the filename extension
			if fileExtn=="jpg": fileExtn="jpeg"
			b = BytesIO()
			self.img.save(b, fileExtn) #jpeg and jpg are interchangeable, can't write jpg!
			self.pictureData = b.getvalue()

			self.bk1.writefile(self.pictureDict[self.pictureName], self.pictureData)	#writes to image ID'd in dictionary
			self.top.destroy()
