#-*- coding:utf-8 -*-

# Main Window Module for PyTALK

import gtk

class GUIMainWindow(gtk.Window):
	def __init__(self):
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
		self.set_title("PyTalk V1.0")
		self.resize(640, 480)
		self.set_position(gtk.WIN_POS_CENTER)
