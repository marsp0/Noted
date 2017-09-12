import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk


class Sidebar(Gtk.VBox):

    def __init__(self):

        Gtk.VBox.__init__(self, False, 0)
        self.set_size_request(200, 600)
        self.scrolled_window = Gtk.ScrolledWindow()

        self.set_homogeneous(True)

        # TreeStore
        self.store = Gtk.TreeStore(str, int)

        # Renderer
        self.renderer = Gtk.CellRendererText()

        # TreeView
        self.view = Gtk.TreeView(self.store)
        self.view.set_headers_visible(False)
        # F6F6F5 - grey sidebar
        self.view.modify_bg(Gtk.StateType.NORMAL,
                            Gdk.Color.parse('#F6F6F5')[1])
        self.view.modify_bg(Gtk.StateType.SELECTED,
                            Gdk.Color.parse('#2980b9')[1])
        self.view.modify_fg(Gtk.StateType.SELECTED,
                            Gdk.Color.parse('#ffffff')[1])
        self.view.set_activate_on_single_click(True)
        self.view.append_column(Gtk.TreeViewColumn("Notes",
                                self.renderer, text=0))
        self.trash_iter = None
        
        self.selection = self.view.get_selection()
        
        self.sidebar_options = {}
        self.menu = Gtk.Menu()
        item_new = Gtk.MenuItem('New')
        self.menu.append(item_new)
        self.sidebar_options['new'] = item_new
        item_delete = Gtk.MenuItem("Delete")
        self.menu.append(item_delete)
        self.sidebar_options['delete'] = item_delete
        item_restore = Gtk.MenuItem("Restore")
        self.menu.append(item_restore)
        self.sidebar_options['restore'] = item_restore
        self.menu.show_all()
        self.menu.attach_to_widget(self.view,None)
        
        # add
        self.scrolled_window.add(self.view)
        self.add(self.scrolled_window)
        
    def get_trash_iter(self):
        for item in self.store:
            if item[0] == 'Trash':
                self.trash_iter = item.iter

    def add_notebook(self, name, notebook_id):
        notebook_iter = self.store.append(None, [name, notebook_id])
        if self.trash_iter != None:
            self.store.move_before(notebook_iter,self.trash_iter)
        return notebook_iter

    def add_item(self, title, note_id, notebook_iter=None):
        # Adds one item to the store
        # there is an option to pass notebook iter.
        # It is used when starting the database
        # checks the depth of the iter to avoid making more nested folders

        if notebook_iter is None:
            parent_iter = self.get_selected()
            if parent_iter is not None and self.store[parent_iter][0] != 'Trash':
                if self.store.iter_depth(parent_iter) != 0:
                    parent_iter = self.store.iter_parent(parent_iter)
                self.store.append(parent_iter, [title, note_id])
                return True
        else:
            if self.store.iter_depth(notebook_iter) == 0:
                self.store.append(notebook_iter, [title, note_id])
                return True
        return False

    def modify_item(self, path, title):

        if self.store[path][0] != title:
            self.store[path][0] = title

    def remove_item(self):

        item = self.get_selected()
        if item is not None and self.store[item][0] != 'Trash':
            if len(self.store.get_path(item).to_string()) > 1:
                note_id = self.store[item][1]
                parent_iter = self.store.iter_parent(item)
                parent_id = self.get_id(parent_iter)
                if parent_id != self.get_id(self.trash_iter):
                    self.add_item(self.store[item][0],note_id,self.trash_iter)
            else:
                parent_id = self.store[item][1]
                note_id = None
                children_amount = self.store.iter_n_children(item)
                counter = 0
                current_child = self.store.iter_children(item)
                while counter < children_amount:
                    title = self.store[current_child][0]
                    idd = self.store[current_child][1]
                    self.add_item(title,idd,self.trash_iter)
                    counter += 1
                    current_child = self.store.iter_next(current_child)
            self.store.remove(item)
            return note_id, parent_id

    def get_id(self, path):
        # get db id from TreePath
        return self.store[path][1]

    def get_selected(self):
        # returns an iter to the selected row
        return self.view.get_selection().get_selected()[1]

    def get_path(self, iter_node):
        # returns TreePath representing the path to the selected node
        return self.store.get_path(iter_node)

    def get_parent(self, iter_node):
        # get parent of a selected note
        return self.store.iter_parent(iter_node)

    def get_iter_from_path(self, path):
        return self.store.get_iter(path)
