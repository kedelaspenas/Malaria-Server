import os

from serveus import app

from serveus.models import db, User, Case, Image, MalType

# app.config['SQLALCHEMY_BINDS'] = { 'crowd': 'sqlite:///'+os.getcwd().replace('\\','/')+ '/cs198pythontest.db' }

'''
To create the database:
- open python shell
from crowd import *
from crowd.models import *
db.create_all()

delete:
db.drop_all()

Column types: http://pythonhosted.org/Flask-SQLAlchemy/models.html
'''



class LabelerType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    # Optional
    def __init__(self, name=""):
        self.name = name

    def __repr__(self):
        return '<Labeler Type %r>' % self.name

    def __str__(self):
        return self.name
    
'''
class Labeler(db.Model):
    pass

class TrainingImage(db.Model):
    pass

class ImageLabel(db.Model):
    pass

class TrainingImageLabelCell(db.Model):
    pass
'''
