#-*- coding:utf-8 -*-

# Main Window Module for PyTALK

import gtk
from gui import frame

class GUIMainWindow(gtk.Window):
	def __init__(self, config):
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
		self.config = config
		self.set_title("PyTalk V1.0")
		self.resize(640, 480)
		self.set_position(gtk.WIN_POS_CENTER)
	
		self.init_gui()
		# self.show_all()
		
	def init_gui(self):
		self.connect("delete_event", self.__on_window_closing)
		self.connect("destroy", gtk.main_quit)
		self.set_border_width(5)
		
		self.mbar = gtk.MenuBar()
		
		__file_menu = gtk.Menu()
		__file = gtk.MenuItem("File")
		__file.set_submenu(__file_menu)
		
		__config = gtk.MenuItem("Configure...")
		__config.connect("activate", self.open_configure)
		__file_menu.append(__config)
		
		__exit = gtk.MenuItem("Quit")
		__exit.connect("activate", gtk.main_quit)
		__file_menu.append(__exit)
		
		self.mbar.append(__file)
		
		vbox_menu = gtk.VBox(False, 2)
		vbox_menu.pack_start(self.mbar, False, False, 0)
		
		self.add(vbox_menu)
		
	def __on_window_closing(self, widget, event, data = None):
		return False
		
	def open_configure(self, widget):
		cfg = frame.GUIConfigFrame(self, self.config)
		cfg.show_all()		
