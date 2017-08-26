class UndoManager(object):

	def __init__(self):
		self.undo_stack = []
		self.redo_stack = []

	def undo(self):
		#print self.undo_stack
		if self.undo_stack:
			result =  self.undo_stack.pop()
			self.redo_stack.append(result)
			return result

	def redo(self):
		#print self.redo_stack
		if self.redo_stack:
			result = self.redo_stack.pop()
			return result

	def add(self,memento):
		self.undo_stack.append(memento)

class ApplyTag(object):

	def __init__(self,buf, start_mark, end_mark, tag):
		self.buf = buf
		self.start = start_mark
		self.end = end_mark
		self.tag = tag

	def undo(self):
		start_iter = self.buf.get_iter_at_mark(self.start)
		end_iter = self.buf.get_iter_at_mark(self.end)
		self.buf.remove_tag(self.tag,start_iter,end_iter)

	def redo(self):
		start_iter = self.buf.get_iter_at_mark(self.start)
		end_iter = self.buf.get_iter_at_mark(self.end)
		self.buf.apply_tag(self.tag,start_iter,end_iter)

class RemoveTag(object):

	def __init__(self,buf,start_mark,end_mark,tag):
		self.buf = buf
		self.start=  start_mark
		self.end = end_mark
		self.tag = tag

	def undo(self):
		start_iter = self.buf.get_iter_at_mark(self.start)
		end_iter = self.buf.get_iter_at_mark(self.end)
		self.buf.apply_tag(self.tag,start_iter,end_iter)

	def redo(self):
		start_iter = self.buf.get_iter_at_mark(self.start)
		end_iter = self.buf.get_iter_at_mark(self.end)
		self.buf.remove_tag(self.tag,start_iter,end_iter)

class RemoveText(object):

	def __init__(self,buf,start_mark,end_mark, data):
		self.buf = buf
		self.start = start_mark
		self.end = end_mark
		self.data = data

	def undo(self):
		start_iter = self.buf.get_iter_at_mark(self.start)
		self.buf.insert(start_iter,self.data)

	def redo(self):
		start_iter = self.buf.get_iter_at_mark(self.start)
		end_iter = self.buf.get_iter_at_mark(self.end)
		self.buf.delete(start_iter,end_iter)

class AddText(object):

	def __init__(self,buf,start_mark,end_mark,data):
		self.buf = buf
		self.start = start_mark
		self.end = end_mark
		self.data = data

	def undo(self):
		start_iter = self.buf.get_iter_at_mark(self.start)
		end_iter = self.buf.get_iter_at_mark(self.end)
		self.buf.delete(start_iter,end_iter)

	def redo(self):
		start_iter = self.buf.get_iter_at_mark(self.start)
		end_iter = self.buf.get_iter_at_mark(self.end)
		self.buf.insert(start_iter,self.data)