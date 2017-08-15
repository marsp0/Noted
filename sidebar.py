import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk,Gdk

class Sidebar(Gtk.VBox):

	def __init__(self):

		Gtk.VBox.__init__(self,False,0)
		self.set_size_request(200,400)
		self.scrolled_window = Gtk.ScrolledWindow()

		self.set_homogeneous(False)

		#TreeStore
		self.store = Gtk.TreeStore(str,int)

		#Renderer
		self.renderer = Gtk.CellRendererText()

		#TreeView
		self.view = Gtk.TreeView(self.store)
		self.view.set_headers_visible(False)
		self.view.modify_bg(Gtk.StateType.NORMAL,Gdk.Color.parse('#F6F6F5')[1])
		self.view.modify_bg(Gtk.StateType.SELECTED, Gdk.Color.parse('#2980b9')[1])
		self.view.modify_fg(Gtk.StateType.SELECTED, Gdk.Color.parse('#ffffff')[1])
		self.view.set_activate_on_single_click(True)
		self.view.append_column(Gtk.TreeViewColumn("Notes",self.renderer,text=0))
		
		#add
		self.scrolled_window.add(self.view)
		self.add(self.scrolled_window)


	def add_notebook(self, name, notebook_id):
		notebook_iter = self.store.append(None,[name,notebook_id])
		return notebook_iter

	def add_item(self,title,note_id,notebook_iter=None):

		#Adds one item to the store
		#there is an option to pass notebook iter. It is used when starting the database
		#checks the depth of the iter to avoid making more nested folders

		if notebook_iter == None:
			parent_iter = self.get_selected()
			if parent_iter != None:
				if self.store.iter_depth(parent_iter) != 0:
					parent_iter = self.store.iter_parent(parent_iter)
				self.store.append(parent_iter,[title,note_id])
				return True
		else:
			if self.store.iter_depth(notebook_iter) == 0:
				self.store.append(notebook_iter,[title,note_id])
				return True
		return False


	def modify_item(self,path,title):

		if self.store[path][0] != title:
			self.store[path][0] = title

	def remove_item(self):

		item =  self.get_selected()
		if item != None:
			if len(self.store.get_path(item).to_string()) > 1:
				note_id = self.store[item][1]
				parent_iter = self.store.iter_parent(item)
				parent_id = self.get_id(parent_iter)
			else:
				parent_id = self.store[item][1]
				note_id = None
			self.store.remove(item)
			return note_id,parent_id

	def get_id(self,path):
		#get db id from TreePath
		return self.store[path][1]

	def get_selected(self):
		#returns an iter to the selected row
		return self.view.get_selection().get_selected()[1]

	def get_path(self,iter_node):
		#returns TreePath representing the path to the selected node
		return self.store.get_path(iter_node)

	def get_parent(self,iter_node):
		#get parent of a selected note
		return self.store.iter_parent(iter_node)

	def get_iter_from_path(self,path):
		return self.store.get_iter(path)