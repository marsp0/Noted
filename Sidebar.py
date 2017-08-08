import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk

class Sidebar(Gtk.Box):

	def __init__(self):
		Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)
		self.set_size_request(200,400)
		self.scrolled_window = Gtk.ScrolledWindow()


		#TreeView
		self.view = Gtk.TreeView()


		#TreeStore
		self.store = Gtk.ListStore(str,int)
		
