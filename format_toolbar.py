import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk

class FormatBar(Gtk.Box):

	def __init__(self):
		Gtk.Box.__init__(self)
		Gtk.StyleContext.add_class(self.get_style_context(), "linked")
		bold = Gtk.Button.new_with_label("Bold")
		italic = Gtk.Button.new_with_label("Italic")
		underline = Gtk.Button.new_with_label("Underline")
		font_size = Gtk.Button.new_with_label("Font Size")
		self.pack_end(font_size,False,True,0)
		self.pack_end(underline,False,True,0)
		self.pack_end(italic,False,True,0)
		self.pack_end(bold,False,True,0)