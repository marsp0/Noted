import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import sidebar as sb
import headerbar as hb
import editor
import shelve
from dialogs import notebook_dialog as nd
from dialogs import delete_dialog as dd
from database import Database
import getpass
import os
import subprocess

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Noted")
        self.set_border_width(5)
        self.set_size_request(1100, 900)
        self.set_resizable(False)
        # Header Bar
        hbar = hb.Headerbar()
        hbar.connect("destroy", self.close_database)
        self.set_titlebar(hbar)

        # Notebook button
        hbar.notebook_button.connect("clicked", self.create_notebook)

        # Create Button
        hbar.create_button.connect("clicked", self.create_note)

        # Save button
        hbar.save_button.connect("clicked", self.save_note)

        # Delete Button
        hbar.delete_button.connect("clicked", self.delete_note)

        #shortcuts
        self.connect("key-press-event",self.on_key_press)

        # MAIN WINDOW
        main_window = Gtk.Grid(column_homogeneous=False, column_spacing=5)

        # SIDEBAR
        self.sidebar = sb.Sidebar()
        self.sidebar.view.connect("row_activated", self.show_note)

        # EDITOR
        self.editor = editor.Editor(self)

        # loads the storage file and creates the dict db
        self.start_database()

        main_window.attach(self.sidebar, 0, 0, 1, 2)
        main_window.attach(self.editor, 1, 0, 2, 1)
        self.add(main_window)

    def create_notebook(self, button):
        # creates a new notebook
        dialog = nd.NameDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = dialog.entry.get_text()
            if name != '':
                self.sidebar.add_notebook(name, self.notebook_id)
                self.database.create_notebook(name,self.notebook_id)
                self.notebook_id += 1
        dialog.destroy()

    def create_note(self, button):
        if self.sidebar.add_item("New Note", self.id):
            self.editor.set_text("")
            parent_id = self.sidebar.get_id(self.sidebar.get_selected())
            self.database.create_note("New Note",'',self.id, parent_id)
            self.id += 1

    def delete_note(self, button):
        dialog = dd.DeleteDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            result = self.sidebar.remove_item()
            self.editor.set_text("")
            if result is not None:
                note_id, parent_id = result
                if note_id is not None:
                    self.database.delete_note(note_id)
                else:
                    self.database.delete_notebook(parent_id)
        dialog.destroy()

    def show_note(self, treeview, path, col):
        if len(path) > 1:
            parent_iter = self.sidebar.get_parent(treeview.get_selection().get_selected()[1])
            parent_id = self.sidebar.get_id(parent_iter)
            note_id = self.sidebar.get_id(path)
            content = self.database.get_note(note_id).content
            self.editor.set_text(content)
        else:
            self.editor.set_text("")
            if treeview.row_expanded(path) is False:
                treeview.expand_row(path, True)
            else:
                treeview.collapse_row(path)

    def save_note(self, event):
        path = self.sidebar.get_selected()
        # check if something was selected and that it was not a notebook
        if path is not None and len(self.sidebar.get_path(path).to_string()) > 1:
            clean_text = self.editor.get_clean_text()
            if clean_text != "":
                title = self.get_title(clean_text)

            else:
                title = "New Note"

            content = self.editor.get_text()
            parent_iter = self.sidebar.get_parent(path)
            parent_id = self.sidebar.get_id(parent_iter)
            note_id = self.sidebar.get_id(path)
            self.database.modify_note(title,content,note_id)
            self.sidebar.modify_item(path, title)

    def start_database(self):
        path = "/home/{}/noted".format(getpass.getuser())
        if not os.path.exists(path):
            subprocess.call(['mkdir', path])
        db = shelve.open("/home/{}/noted/database.db".format(getpass.getuser()))
        self.database = Database()
        self.database.start_database()
        if not db:
            self.id = 1
            self.notebook_id = 1
        else:
            self.id = db['note_id']
            self.notebook_id = db['notebook_id']
        for notebook in self.database.get_notebooks():
            notebook_iter = self.sidebar.add_notebook(notebook.name, notebook.idd)
            notes = self.database.get_notes_from_notebook(notebook.idd)
            for note in notes:
                self.sidebar.add_item(note.name,note.idd,notebook_iter)
        db.close()

    def close_database(self, event):
        db = shelve.open("/home/{}/noted/database.db".format(getpass.getuser()))
        db['note_id'] = self.id
        db['notebook_id'] = self.notebook_id
        db.close()
        self.database.close_database()
        self.hide()
        Gtk.main_quit()

    def get_title(self, content):

        content = content.lstrip()
        title_index = content.find("\n")
        if title_index < 20 and title_index != -1:
            title = content[:title_index]
        elif len(content) > 20:
            title = content[:20]
        else:
            title = content
        return title

    def on_button_clicked(self, widget, tag):

        self.editor.toggle_tag(tag, None)


    def on_key_press(self,widget,event):
        keyval = event.keyval
        keyval_name = Gdk.keyval_name(keyval)
        state = event.state
        ctrl = (state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and keyval_name == 's':
            self.save_note(None)
        elif ctrl and keyval_name == 'n':
            self.create_note(None)
        elif ctrl and keyval_name == 'k':
            self.create_notebook(None)
        elif ctrl and keyval_name == 'q':
            self.close_database(None)

def start():
    win = MainWindow()
    win.show_all()
    Gtk.main()
