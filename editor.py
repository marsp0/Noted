import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk,Gdk, Pango
import format_toolbar as ft

class Editor(Gtk.Grid):

	def __init__(self):

		Gtk.Grid.__init__(self,row_spacing=5, column_spacing=2)

		#scrolled window
		self.scrolled_window = Gtk.ScrolledWindow()
		self.scrolled_window.set_vexpand(True)
		self.scrolled_window.set_hexpand(True)
		
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

		#Scrolle Window to TextView
		self.scrolled_window.add(self.textview)

		self.tags = {}
		self.tags['bold'] = self.textbuffer.create_tag("bold",weight=Pango.Weight.BOLD)
		self.tags['italic'] = self.textbuffer.create_tag("italic",style=Pango.Style.ITALIC)
		self.tags['underline'] = self.textbuffer.create_tag("underline",underline=Pango.Underline.SINGLE)
		self.tags['open_sans'] = self.textbuffer.create_tag("sans",family = "Open Sans")
		self.tags['calibri'] = self.textbuffer.create_tag("calibri", family = "Calibri")

		self.connect("key-press-event",self.apply_tag)

		#TAGS
		self.tag_bar = Gtk.Entry()
		self.tag_bar.set_placeholder_text("Tags")
		self.tag_bar.set_hexpand(True)

		#FORMAT TOOLBAR
		self.format_toolbar = ft.FormatBar()
		self.format_toolbar.bold.connect("clicked",self.toggle_tag, 'bold')
		self.format_toolbar.italic.connect("clicked",self.toggle_tag, 'italic')
		self.format_toolbar.underline.connect("clicked",self.toggle_tag, 'underline')
		self.format_toolbar.calibri.connect("clicked", self.toggle_tag,'calibri')
		self.format_toolbar.open_sans.connect("clicked", self.toggle_tag,'open_sans')


		self.attach(self.scrolled_window,0,0,2,1)
		self.attach(self.tag_bar,0,1,1,1)
		self.attach(self.format_toolbar,1,1,1,1)

	def get_text(self):

		return self.textbuffer.serialize(self.textbuffer,self.serialized_format,self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())

	def set_text(self,content):

		self.textbuffer.set_text("")
		if content != "":
			self.textbuffer.deserialize(self.textbuffer,self.deserialized_format,self.textbuffer.get_start_iter(),content)
		else:
			pass


	def toggle_tag(self,widget,tag):
		limits = self.textbuffer.get_selection_bounds()
		to_apply = True
		if len(limits) != 0:
			start,end = limits
			tag_list = start.get_tags()
			if len(tag_list) != 0:
				for item in tag_list:
					if item.props.name == tag:
						self.textbuffer.remove_tag(self.tags[tag],start,end)
						to_apply = False
			if to_apply:
				self.textbuffer.apply_tag(self.tags[tag],start,end)
				#print self.tags[tag].props.font


	def get_clean_text(self):

		return self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),False)

	def apply_tag(self,widget,key):
		print 
		try:
			if ord(key.string) >= 32:
				start_index = self.textbuffer.props.cursor_position-1
				start_iter = self.textbuffer.get_iter_at_offset(start_index)
				end_iter = self.textbuffer.get_iter_at_offset(start_index+1)
				self.textbuffer.apply_tag(self.tags['bold'],start_iter,end_iter)
				print 'dsa'
		except TypeError:
			pass