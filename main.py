import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk
import shelve

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Noted")
        self.set_border_width(7)
        self.set_size_request(1000, 800)
        
        #Header Bar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Noted"
        self.set_titlebar(hb)
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

        #Create Button
        create_button = Gtk.Button.new_with_label("Create")
        create_button.connect("clicked",self.create_note)
        box.add(create_button)

        #Delete Button
        delete_button = Gtk.Button.new_with_label("Delete")
        delete_button.connect("clicked",self.delete_note)
        box.add(delete_button)

        hb.pack_start(box)

        #main Window
        main_window = Gtk.Grid(column_homogeneous=False, column_spacing=5)

        main_left = Gtk.ScrolledWindow()

        left_window = Gtk.Box(Gtk.Orientation.VERTICAL)
        left_window.set_size_request(200,400)

        self.store = Gtk.ListStore(str)

        print self.store

        self.view = Gtk.TreeView(self.store)
        self.view.set_headers_visible(False)

        renderer = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Notes",renderer,text = 0)
        self.view.append_column(col)

        main_left.add(self.view)
        left_window.add(main_left)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(3)
        self.textbuffer = self.textview.get_buffer()
        scrolled_window.add(self.textview)

        main_window.attach(left_window,0,0,1,1)
        main_window.attach(scrolled_window, 1, 0, 1, 1)
        self.add(main_window)
    
    def create_note(self,button):
        #limit of chars for the title of the note
        title_limit = -2
        #get the actual title
        title = self.textbuffer.get_text(self.textbuffer.get_start_iter(), self.textbuffer.get_iter_at_line(1), False)
        #if title is empty then it means that there is only 1 line of note
        if title == '':
            title = self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),False)
            title_limit = len(title)
        if len(title) > 20:
            title_limit = 20
        self.store.append([title[:title_limit]])

    def delete_note(self,button):
        item =  self.view.get_selection().get_selected()[1]
        self.store.remove(item)
    
    def start_database(self):
        store = shelve.open("database")
        return store


win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()