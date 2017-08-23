from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_tables import Notebook, Note, Base
import getpass
import os
import subprocess

class Database(object):

	def start_database(self):
		db_path = "/home/{}/noted/sqlitedatabase.db".format(getpass.getuser())
		if not os.path.exists(db_path):
			self.engine = create_engine('sqlite:///{}'.format(db_path),echo=False)
			Base.metadata.create_all(self.engine)
		else:
			self.engine = create_engine('sqlite:///{}'.format(db_path),echo=False)
			Base.metadata.bind = self.engine
		DBSession = sessionmaker(bind=self.engine)
		self.session = DBSession()

	def close_database(self):
		self.session.close()

	def create_note(self,name,content,idd,notebook_id):
		note = Note(name=name,content=content,idd = idd,notebook_id = notebook_id)
		self.session.add(note)
		self.session.commit()

	def create_notebook(self,name,idd):
		notebook = Notebook(name=name, idd = idd)
		self.session.add(notebook)
		self.session.commit()

	def delete_notebook(self,idd):
		notes = self.session.query(Note).filter_by(notebook_id=idd).all()
		notebook = self.session.query(Notebook).filter_by(idd=idd).one()
		for note in notes:
			self.session.delete(note)
		self.session.delete(notebook)
		self.session.commit()

	def delete_note(self,idd):
		note = self.session.query(Note).filter_by(idd=idd).one()
		self.session.delete(note)
		self.session.commit()

	def modify_note(self,name,content,idd):
		note = self.session.query(Note).filter_by(idd=idd).one()
		note.name = unicode(name,'utf-8')
		note.content = unicode(content, 'utf-8')
		self.session.commit()

	def get_notebooks(self):
		notebooks = self.session.query(Notebook).all()
		return notebooks

	def get_notes_from_notebook(self,notebook_id):
		notes = self.session.query(Note).filter_by(notebook_id = notebook_id).all()
		return notes

	def get_note(self,idd):
		result = self.session.query(Note).filter_by(idd=idd).one()
		return result