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
import notebook_dialog as nd


class MainWindow(Gtk.Window):

	def __init__(self):
		Gtk.Window.__init__(self, title="Noted")
		self.set_border_width(5)
		self.set_size_request(1000, 800)
		
		#Header Bar
		hbar = hb.Headerbar()
		hbar.connect("destroy",self.close_database)
		self.set_titlebar(hbar)

		#Notebook button
		hbar.notebook_button.connect("clicked",self.create_notebook)
		
		#Create Button
		hbar.create_button.connect("clicked",self.create_note)

		#Save button
		hbar.save_button.connect("clicked",self.save_note)

		#Delete Button
		hbar.delete_button.connect("clicked",self.delete_note)

		# MAIN WINDOW
		main_window = Gtk.Grid(column_homogeneous=False, column_spacing=5)

		#SIDEBAR
		self.sidebar = sb.Sidebar()
		self.sidebar.view.connect("row_activated",self.show_note)

		#EDITOR
		self.editor = editor.Editor()

		#loads the storage file and creates the dict db
		self.start_database()
		

		main_window.attach(self.sidebar,0,0,1,2)
		main_window.attach(self.editor, 1, 0, 2, 1)
		self.add(main_window)

	def create_notebook(self,button):
		#creates a new notebook
		dialog = nd.NameDialog(self)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			name = dialog.entry.get_text()
			self.sidebar.add_notebook(name,self.notebook_id)
			self.db[self.notebook_id] = {"name" : name, "notes" : {}}
			self.notebook_id += 1
		dialog.destroy()
	
	def create_note(self,button):
		if self.sidebar.add_item("New Note", self.id):
			self.editor.set_text("")
			note_item = note.Note("New Note", "", [])
			parent_id = self.sidebar.get_id(self.sidebar.get_selected())
			self.db[parent_id]['notes'][self.id] = note_item
			self.id += 1

	def delete_note(self,button):

		result = self.sidebar.remove_item()
		self.editor.set_text("")
		if result != None:
			note_id, parent_id = result
			if note_id != None:
				del self.db[parent_id]['notes'][note_id]
			else:
				del self.db[parent_id]

	def show_note(self,treeview,path,col):
		if len(path) > 1:
			parent_iter = self.sidebar.get_parent(treeview.get_selection().get_selected()[1])
			parent_id = self.sidebar.get_id(parent_iter)
			note_id = self.sidebar.get_id(path)
			self.editor.set_text(self.db[parent_id]['notes'][note_id].get_content())
		else:
			self.editor.set_text("")

	def save_note(self,event):
		path =  self.sidebar.get_selected()
		#check if something was selected and that it was not a notebook
		if path != None and len(self.sidebar.get_path(path).to_string()) > 1:
			clean_text = self.editor.get_clean_text()
			if clean_text != "":
				title = self.get_title(clean_text)
				
			else:
				title = "New Note"

			content = self.editor.get_text()
			note_item = note.Note(title,content,[])
			parent_iter = self.sidebar.get_parent(path)
			parent_id = self.sidebar.get_id(parent_iter)
			note_id = self.sidebar.get_id(path)
			self.db[parent_id]['notes'][note_id] = note_item
			self.sidebar.modify_item(path,title)

	def start_database(self):

		db = shelve.open("database.db")
		if not db:
			self.db = {}
			self.id = 0
			self.notebook_id = 0
		else:
			self.db = db['notes']
			self.id = db['note_id']
			self.notebook_id = db['notebook_id']

		for item in self.db:
			notebook_iter = self.sidebar.add_notebook(self.db[item]['name'],item)
			for note_item in self.db[item]['notes']:
				self.sidebar.add_item(self.db[item]['notes'][note_item].get_title(),note_item,notebook_iter)
		db.close()

	def close_database(self,event):
		db = shelve.open('database.db')
		db['notes'] = self.db
		db['note_id'] = self.id
		db['notebook_id'] = self.notebook_id
		db.close()
		self.hide()
		Gtk.main_quit()


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

		self.editor.toggle_tag(tag, None)

win = MainWindow()
win.show_all()
Gtk.main()