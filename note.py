class Note(object):

	def __init__(self, title,content,tags):

		self._title = title
		self._content = content
		self._tags = tags


	def get_content(self):

		return self._content

	def set_content(self,content):

		self._content = content

	def get_title(self):

		return self._title

	def set_title(self,title):

		self._title = title

	def get_tags(self):

		return self._tags

	def set_tags(self,tags):
		
		self._tags = tags