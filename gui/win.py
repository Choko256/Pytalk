#-*- coding:utf-8 -*-

# Main Window Module for PyTALK

from tkinter import *

class PyTalkWindow(Frame):
	def __init__(self, master = None):
		Frame.__init__(self, master)
		self.pack()
		self.create_widgets()
		
	def create_widgets(self):
		self.parent.title = "PyTalk V1.0"
		self.__menubar = Menu(self.parent)
		
