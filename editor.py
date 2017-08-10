import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk,Gdk, Pango
import format_toolbar as ft

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
		self.serialized_format = self.textbuffer.register_serialize_tagset()
		self.deserialized_format = self.textbuffer.register_deserialize_tagset()

		self.tags = {}
		self.tags['bold'] = self.textbuffer.create_tag("bold",weight=Pango.Weight.BOLD)
		self.tags['italic'] = self.textbuffer.create_tag("italic",style=Pango.Style.ITALIC)
		self.tags['underline'] = self.textbuffer.create_tag("underline",underline=Pango.Underline.SINGLE)

		self.add(self.textview)

	def get_text(self):

		return self.textbuffer.serialize(self.textbuffer,self.serialized_format,self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())

	def set_text(self,content):

		self.textbuffer.set_text("")
		if content != "":
			print self.textview.get_monospace()
			self.textbuffer.deserialize(self.textbuffer,self.deserialized_format,self.textbuffer.get_start_iter(),content)
		else:
			pass


	def toggle_tag(self,tag):
		limits = self.textbuffer.get_selection_bounds()
		if len(limits) != 0:
			start,end = limits
			tag_list = start.get_tags()
			to_apply = True
			if len(tag_list) != 0:
				for item in tag_list:
					if item.props.name == tag:
						self.textbuffer.remove_tag(self.tags[tag],start,end)
						to_apply = False
			if to_apply:
				self.textbuffer.apply_tag(self.tags[tag],start,end)

	def get_clean_text(self):

		return self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),False)

	def modify_font(self,font_description):
		self.textview.modify_font(font_description)