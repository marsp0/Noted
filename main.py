import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk,Gdk
import format_toolbar as ft
import sidebar as sb
import shelve

class MainWindow(Gtk.Window):

	def __init__(self):
		Gtk.Window.__init__(self, title="Noted")
		self.set_border_width(5)
		self.set_size_request(1000, 800)
		
		#Header Bar
		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.connect("destroy",self.close_database)
		hb.props.title = "Noted"
		self.set_titlebar(hb)
		
		box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		Gtk.StyleContext.add_class(box.get_style_context(), "linked")

		save_button = Gtk.Button.new_with_label("Save")
		save_button.connect("clicked",self.save_note)

		hb.pack_end(save_button)

		#Create Button
		create_button = Gtk.Button.new_with_label("New")
		create_button.connect("clicked",self.create_note)
		box.add(create_button)

		#Delete Button
		delete_button = Gtk.Button.new_with_label("Delete")
		delete_button.connect("clicked",self.delete_note)
		box.add(delete_button)

		hb.pack_start(box)

		# MAIN WINDOW
		main_window = Gtk.Grid(column_homogeneous=False, column_spacing=5, row_spacing=5)

		self.sidebar = sb.Sidebar()
		self.sidebar.view.connect("row_activated",self.show_note)

		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_vexpand(True)
		scrolled_window.set_hexpand(True)
		self.textview = Gtk.TextView()
		self.textview.set_wrap_mode(3)
		self.textview.set_bottom_margin(5)
		self.textview.set_top_margin(5)
		self.textview.set_left_margin(5)
		self.textview.set_right_margin(5)
		self.textbuffer = self.textview.get_buffer()

		self.format_toolbar = ft.FormatBar()
		self.tag_bar = Gtk.Entry()
		self.tag_bar.set_placeholder_text("Tags")
		self.tag_bar.set_hexpand(True)

		scrolled_window.add(self.textview)

		self.start_database()
		if self.db:
			self.id = max(self.db.keys())+1
		else:
			self.id = 0

		#label = Gtk.Label("Notes")
		#main_window.attach(label,0,0,1,1)

		#main_window.attach(left_window,0,0,1,2)
		main_window.attach(self.sidebar,0,0,1,2)
		main_window.attach(scrolled_window, 1, 0, 2, 1)
		main_window.attach(self.format_toolbar,2,1,1,1)
		main_window.attach(self.tag_bar,1,1,1,1)

		self.add(main_window)
	
	def create_note(self,button):
		#limit of chars for the title of the note
		title_limit = -2
		#get the actual title
		title = self.textbuffer.get_text(self.textbuffer.get_start_iter(), self.textbuffer.get_iter_at_line(1), False)
		#if title is empty then it means that there is only 1 line of note
		if title == '':
			title = self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),False)
			if title == '':
				return
			title_limit = len(title)
		if len(title) > 20:
			title_limit = 20
		self.sidebar.add_item(title,self.id)
		self.db[self.id] = self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),True)
		self.id += 1

	def delete_note(self,button):
		item = self.sidebar.remove_item()
		if item != None:
			del self.db[item]
	
	def start_database(self):
		db = shelve.open("database.db")
		if not db:
			self.db = {}
		else:
			self.db = db['notes']
		for item in self.db:
			title_index = self.db[item].find("\n")
			if title_index < 20 and title_index != -1:
				title = self.db[item][:title_index]
			elif len(self.db[item]) > 20:
				title = self.db[item][:20]
			else:
				title = self.db[item]
			self.sidebar.add_item(title,item)
		db.close()

	def close_database(self,event):
		db = shelve.open('database.db')
		db['notes'] = self.db
		db.close()
		self.hide()
		Gtk.main_quit()

	def show_note(self,tree_view,path,col):
		item = self.sidebar.get_item(path)
		self.textbuffer.set_text(self.db[item])

	def save_note(self,event):
		path =  self.sidebar.get_selected()
		self.db[self.sidebar.get_item(path)] = self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),True)

		

win = MainWindow()
#win.connect("destroy",Gtk.main_quit)
win.show_all()
Gtk.main()