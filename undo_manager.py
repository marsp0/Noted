

class UndoManager(object):

	def __init__(self):
		self.undo_stack = []
		self.redo_stack = []