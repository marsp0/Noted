import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk

class NameDialog(Gtk.Dialog):

	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "", parent, 0,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
		Gtk.STOCK_OK, Gtk.ResponseType.OK))
		self.label = Gtk.Label("Choose a name")

		self.entry = Gtk.Entry()

		box = self.get_content_area()
		box.add(self.label)
		box.add(self.entry)
		self.show_all()
