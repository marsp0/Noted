import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk,Gdk
import format_toolbar as ft
import sidebar as sb
import editor
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

		#Create Button
		create_button = Gtk.Button()
		create_button.connect("clicked",self.create_note)
		create_button.props.relief = Gtk.ReliefStyle(0)
		image = Gtk.Image.new_from_icon_name("document-new", Gtk.IconSize.DND)
		image.set_tooltip_text("New (Ctrl+N)")
		image.show()
		create_button.add(image)
		box.add(create_button)

		#save button
		save_button = Gtk.Button()
		save_button.connect("clicked",self.save_note)
		save_button.props.relief = Gtk.ReliefStyle(0)

		image = Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.DND)
		image.set_tooltip_text("Save (Ctrl+S)")
		image.show()
		save_button.add(image)
		box.add(save_button)

		#Delete Button
		delete_button = Gtk.Button()
		delete_button.connect("clicked",self.delete_note)
		delete_button.props.relief = Gtk.ReliefStyle(0)
		image = Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.DND)
		image.set_tooltip_text("Delete")
		image.show()
		delete_button.add(image)
		hb.pack_end(delete_button)

		hb.pack_start(box)

		# MAIN WINDOW
		main_window = Gtk.Grid(column_homogeneous=False, column_spacing=5, row_spacing=5)

		#SIDEBAR
		self.sidebar = sb.Sidebar()
		self.sidebar.view.connect("row_activated",self.show_note)

		#EDITOR
		self.editor = editor.Editor()

		#FORMAT TOOLBAR
		self.format_toolbar = ft.FormatBar()

		#TAGS
		self.tag_bar = Gtk.Entry()
		self.tag_bar.set_placeholder_text("Tags")
		self.tag_bar.set_hexpand(True)

		self.start_database()
		if self.db:
			self.id = max(self.db.keys())+1
		else:
			self.id = 0

		main_window.attach(self.sidebar,0,0,1,2)
		main_window.attach(self.editor, 1, 0, 2, 1)
		main_window.attach(self.tag_bar,1,1,1,1)
		main_window.attach(self.format_toolbar,2,1,1,1)
		self.add(main_window)
	
	def create_note(self,button):
		title = self.editor.get_title()
		if title != '':
			self.sidebar.add_item(title,self.id)
			self.db[self.id] = self.editor.get_text()
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
		self.editor.set_text(self.db[item])

	def save_note(self,event):
		path =  self.sidebar.get_selected()
		if path != None:
			self.db[self.sidebar.get_item(path)] = self.editor.get_text()

		

win = MainWindow()
win.show_all()
Gtk.main()