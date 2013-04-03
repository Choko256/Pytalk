#-*- coding:utf-8 -*-

# GUI Frames module

import gtk
import gobject
from lib import irc, core

class GUIConfigMainTabFrame(gtk.Frame):
	def __init__(self, config):
		gtk.Frame.__init__(self)
		self.config = config
		self.set_border_width(3)
		self.init_gui()
		self.show_all()
		
	def init_gui(self):
		hbox = gtk.HBox(False, 2)
		store = gtk.ListStore(gobject.TYPE_STRING, irc.Server)
		
		profile = self.config.get_info()[0]['cfg']
		for srv in profile:
			store.append([srv, profile[srv])
		

class GUIConfigFrame(gtk.Window):
	def __init__(self, parent, config):
		gtk.Window.__init__(self, type=gtk.WINDOW_TOPLEVEL)
		# self.set_parent(parent)
		self.config = config
		self.set_modal(True)
		self.set_title("PyTalk Configuration")
		self.resize(400, 300)
		self.set_transient_for(parent)
		self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		#self.set_resizable(False)
		self.init_gui()
		# self.show_all()
		
	def init_gui(self):
		vbox = gtk.VBox(False, 2)
		hbox = gtk.HBox(True, 3)
		self.tabs = gtk.Notebook()
		self.tabs.set_tab_pos(gtk.POS_TOP)
		
		mpage = GUIConfigMainTabFrame(self.config)
		self.tabs.append_page(mpage, gtk.Label("Servers"))
		
		btn_ok = gtk.Button("OK")
		btn_ok.connect("clicked", self.__on_ok_clicked)
		btn_ok.set_size_request(70, 30)
		
		btn_cancel = gtk.Button("Cancel")
		btn_cancel.connect("clicked", self.__on_cancel_clicked)
		btn_cancel.set_size_request(70, 30)
		
		vbox.pack_start(self.tabs)
		hbox.add(btn_ok)
		hbox.add(btn_cancel)
		halign = gtk.Alignment(1, 0, 0, 0)
		halign.add(hbox)
		vbox.pack_start(halign, False, False, 3)
		
		self.add(vbox)
		
	def __on_ok_clicked(self, widget):
		self.destroy()
		
	def __on_cancel_clicked(self, widget):
		self.destroy()
