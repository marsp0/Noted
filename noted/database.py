import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_tables import Notebook, Note, Base
import os
import subprocess
from logger import logger as lg

class Database(object):

	logger = lg.Logger()

	@lg.logging_decorator(logger)
	def start_database(self):
		path = GLib.get_user_data_dir()
		db_path = "{}/Noted/sqlitedatabase.db".format(path)
		if not os.path.exists(db_path):
			self.engine = create_engine('sqlite:///{}'.format(db_path),echo=False)
			Base.metadata.create_all(self.engine)
		else:
			self.engine = create_engine('sqlite:///{}'.format(db_path),echo=False)
			Base.metadata.bind = self.engine
		DBSession = sessionmaker(bind=self.engine)
		self.session = DBSession()

	@lg.logging_decorator(logger)
	def close_database(self):
		self.session.close()

	@lg.logging_decorator(logger)
	def create_note(self,name,content,idd,notebook_id):
		try:
			note = Note(name=unicode(name,'iso-8859-1'),content=unicode(content,'iso-8859-1'),idd = idd,notebook_id = notebook_id)
		except TypeError:
			note = Note(name=name,content=content,idd=idd,notebook_id=notebook_id)
		self.session.add(note)
		self.session.commit()

	@lg.logging_decorator(logger)
	def create_notebook(self,name,idd):
		notebook = Notebook(name=name, idd = idd)
		self.session.add(notebook)
		self.session.commit()

	@lg.logging_decorator(logger)
	def delete_notebook(self,idd):
		notes = self.session.query(Note).filter_by(notebook_id=idd).all()
		notebook = self.session.query(Notebook).filter_by(idd=idd).one()

		if notebook.name == 'Trash':
			for note in notes:
				self.session.delete(note)
		else:
			trash_notebook = self.session.query(Notebook).filter_by(name='Trash').one()
			for note in notes:
				note.notebook_id = trash_notebook.idd
				note.deleted_notebook_name = notebook.name
				note.deleted_notebook_id = notebook.idd
		self.session.commit()
		self.session.delete(notebook)
		self.session.commit()

	@lg.logging_decorator(logger)
	def delete_note(self,idd):
		note = self.session.query(Note).filter_by(idd=idd).one()
		notebook = self.session.query(Notebook).filter_by(idd=note.notebook_id).one()
		trash_notebook = self.session.query(Notebook).filter_by(name='Trash').one()
		if notebook.name == 'Trash':
			self.session.delete(note)
		else:
			note.notebook_id = trash_notebook.idd
			note.deleted_notebook_name = notebook.name
			note.deleted_notebook_id = notebook.idd
		self.session.commit()
		
	@lg.logging_decorator(logger)
	def restore_note(self,idd):
		note = self.session.query(Note).filter_by(idd=idd).one()
		notebook_name = note.deleted_notebook_name
		notebook = self.session.query(Notebook).filter_by(name = note.deleted_notebook_name, idd = note.deleted_notebook_id).first()
		if notebook:
			note.deleted_notebook_name = None
			note.deleted_notebook_id = None
			note.notebook_id = notebook.idd
			result = False
		else:
			self.create_notebook(note.deleted_notebook_name,note.deleted_notebook_id)
			note.notebook_id = note.deleted_notebook_id
			note.deleted_notebook_name = None
			note.deleted_notebook_id = None
			result = True
		self.session.commit()
		return note.notebook_id,notebook_name,result
		
	@lg.logging_decorator(logger)	
	def modify_note(self,name,content,idd):
		note = self.session.query(Note).filter_by(idd=idd).one()
		note.name = unicode(name,'iso-8859-1')
		note.content = unicode(content,'iso-8859-1')
		self.session.commit()

	@lg.logging_decorator(logger)
	def get_notebooks(self):
		notebooks = self.session.query(Notebook).all()
		return notebooks

	@lg.logging_decorator(logger)
	def get_notes_from_notebook(self,notebook_id):
		notes = self.session.query(Note).filter_by(notebook_id = notebook_id).all()
		return notes

	@lg.logging_decorator(logger)
	def get_note(self,idd):
		result = self.session.query(Note).filter_by(idd=idd).one()
		return result
