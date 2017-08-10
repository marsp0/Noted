import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk,Gdk
import format_toolbar as ft
import sidebar as sb
import headerbar as hb
import editor
import note
import shelve


class MainWindow(Gtk.Window):

	def __init__(self):
		Gtk.Window.__init__(self, title="Noted")
		self.set_border_width(5)
		self.set_size_request(1000, 800)
		
		#Header Bar
		hbar = hb.Headerbar()
		hbar.connect("destroy",self.close_database)
		self.set_titlebar(hbar)
		
		#Create Button
		hbar.create_button.connect("clicked",self.create_note)

		#Save button
		hbar.save_button.connect("clicked",self.save_note)

		#Delete Button
		hbar.delete_button.connect("clicked",self.delete_note)

		# MAIN WINDOW
		main_window = Gtk.Grid(column_homogeneous=False, column_spacing=5, row_spacing=5)

		#SIDEBAR
		self.sidebar = sb.Sidebar()
		self.sidebar.view.connect("row_activated",self.show_note)

		#EDITOR
		self.editor = editor.Editor()

		#FORMAT TOOLBAR
		self.format_toolbar = ft.FormatBar()
		self.format_toolbar.bold.connect("clicked",self.on_button_clicked, 'bold')
		self.format_toolbar.italic.connect("clicked",self.on_button_clicked, 'italic')
		self.format_toolbar.underline.connect("clicked",self.on_button_clicked, 'underline')

		#TAGS
		self.tag_bar = Gtk.Entry()
		self.tag_bar.set_placeholder_text("Tags")
		self.tag_bar.set_hexpand(True)

		self.start_database()
		

		main_window.attach(self.sidebar,0,0,1,2)
		main_window.attach(self.editor, 1, 0, 2, 1)
		main_window.attach(self.tag_bar,1,1,1,1)
		main_window.attach(self.format_toolbar,2,1,1,1)
		self.add(main_window)
	
	def create_note(self,button):

		self.sidebar.add_item("New Note", self.id)
		self.editor.set_text("")
		note_item = note.Note("New Note", "", [])
		self.db[self.id] = note_item
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
			self.sidebar.add_item(self.db[item].get_title(),item)
		
		if self.db:
			self.id = max(self.db.keys())+1
		else:
			self.id = 0
		db.close()

	def close_database(self,event):
		print self.db
		db = shelve.open('database.db')
		db['notes'] = self.db
		db.close()
		self.hide()
		Gtk.main_quit()

	def show_note(self,tree_view,path,col):

		item = self.sidebar.get_item(path)
		self.editor.set_text(self.db[item].get_content())

	def save_note(self,event):

		path =  self.sidebar.get_selected()
		if path != None:
			clean_text = self.editor.get_clean_text()
			if clean_text != "":
				title = self.get_title(clean_text)
				
			else:
				title = "New Note"

			content = self.editor.get_text()
			note_item = note.Note(title,content,[])
			self.db[self.sidebar.get_item(path)] = note_item
			self.sidebar.modify_item(path,title)


	def get_title(self,content):

		content = content.lstrip()
		title_index = content.find("\n")
		if title_index < 20 and title_index != -1:
			title = content[:title_index]
		elif len(content) > 20:
			title = content[:20]
		else:
			title = content
		return title
		
	def on_button_clicked(self,widget,tag):

		self.editor.apply_tag(tag)


win = MainWindow()
win.show_all()
Gtk.main()