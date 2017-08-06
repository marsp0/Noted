import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk

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

        create_button = Gtk.Button.new_with_label("Create")
        create_button.connect("clicked",self.create_note)
        box.add(create_button)

        delete_button = Gtk.Button.new_with_label("Delete")
        delete_button.connect("clicked",self.delete_note)
        box.add(delete_button)

        hb.pack_start(box)

        #main Window
        main_window = Gtk.Grid(column_homogeneous=False, column_spacing=5)

        left_window = Gtk.Box(Gtk.Orientation.VERTICAL)
        left_window.set_size_request(200,400)
        
        store = Gtk.ListStore(str)
        treeiter = store.append(["some biches"])
        treeiter = store.append(["some biches2"])

        print store

        view = Gtk.TreeView(store)

        renderer = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Notes",renderer,text = 0)
        view.append_column(col)

        left_window.add(view)


        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        self.text = Gtk.TextView()
        self.text.set_wrap_mode(3)
        scrolled_window.add(self.text)

        

        main_window.attach(left_window,0,0,1,1)
        main_window.attach(scrolled_window, 1, 0, 1, 1)
        self.add(main_window)
    
    def create_note(self,button):
        print button
        pass

    def delete_note(self,button):
        pass
    
    def start_database(self):
        self.store = 

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()