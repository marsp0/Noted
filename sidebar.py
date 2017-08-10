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
		self.store = Gtk.ListStore(str,int)

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

	def add_item(self,title,note_id):

		self.store.append([title,note_id])

	def modify_item(self,path,title):

		if self.store[path][0] != title:
			self.store[path][0] = title

	def remove_item(self):

		item =  self.view.get_selection().get_selected()[1]
		if item != None:
			to_return = self.store[item][1]
			self.store.remove(item)
			return to_return

	def get_item(self,path):

		return self.store[path][1]

	def get_selected(self):
		
		return self.view.get_selection().get_selected()[1]