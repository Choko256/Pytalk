#-*- coding:utf-8 -*-

# GUI Manager using PyGTK

import pygtk
pygtk.require('2.0')
import gtk

from gui import win

GUIMainWindow = None

class GUIManager:
	@staticmethod
	def create_main_window():
		global GUIMainWindow
		
		if GUIMainWindow is None:
			GUIMainWindow = win.GUIMainWindow()
			GUIMainWindow.show_all()
			
		gtk.main()
