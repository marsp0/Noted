import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk

class FormatBar(Gtk.Box):

	def __init__(self):

		Gtk.Box.__init__(self)
		Gtk.StyleContext.add_class(self.get_style_context(), "linked")

		#bold
		self.bold = Gtk.ToggleButton()
		image =  Gtk.Image.new_from_icon_name("format-text-bold-symbolic", Gtk.IconSize.MENU)
		image.show()
		self.bold.add(image)
		self.bold.set_tooltip_text("Bold")

		#Italic
		self.italic = Gtk.ToggleButton()
		image =  Gtk.Image.new_from_icon_name("format-text-italic-symbolic", Gtk.IconSize.MENU)
		image.show()
		self.italic.add(image)
		self.italic.set_tooltip_text("Italic")

		#Underline
		self.underline = Gtk.ToggleButton()
		image =  Gtk.Image.new_from_icon_name("format-text-underline-symbolic", Gtk.IconSize.MENU)
		image.show()
		self.underline.add(image)
		self.underline.set_tooltip_text("Underline")

		#ubuntu font
		self.ubuntu = Gtk.ToggleButton.new_with_label("Ubuntu Mono")

		#font size
		self.size = Gtk.Entry()
		self.size.set_text(str(12))
		self.size.set_max_width_chars(4)
		self.size.set_width_chars(4)
		self.size.set_max_length(2)


		self.buttons = {}
		self.buttons['bold'] = self.bold
		self.buttons['italic'] = self.italic
		self.buttons['underline'] = self.underline
		self.buttons['ubuntu'] = self.ubuntu
		#no need to add size as it is not being toggled
		#self.buttons['size'] = self.size

		self.pack_end(self.size,False,False,0)
		self.pack_end(self.ubuntu,False,False,0)
		self.pack_end(self.underline,False,False,0)
		self.pack_end(self.italic,False,False,0)
		self.pack_end(self.bold,False,False,0)