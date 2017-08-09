import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk,Gdk

class Editor(Gtk.ScrolledWindow):

	def __init__(self):
		Gtk.ScrolledWindow.__init__(self)
		self.set_vexpand(True)
		self.set_hexpand(True)
		
		#TextView
		self.textview = Gtk.TextView()
		self.textview.set_wrap_mode(3)
		self.textview.set_bottom_margin(5)
		self.textview.set_top_margin(5)
		self.textview.set_left_margin(5)
		self.textview.set_right_margin(5)
		self.textbuffer = self.textview.get_buffer()

		self.add(self.textview)

	def get_title(self):
		title = self.textbuffer.get_text(self.textbuffer.get_start_iter(), self.textbuffer.get_iter_at_line(1), False)
		if title == '':
			title = self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),False)
			if title == '':
				return
		if len(title) > 20:
			return title[:20]

	def get_text(self):

		return self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),True)

	def set_text(self,content):
		self.textbuffer.set_text(content)