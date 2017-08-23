from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_tables import Notebook, Note, Base
import getpass
import os
import subprocess

class Database(object):

	def start_database(self):
		db_path = "/home/{}/noted".format(getpass.getuser())
		if not os.path.exists(db_path):
			subprocess.call(['mkdir', '{}'.format(db_path)])
			self.engine = create_engine('sqlite:///{}/database.db'.format(db_path),echo=True)
			Base.metadata.create_all(self.engine)
		else:
			self.engine = create_engine('sqlite:///{}/database.db'.format(db_path),echo=True)
			Base.metadata.bind = self.engine
		DBSession = sessionmaker(bind=self.engine)
		self.session = DBSession()

	def stop_database(self):
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
		notebook = self.session.query(Notebook).filter_by(idd=notebook_id).one()
		for note in notes:
			self.session.delete(note)
		self.session.delete(notebook)
		self.session.commit()

	def delete_note(self,idd):
		note = self.session.query(Note).filter_by(idd=idd).one()
		self.session.delete(note)
		self.session.commit()

	def modify_note(self,idd,name,content):
		note = self.session.query(Note).filter_by(idd=idd)
		note.name = name
		note.content = content
		self.session.commit()

	def get_notebooks(self):
		pass

p = Database()