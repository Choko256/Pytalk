#-*- coding:utf-8 -*-

# GUI Frames module

import gtk

class GUIConfigMainTabFrame(gtk.Frame):
	def __init__(self):
		gtk.Frame.__init__(self, "MainConfigTab")
		self.set_border_width(8)
		self.show()

class GUIConfigFrame(gtk.Window):
	def __init__(self, parent):
		gtk.Window.__init__(self, type=gtk.WINDOW_TOPLEVEL)
		# self.set_parent(parent)
		self.set_modal(True)
		self.set_title("PyTalk Configuration")
		self.set_position(gtk.WIN_POS_CENTER)
		self.resize(400, 300)
		self.set_transient_for(parent)
		self.set_resizable(False)
		self.init_gui()
		
	def init_gui(self):
		self.tabs = gtk.Notebook()
		self.tabs.set_tab_pos(gtk.POS_TOP)
		
		mpage = GUIConfigMainTabFrame()
		self.tabs.append_page(mpage, gtk.Label("Main"))
		self.show_all()
