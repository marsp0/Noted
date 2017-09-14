import gi
gi.require_version('Gtk', '3.0')
# gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Gdk, Pango, GdkPixbuf
import format_toolbar as ft
import subprocess

WHITESPACE = ('\r', '\n', '\t', ' ')

class UndoableInsert(object):

    def __init__(self,text_iter,text,text_len):

        self.offset = text_iter.get_offset()
        self.text = text
        self.len = text_len
        self.tags = text_iter.get_tags()
        if self.len > 1:
            self.mergeable = False
        else:
            self.mergeable = True

class UndoableDelete(object):

    def __init__(self,buf, start_iter,end_iter):

        self.text = buf.get_text(start_iter, end_iter,False)
        self.tags = start_iter.get_tags()
        self.start = start_iter.get_offset()
        self.end = end_iter.get_offset()
        insert_iter = buf.get_iter_at_mark(buf.get_insert())
        if insert_iter.get_offset() <= self.start:
            self.delete_key_used = True
        else:
            self.delete_key_used = False
        if self.end - self.start > 1 or self.text in ("\r", "\n", " "):
            self.mergeable = False
        else:
            self.mergeable = True
            
class UndoableInsertTag(object):
    
    def __init__(self, tag, start, end):
        self.tag = tag
        self.start = start.get_offset()
        self.end = end.get_offset()
        self.mergeable = False
        
class UndoableDeleteTag(object):

    def __init__(self,tag,start,end):
        self.tag = tag
        self.start = start.get_offset()
        self.end = end.get_offset()
        self.mergeable = False


class Editor(Gtk.Grid):

    def __init__(self,parent):

        Gtk.Grid.__init__(self, row_spacing=5, column_spacing=2)
        
        #############################################################
        # Scrolled window
        #############################################################
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_hexpand(True)
        self.parent = parent

        self.current_indent_level = 1
        self.offset_after_tab_deletion = None
        
        #############################################################
        # TextView
        #############################################################
        
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
        
        #############################################################
        # Scrolle Window to TextView
        #############################################################
        
        self.scrolled_window.add(self.textview)
        
        #############################################################
        #Tags
        #############################################################
        
        self.tags = {}
        self.tags['bold'] = self.textbuffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.tags['italic'] = self.textbuffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.tags['underline'] = self.textbuffer.create_tag("underline", underline=Pango.Underline.SINGLE)
        self.tags['just_left'] = self.textbuffer.create_tag("just_left", justification=Gtk.Justification(0))
        self.tags['just_center'] = self.textbuffer.create_tag("just_center", justification=Gtk.Justification(2))
        self.tags['just_right'] = self.textbuffer.create_tag("just_right", justification=Gtk.Justification(1))
        self.tags['just_fill'] = self.textbuffer.create_tag("just_fill", justification=Gtk.Justification(3))
        self.tags['title'] = self.textbuffer.create_tag('title', font='20')
        self.tags['header'] = self.textbuffer.create_tag('header', font='15')
        
        #############################################################
        # SIGNAL CONNECTIONS
        #############################################################
        
        self.textbuffer.connect_after("insert-text", self.insert_with_tags)
        self.textbuffer.connect("delete-range",self.delete)
        self.textbuffer.connect_after("delete-range",self.delete_after)
        
        #############################################################
        #Shortcuts
        #############################################################
        self.parent.connect('key-press-event',self.activate_shortcuts)
        
        #############################################################
        # FORMAT TOOLBAR
        #############################################################
        
        self.format_toolbar = ft.FormatBar()
        self.format_toolbar.bold.connect("clicked", self.toggle_tag, 'bold')
        self.format_toolbar.italic.connect("clicked", self.toggle_tag, 'italic')
        self.format_toolbar.underline.connect("clicked", self.toggle_tag, 'underline')

        self.format_toolbar.just_right.connect('clicked', self.apply_just, 'just_right')
        self.format_toolbar.just_left.connect('clicked', self.apply_just, 'just_left')
        self.format_toolbar.just_center.connect('clicked', self.apply_just, 'just_center')
        self.format_toolbar.just_fill.connect('clicked', self.apply_just, 'just_fill')
        self.format_toolbar.title.connect('clicked', self.apply_tag, 'title')
        self.format_toolbar.header.connect('clicked', self.apply_tag, 'header')
        #self.format_toolabar.image.connect("clicked", self.add_image)
        self.format_toolbar.list.connect("clicked",self.add_list)
        self.format_toolbar.undo.connect('clicked',self.undo)
        self.format_toolbar.redo.connect('clicked',self.redo)
        self.format_toolbar.send_feedback.connect("clicked", self.send_feedback)
        
        ##################################################################
        #keep a dict so that we have the buttons act like Toggle buttons
        ##################################################################
        
        self.just_buttons = {}
        self.just_buttons['just_left'] = False
        self.just_buttons['just_center'] = False
        self.just_buttons['just_right'] = False
        self.just_buttons['just_fill'] = False
        
        #############################################################
        #UNDO
        #############################################################
        
        self.undo_stack = []
        self.redo_stack = []
        self.not_undoable_action = False
        self.undo_in_progress = False

        #############################################################
        #Packing
        #############################################################
        
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
                ##########
                #undo part
                ##########
                if not self.undo_in_progress:
                    redo_stack = []
                if self.not_undoable_action:
                    return
                undo_action = UndoableInsertTag(tag,start,end)
                self.undo_stack.append(undo_action)
                
            else:
                self.textbuffer.remove_tag(self.tags[tag], start, end)
                ##########
                #undo part
                ##########
                if not self.undo_in_progress:
                    redo_stack = []
                if self.not_undoable_action:
                    return
                undo_action = UndoableDeleteTag(tag,start,end)
                self.undo_stack.append(undo_action)
        self.textview.grab_focus()

    def apply_tag(self, widget, tag):
        limits = self.textbuffer.get_selection_bounds()
        if len(limits) != 0:
            start, end = limits
            if tag == 'header':
                self.textbuffer.remove_tag(self.tags['title'], start, end)
            elif tag == 'title':
                self.textbuffer.remove_tag(self.tags['header'],start,end)
            self.textbuffer.apply_tag(self.tags[tag], start, end)
            
            ##########
            #undo part
            ##########
            if not self.undo_in_progress:
                redo_stack = []
            if self.not_undoable_action:
                return
            undo_action = UndoableInsertTag(tag,start,end)
            self.undo_stack.append(undo_action)
        self.textview.grab_focus()

    def apply_just(self,widget,tag):
        current_position = self.textbuffer.get_iter_at_offset(self.textbuffer.props.cursor_position)
        current_line = current_position.get_line()
        current_line_offset = current_position.get_line_offset()
        start_iter = self.textbuffer.get_iter_at_line_offset(current_line,0)
        if start_iter.get_chars_in_line() <= 1:
            end_iter = self.textbuffer.get_iter_at_line_offset(current_line,0)
        else:
            end_iter = self.textbuffer.get_iter_at_line_offset(current_line,1)
        for button in self.just_buttons:
            if button != tag:
                self.just_buttons[button] = False
                self.textbuffer.remove_tag(self.tags[button],start_iter,end_iter)
            else:
                self.just_buttons[tag] = True
                self.textbuffer.apply_tag(self.tags[tag],start_iter,end_iter)
        self.textview.grab_focus()


    def insert_with_tags(self, buf, start_iter, data, data_len):
        end = self.textbuffer.props.cursor_position
        #creating new start iter because the provided one
        #gets invalidated for some reason
        start_iter = self.textbuffer.get_iter_at_offset(end-1)
        end_iter = self.textbuffer.get_iter_at_offset(end)
        if not self.undo_in_progress:
            for tag in self.format_toolbar.buttons:
                if self.format_toolbar.buttons[tag].get_active():
                    self.textbuffer.apply_tag(self.tags[tag], start_iter, end_iter)
        if start_iter.get_line_offset() == 0:
            for item in self.just_buttons:
                if self.just_buttons[item] == True:
                    self.textbuffer.apply_tag(self.tags[item],start_iter,end_iter)
                    self.textbuffer.place_cursor(end_iter)
                    
        if self.format_toolbar.list.get_active() and not self.undo_in_progress:
            new_iter = self.textbuffer.get_iter_at_offset(self.textbuffer.props.cursor_position)
            if data == '\n':
                for i in xrange(self.current_indent_level):
                    self.textbuffer.insert(new_iter,'\t')
                    new_iter.forward_char()
                self.textbuffer.insert(new_iter,'-')
                new_iter.forward_char()
                self.textbuffer.insert(new_iter,' ')
            elif data == '\t':
                current_line = new_iter.get_line()
                start_iter = self.textbuffer.get_iter_at_line_offset(current_line,0)
                end_iter = self.textbuffer.get_iter_at_line_offset(current_line,start_iter.get_chars_in_line()-1)
                template = '\t'*self.current_indent_level+'- '
                line_content = self.textbuffer.get_text(start_iter,end_iter,False)
                if line_content in (template,template+'\t'):
                    if line_content == template:
                        remove_start_iter = self.textbuffer.get_iter_at_line_offset(current_line,self.current_indent_level+2)
                        remove_end_iter = self.textbuffer.get_iter_at_line_offset(current_line,self.current_indent_level+3)
                    else:
                        remove_start_iter = self.textbuffer.get_iter_at_line_offset(current_line,self.current_indent_level+3)
                        remove_end_iter = self.textbuffer.get_iter_at_line_offset(current_line,self.current_indent_level+4)
                    self.textbuffer.delete(remove_start_iter,remove_end_iter)
                    add_start_iter = self.textbuffer.get_iter_at_line_offset(current_line,0)
                    self.textbuffer.insert(add_start_iter,'\t')
                    self.current_indent_level += 1
        self.textview.grab_focus()
        ##########
        #undo part
        ##########
        def can_be_merged(prev,cur):
            if not cur.mergeable or not prev.mergeable:
                return False
            elif cur.offset != (prev.offset + prev.len):
                return False
            elif cur.text in WHITESPACE and not prev.text in WHITESPACE:
                return False
            elif prev.text in WHITESPACE and not cur.text in WHITESPACE:
                return False
            return True
        
        if not self.undo_in_progress:
            self.redo_stack = []
        if self.not_undoable_action:
            return
        current_cursor_position = self.textbuffer.props.cursor_position
        start = self.textbuffer.get_iter_at_offset(current_cursor_position - data_len)
        undo_action = UndoableInsert(start, data, data_len)
        try:
            prev_insert = self.undo_stack.pop()
        except IndexError:
            self.undo_stack.append(undo_action)
            return
        if not isinstance(prev_insert,UndoableInsert):
            self.undo_stack.append(prev_insert)
            self.undo_stack.append(undo_action)
            return
        if can_be_merged(prev_insert,undo_action):
            prev_insert.len += undo_action.len
            prev_insert.text += undo_action.text
            self.undo_stack.append(prev_insert)
        else:
            self.undo_stack.append(prev_insert)
            self.undo_stack.append(undo_action)

    def delete(self,buff, start,end):
        if buff.get_text(start,end,False) == '\t' and start.get_line_offset() <= self.current_indent_level:
            if self.current_indent_level > 1:
                self.current_indent_level -= 1
                self.offset_after_tab_deletion = start.get_offset()
        ##########
        #undo part
        ##########
        def can_be_merged(prev,cur):
            WHITESPACE = (' ', '\t')
            if not cur.mergeable or not prev.mergeable:
                return False
            elif prev.delete_key_used != cur.delete_key_used:
                return False
            elif prev.start != cur.start and prev.start != cur.end:
                return False
            elif cur.text not in WHITESPACE and prev.text in WHITESPACE:
                return False
            elif cur.text in WHITESPACE and prev.text not in WHITESPACE:
                return False
            return True
        if not self.undo_in_progress:
            self.redo_stack = []
        if self.not_undoable_action:
            return
        undo_action = UndoableDelete(self.textbuffer,start,end)
        try:
            prev_delete = self.undo_stack.pop()
        except IndexError:
            self.undo_stack.append(undo_action)
            return
        if not isinstance(prev_delete, UndoableDelete):
            self.undo_stack.append(prev_delete)
            self.undo_stack.append(undo_action)
            return
        if can_be_merged(prev_delete, undo_action):
            if prev_delete.start == undo_action.start:
                prev_delete.text += undo_action.text
                prev_delete.end  += (undo_action.end - undo_action.start)
            else:
                prev_delete = "{}{}".format(undo_action.text,prev_delete.text)
                prev_delete.start = undo_action.start
            self.undo_stack.append(prev_delete)
        else:
            self.undo_stack.append(prev_delete)
            self.undo_stack.append(undo_action)

    def delete_after(self,buff,start,end):
        if self.offset_after_tab_deletion:
            self.textbuffer.insert(buff.get_iter_at_offset(self.offset_after_tab_deletion),'- ')
            self.offset_after_tab_deletion = None
            
    def undo(self,widget):
        if not self.undo_stack:
            return
        self.not_undoable_action = True
        self.undo_in_progress = True
        undo_action = self.undo_stack.pop()
        self.redo_stack.append(undo_action)
        if isinstance(undo_action,UndoableInsert):
            start = self.textbuffer.get_iter_at_offset(undo_action.offset)
            end = self.textbuffer.get_iter_at_offset(undo_action.offset+undo_action.len)
            self.textbuffer.delete(start,end)
            self.textbuffer.place_cursor(start)
        elif isinstance(undo_action, UndoableInsertTag):
            start = self.textbuffer.get_iter_at_offset(undo_action.start)
            end = self.textbuffer.get_iter_at_offset(undo_action.end)
            self.textbuffer.remove_tag(self.tags[undo_action.tag],start,end)
            self.textview.grab_focus()
        elif isinstance(undo_action,UndoableDeleteTag):
            start = self.textbuffer.get_iter_at_offset(undo_action.start)
            end = self.textbuffer.get_iter_at_offset(undo_action.end)
            self.textbuffer.apply_tag(self.tags[undo_action.tag],start,end)
        else:
            start = self.textbuffer.get_iter_at_offset(undo_action.start)
            self.textbuffer.insert(start,undo_action.text)
            end = self.textbuffer.get_iter_at_offset(undo_action.end)
            for tag in undo_action.tags:
                self.textbuffer.apply_tag(tag,start,end)
            if undo_action.delete_key_used:
                self.textbuffer.place_cursor(start)
            else:
                self.textbuffer.place_cursor(end)
        self.textview.grab_focus()
        self.not_undoable_action = False
        self.undo_in_progress = False
        
    def redo(self,widget):
        if not self.redo_stack:
            return
        self.not_undoable_action = True
        self.undo_in_progress = True
        redo_action = self.redo_stack.pop()
        self.undo_stack.append(redo_action)
        if isinstance(redo_action, UndoableInsert):
            start = self.textbuffer.get_iter_at_offset(redo_action.offset)
            self.textbuffer.insert(start,redo_action.text)
            new_cursor_pos = self.textbuffer.get_iter_at_offset(redo_action.offset + redo_action.len)
            for tag in redo_action.tags:
                start = self.textbuffer.get_iter_at_offset(redo_action.offset)
                end = self.textbuffer.get_iter_at_offset(redo_action.offset+redo_action.len)
                self.textbuffer.apply_tag(tag,start,end)
            self.textbuffer.place_cursor(new_cursor_pos)
        elif isinstance(redo_action,UndoableInsertTag):
            start = self.textbuffer.get_iter_at_offset(redo_action.start)
            end = self.textbuffer.get_iter_at_offset(redo_action.end)
            self.textbuffer.apply_tag(self.tags[redo_action.tag],start,end)
        elif isinstance(redo_action,UndoableDeleteTag):
            start = self.textbuffer.get_iter_at_offset(redo_action.start)
            end = self.textbuffer.get_iter_at_offset(redo_action.end)
            self.textbuffer.remove_tag(self.tags[redo_action.tag],start,end)
        else:
            start = self.textbuffer.get_iter_at_offset(redo_action.start)
            end = self.textbuffer.get_iter_at_offset(redo_action.end)
            self.textbuffer.delete(start,end)
            self.textbuffer.place_cursor(start)
        self.textview.grab_focus()
        self.not_undoable_action = False
        self.undo_in_progress = False

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
            current_position = self.textbuffer.get_iter_at_offset(self.textbuffer.props.cursor_position)
            self.textbuffer.insert(current_position, '\n\t- ')
        else:
            self.current_indent_level = 1

    def send_feedback(self, widget):
        try:
            result = subprocess.call(
                ["pantheon-mail", "mailto:notedfeedback@gmail.com"])
        except OSError:
            pass

    def activate_shortcuts(self,widget,event):
        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)
        state = event.state
        ctrl = (state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and keyval_name == 'b':
            if self.format_toolbar.bold.get_active():
                self.format_toolbar.bold.set_active(False)
            else:
                self.format_toolbar.bold.set_active(True)
        elif ctrl and keyval_name == 'i':
            if self.format_toolbar.italic.get_active():
                self.format_toolbar.italic.set_active(False)
            else:
                self.format_toolbar.italic.set_active(True)
        elif ctrl and keyval_name == 'u':
            if self.format_toolbar.underline.get_active():
                self.format_toolbar.underline.set_active(False)
            else:
                self.format_toolbar.underline.set_active(True)
        elif ctrl and keyval_name == 't':
            self.apply_tag(None,'title')
        elif ctrl and keyval_name == 'h':
            self.apply_tag(None,'header')
        elif ctrl and keyval_name == 'l':
            self.apply_just(None,'just_left')
        elif ctrl and keyval_name == 'r':
            self.apply_just(None,'just_right')
        elif ctrl and keyval_name == 'e':
            self.apply_just(None,'just_center')
        elif ctrl and keyval_name == 'j':
            self.apply_just(None,'just_fill')
        elif ctrl and keyval_name == 'g':
            if self.format_toolbar.list.get_active():
                self.format_toolbar.list.set_active(False)
            else:
                self.format_toolbar.list.set_active(True)
