import gi
gi.require_version('Gtk', '3.0')
# gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Gdk, Pango, GdkPixbuf
import format_toolbar as ft
import subprocess


class Editor(Gtk.Grid):

    def __init__(self,parent):

        Gtk.Grid.__init__(self, row_spacing=5, column_spacing=2)

        # scrolled window
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_hexpand(True)

        # TextView
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(3)
        self.textview.set_bottom_margin(5)
        self.textview.set_top_margin(5)
        self.textview.set_left_margin(5)
        self.textview.set_right_margin(5)
        self.textview.modify_font(Pango.FontDescription.from_string("11"))
        self.textbuffer = self.textview.get_buffer()
        self.serialized_format = self.textbuffer.register_serialize_tagset()
        self.deserialized_format = self.textbuffer.register_deserialize_tagset()

        # Scrolle Window to TextView
        self.scrolled_window.add(self.textview)

        self.tags = {}
        self.tags['bold'] = self.textbuffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.tags['italic'] = self.textbuffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.tags['underline'] = self.textbuffer.create_tag("underline", underline=Pango.Underline.SINGLE)
        self.tags['ubuntu'] = self.textbuffer.create_tag("ubuntu", family="Ubuntu Mono")
        self.tags['just_left'] = self.textbuffer.create_tag("just_left", justification=Gtk.Justification(0))
        self.tags['just_center'] = self.textbuffer.create_tag("just_center", justification=Gtk.Justification(2))
        self.tags['just_right'] = self.textbuffer.create_tag("just_right", justification=Gtk.Justification(1))
        self.tags['just_fill'] = self.textbuffer.create_tag("just_fill", justification=Gtk.Justification(3))
        self.tags['title'] = self.textbuffer.create_tag('title', font='20')
        self.tags['header'] = self.textbuffer.create_tag('header', font='15')

        # SIGNAL CONNECTIONS
        self.textbuffer.connect_after("insert-text", self.insert_with_tags)

        # FORMAT TOOLBAR
        self.format_toolbar = ft.FormatBar()
        self.format_toolbar.bold.connect("clicked", self.toggle_tag, 'bold')
        self.format_toolbar.italic.connect("clicked", self.toggle_tag, 'italic')
        self.format_toolbar.underline.connect("clicked", self.toggle_tag, 'underline')
        self.format_toolbar.ubuntu.connect("clicked", self.toggle_tag, 'ubuntu')
        self.format_toolbar.just_right.connect('clicked', self.apply_tag, 'just_right')
        self.format_toolbar.just_left.connect('clicked', self.apply_tag, 'just_left')
        self.format_toolbar.just_center.connect('clicked', self.apply_tag, 'just_center')
        self.format_toolbar.just_fill.connect('clicked', self.apply_tag, 'just_fill')
        self.format_toolbar.title.connect('clicked', self.apply_tag, 'title')
        self.format_toolbar.header.connect('clicked', self.apply_tag, 'header')
        #self.format_toolbar.image.connect("clicked", self.add_image)
        self.format_toolbar.list.connect("clicked",self.add_list)
        self.format_toolbar.send_feedback.connect("clicked", self.send_feedback)


        self.attach(self.scrolled_window, 0, 0, 2, 1)
        self.attach(self.format_toolbar, 0, 1, 2, 1)

    def get_text(self,start=None,end=None):
        if not start:
            start = self.textbuffer.get_start_iter()
        if not end:
            end = self.textbuffer.get_end_iter()
        return self.textbuffer.serialize(self.textbuffer,
                                         self.serialized_format,
                                         start,
                                         end)

    def get_clean_text(self):

        return self.textbuffer.get_text(self.textbuffer.get_start_iter(),
                                        self.textbuffer.get_end_iter(), False)

    def set_text(self, content):
        self.textbuffer.set_text("")
        if content != "":
            self.textbuffer.deserialize(self.textbuffer,
                                        self.deserialized_format,
                                        self.textbuffer.get_start_iter(),
                                        content.encode("iso-8859-1"))
        else:
            pass

    def toggle_tag(self, widget, tag):
        limits = self.textbuffer.get_selection_bounds()
        if len(limits) != 0:
            start, end = limits
            if self.format_toolbar.buttons[tag].get_active():
                self.textbuffer.apply_tag(self.tags[tag], start, end)
            else:
                self.textbuffer.remove_tag(self.tags[tag], start, end)

    def apply_tag(self, widget, tag):
        limits = self.textbuffer.get_selection_bounds()
        if len(limits) != 0:
            start, end = limits
            if tag == 'header':
                self.textbuffer.remove_tag(self.tags['title'], start, end)
            elif tag == 'title':
                self.textbuffer.remove_tag(self.tags['header'], start, end)
            elif tag == 'just_left':
                self.textbuffer.remove_tag(self.tags['just_right'], start, end)
                self.textbuffer.remove_tag(
                    self.tags['just_center'], start, end)
                self.textbuffer.remove_tag(self.tags['just_fill'], start, end)
            elif tag == 'just_right':
                self.textbuffer.remove_tag(self.tags['just_left'], start, end)
                self.textbuffer.remove_tag(
                    self.tags['just_center'], start, end)
                self.textbuffer.remove_tag(self.tags['just_fill'], start, end)
            elif tag == 'just_center':
                self.textbuffer.remove_tag(self.tags['just_right'], start, end)
                self.textbuffer.remove_tag(self.tags['just_left'], start, end)
                self.textbuffer.remove_tag(self.tags['just_fill'], start, end)
            elif tag == 'just_fill':
                self.textbuffer.remove_tag(self.tags['just_right'], start, end)
                self.textbuffer.remove_tag(self.tags['just_center'], start, end)
                self.textbuffer.remove_tag(self.tags['just_left'], start, end)
            self.textbuffer.apply_tag(self.tags[tag], start, end)

    def insert_with_tags(self, buf, start_iter, data, data_len):
        end = self.textbuffer.props.cursor_position
        #creating new start iter because the provided one
        #gets invalidated for some reason
        start_iter = self.textbuffer.get_iter_at_offset(end-data_len)
        end_iter = self.textbuffer.get_iter_at_offset(end)
        #print 'the content is', self.textbuffer.get_text(start_iter,end_iter,False), repr(data)
        for tag in self.format_toolbar.buttons:
            if self.format_toolbar.buttons[tag].get_active():
                self.textbuffer.apply_tag(self.tags[tag], start_iter, end_iter)
        if self.format_toolbar.list.get_active():
            if data == '\n':
                new_iter = self.textbuffer.get_iter_at_offset(self.textbuffer.props.cursor_position+1)
                self.textbuffer.insert(new_iter,'\t- ', 3)


    def add_image(self, widget):
        dialog = Gtk.FileChooserDialog("Pick a file",
                                       None,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.ACCEPT))
        image_filter = Gtk.FileFilter()
        image_filter.set_name("Image files")
        image_filter.add_mime_type("image/*")
        dialog.add_filter(image_filter)
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            image_path = dialog.get_file().get_path()
            image = GdkPixbuf.Pixbuf.new_from_file(image_path)
            image_format, width, height = GdkPixbuf.Pixbuf.get_file_info(
                image_path)
            if width > 800:
                width = 800
            if height > 640:
                height = 640
            if width > 800 and height > 640:
                width = 800
                height = 640
            image = image.scale_simple(
                width, height, GdkPixbuf.InterpType.BILINEAR)
            current_position = self.textbuffer.props.cursor_position
            cursor_iter = self.textbuffer.get_iter_at_offset(current_position)
            self.textbuffer.insert_pixbuf(cursor_iter, image)

        dialog.destroy()

    def add_list(self,widget):
        if self.format_toolbar.list.get_active():
            current_position = self.textbuffer.get_iter_at_offset(self.textbuffer.props.cursor_position+4)
            self.textbuffer.insert(current_position, '\n\t- ')

    def send_feedback(self, widget):
        try:
            result = subprocess.call(
                ["pantheon-mail", "mailto:notedfeedback@gmail.com"])
        except OSError:
            pass
