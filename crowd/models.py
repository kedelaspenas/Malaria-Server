import os

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
    __tablename__ = 'labelertype'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    labelers = db.relationship('Labeler', backref='labelertype', lazy='dynamic')

    # Optional
    def __init__(self, name=""):
        self.name = name

    def __repr__(self):
        return '<Labeler Type %r>' % self.name

    def __str__(self):
        return self.name

class Labeler(db.Model):
    __tablename__ = 'labeler'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_images_labeled = db.Column(db.Integer)
    total_correct_images_labeled = db.Column(db.Integer)
    last_session = db.Column(db.DateTime())
    labeler_rating = db.Column(db.Float)
    labeler_type_id = db.Column(db.Integer, db.ForeignKey('labelertype.id'))

class TrainingImage(db.Model):
    __tablename__ = 'trainingimage'
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    total_labels = db.Column(db.Integer)
    final_label = db.Column(db.Integer, db.ForeignKey('maltype.id'))
    date_finalized = db.Column(db.DateTime())
    training_image_labels = db.relationship('TrainingImageLabel', backref='trainingimage', lazy='dynamic')
    
class TrainingImageLabel(db.Model):
    __tablename__ = 'trainingimagelabel'
    id = db.Column(db.Integer, primary_key=True)
    training_image_id = db.Column(db.Integer, db.ForeignKey('trainingimage.id'))
    date = db.Column(db.Date)
    # is there a db column type na duration?
    time_start = db.Column(db.Time)
    time_end = db.Column(db.Time)
    initial_label = db.Column(db.Integer, db.ForeignKey('maltype.id'))
    correct_label = db.Column(db.Integer, db.ForeignKey('maltype.id'))
    labeler_correct = db.Column(db.Boolean)
    cells = db.relationship('TrainingImageLabelCell', backref='trainingimagelabel', lazy='dynamic')

class TrainingImageLabelCell(db.Model):
    __tablename__ = 'trainingimagelabelcell'
    id = db.Column(db.Integer, primary_key=True)
    training_image_label_id = db.Column(db.Integer, db.ForeignKey('trainingimagelabel.id'))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    nearest_cell_x = db.Column(db.Float)
    nearest_cell_y = db.Column(db.Float)
