import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk,Gdk
import format_toolbar as ft
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
		#save_button.modify_bg(Gtk.StateType.NORMAL,Gdk.Color.parse('#2796BC')[1])
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

		#main Window
		main_window = Gtk.Grid(column_homogeneous=False, column_spacing=5, row_spacing=5)

		





		main_left = Gtk.ScrolledWindow()

		left_window = Gtk.VBox(homogeneous=False)
		left_window.set_size_request(200,400)

		self.store = Gtk.ListStore(str,int)


		self.view = Gtk.TreeView(self.store)
		self.view.set_headers_visible(False)
		self.view.modify_bg(Gtk.StateType.NORMAL,Gdk.Color.parse('#F6F6F5')[1])
		self.view.connect("row_activated",self.show_note)
		self.view.set_activate_on_single_click(True)

		renderer = Gtk.CellRendererText()
		col = Gtk.TreeViewColumn("Notes",renderer,text = 0)
		self.view.append_column(col)

		

		main_left.add(self.view)

		label = Gtk.Label("Notes")
		label.set_size_request(100,100)
		left_window.add(label)
		left_window.add(main_left)

		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_vexpand(True)
		scrolled_window.set_hexpand(True)
		self.textview = Gtk.TextView()
		self.textview.set_wrap_mode(3)
		self.textbuffer = self.textview.get_buffer()

		self.format_toolbar = ft.FormatBar()
		self.title = Gtk.Entry()
		self.title.set_hexpand(True)

		scrolled_window.add(self.textview)

		self.start_database()
		if self.db:
			self.id = max(self.db.keys())
		else:
			self.id = 0

		main_window.attach(left_window,0,0,1,2)
		main_window.attach(scrolled_window, 1, 1, 2, 1)
		main_window.attach(self.format_toolbar,2,0,1,1)
		main_window.attach(self.title,1,0,1,1)

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
			print '123'
			title_limit = len(title)
		if len(title) > 20:
			title_limit = 20
		self.store.append([title[:title_limit],self.id])
		print 'dsa'
		self.db[self.id] = self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),True)
		print self.db
		self.id += 1



	def delete_note(self,button):
		item =  self.view.get_selection().get_selected()[1]
		if item != None:
			del self.db[self.store[item][1]]
			self.store.remove(item)
	
	def start_database(self):
		db = shelve.open("database.db")
		if not db:
			self.db = {}
		else:
			self.db = db['notes']
		for item in self.db:
			title_index = self.db[item].find("\n")
			if title_index < 20 and title_index != -1:
				print title_index
				title = self.db[item][:title_index]
			elif len(self.db[item]) > 20:
				title = self.db[item][:20]
			else:
				title = self.db[item]
			self.store.append([title,item])
		db.close()

	def close_database(self,event):
		db = shelve.open('database.db')
		db['notes'] = self.db
		db.close()
		self.hide()
		Gtk.main_quit()

	def show_note(self,tree_view,path,col):
		self.textbuffer.set_text(self.db[self.store[path][1]])

	def save_note(self,event):
		item =  self.view.get_selection().get_selected()[1]
		self.db[self.store[item][1]] = self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),True)

		

win = MainWindow()
#win.connect("destroy",Gtk.main_quit)
win.show_all()
Gtk.main()