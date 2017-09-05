class UndoManager(object):

	def __init__(self):
		self.undo_stack = []
		self.redo_stack = []

	def undo(self):
		if self.undo_stack:
			print len(self.undo_stack)
			result =  self.undo_stack.pop()
			self.redo_stack.append(result)
			return result

	def redo(self):
		#print self.redo_stack
		if self.redo_stack:
			result = self.redo_stack.pop()
			#self.undo_stack.append(result)
			return result

	def add(self,memento,to_cancel=None):
		self.undo_stack.append(memento)

#############################################################
# Memento
#############################################################

class Memento(object):

	def __init__(self, buf, format, data):
		self.buf = buf
		self.data = data
		self.format = format

	def undo(self):
		self.buf.set_text("")
		self.buf.deserialize(self.buf,self.format,self.buf.get_start_iter(),self.data.encode("iso-8859-1"))

#############################################################
# TAGS
#############################################################

class ApplyTag(object):

	def __init__(self,buf, start_offset, end_offset, tag):
		self.buf = buf
		self.start = start_offset
		self.end = end_offset
		self.tag = tag

	def undo(self):
		start_iter = self.buf.get_iter_at_offset(self.start)
		end_iter = self.buf.get_iter_at_offset(self.end)
		self.buf.remove_tag(self.tag,start_iter,end_iter)

	def redo(self):
		start_iter = self.buf.get_iter_at_offset(self.start)
		end_iter = self.buf.get_iter_at_offset(self.end)
		self.buf.apply_tag(self.tag,start_iter,end_iter)

class RemoveTag(object):

	def __init__(self,buf,start_offset,end_offset,tag):
		ApplyTag.__init__(self,buf,start_offset,end_offset,tag)

	def undo(self):
		ApplyTag.redo(self)

	def redo(self):
		ApplyTag.undo(self)


#############################################################
# Text
#############################################################

class AddText(object):

	def __init__(self,buf,start_offset,end_offset,data):
		self.buf = buf
		self.start = start_offset
		self.end = end_offset
		self.data = data

	def undo(self):
		start_iter = self.buf.get_iter_at_offset(self.start)
		end_iter = self.buf.get_iter_at_offset(self.end)
		self.buf.delete(start_iter,end_iter)

	def redo(self):
		start_iter = self.buf.get_iter_at_offset(self.start)
		end_iter = self.buf.get_iter_at_offset(self.end)
		self.buf.insert(start_iter,self.data)

class RemoveText(AddText):

	def __init__(self,buf,start_offset,end_offset, data):
		AddText.__init__(self, buf, start_offset,end_offset,data)

	def undo(self):
		AddText.redo(self)

	def redo(self):
		AddText.undo(self)