import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk


class DeleteDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "", parent, 0,
                            (Gtk.STOCK_NO, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_YES, Gtk.ResponseType.OK))

        self.label = Gtk.Label("Are you sure ?")

        box = self.get_content_area()
        box.add(self.label)
        self.show_all()
