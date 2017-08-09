import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk

class FormatBar(Gtk.Box):

	def __init__(self):
		Gtk.Box.__init__(self)
		Gtk.StyleContext.add_class(self.get_style_context(), "linked")
		self.bold = Gtk.ToggleButton.new_with_label("Bold")
		self.italic = Gtk.ToggleButton.new_with_label("Italic")
		self.underline = Gtk.ToggleButton.new_with_label("Underline")
		self.font_size = Gtk.ToggleButton.new_with_label("Font Size")
		self.pack_end(self.font_size,False,True,0)
		self.pack_end(self.underline,False,True,0)
		self.pack_end(self.italic,False,True,0)
		self.pack_end(self.bold,False,True,0)