from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Notebook(Base):

	__tablename__ = 'notebook'

	idd = Column(Integer,primary_key = True)
	name = Column(String(250), nullable=False)
	notes = relationship('Note',backref='notebook')

class Note(Base) :

	__tablename__ = 'note'

	idd = Column(Integer,primary_key=True)
	name = Column(String(250), nullable=False)
	content = Column(Text)
	notebook_id = Column(Integer, ForeignKey("notebook.idd"))
	deleted_notebook_name = Column(String,nullable=True)
	deleted_notebook_id = Column(Integer,nullable=True)
