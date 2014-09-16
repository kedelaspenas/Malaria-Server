import os

from serveus.models import db, User, UserType, Case, Key, Image, Database, Chunklist, Chunk, Region, Province, Municipality, ParType, Validation

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

    def __str__(self):
        return self.name

class Labeler(db.Model):
    __tablename__ = 'labeler'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_images_labeled = db.Column(db.Integer)
    total_correct_images_labeled = db.Column(db.Integer)
    current_training_image_id = db.Column(db.Integer, db.ForeignKey('trainingimage.id'))
    last_session = db.Column(db.DateTime())
    labeler_rating = db.Column(db.Float)
    labeler_type_id = db.Column(db.Integer, db.ForeignKey('labelertype.id'))
    training_image_labels = db.relationship('TrainingImageLabel', backref='labeler', lazy='dynamic')
    
    def __init__(self, user_id="", total_images_labeled="", total_correct_images_labeled="", current_training_image_id ="", last_session="", labeler_rating="", labeler_type_id=""):
        self.user_id = user_id
        self.total_images_labeled = total_images_labeled
        self.total_correct_images_labeled = total_correct_images_labeled
        self.current_training_image_id = current_training_image_id
        self.last_session = last_session
        self.labeler_rating = labeler_rating
        self.labeler_type_id = labeler_type_id
        
    def __str__(self):
        return self.user.username

class TrainingImage(db.Model):
    __tablename__ = 'trainingimage'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    total_labels = db.Column(db.Integer)
    final_label_1 = db.Column(db.String(80))
    final_label_2 = db.Column(db.String(80))
    date_finalized = db.Column(db.DateTime())
    training_image_labels = db.relationship('TrainingImageLabel', backref='trainingimage', lazy='dynamic')
    
    def __init__(self, image_id="", total_labels="", final_label_1="", final_label_2="", date_finalized=""):
        self.image_id = image_id
        self.total_labels = total_labels
        self.final_label_1 = final_label_1
        self.final_label_2 = final_label_2
        self.date_finalized = date_finalized
        
    def __str__(self):
        return 'Training image ' + str(self.id) + ' labels ' + str(self.total_labels)
    
class TrainingImageLabel(db.Model):
    __tablename__ = 'trainingimagelabel'
    
    id = db.Column(db.Integer, primary_key=True)
    labeler_id = db.Column(db.Integer, db.ForeignKey('labeler.id'))
    training_image_id = db.Column(db.Integer, db.ForeignKey('trainingimage.id'))
    date = db.Column(db.Date)
    # is there a db column type na duration?
    time_start = db.Column(db.Time)
    time_end = db.Column(db.Time)
    initial_label = db.Column(db.String(80))
    correct_label = db.Column(db.String(80))
    labeler_correct = db.Column(db.Boolean)
    cells = db.relationship('TrainingImageLabelCell', backref='trainingimagelabel', lazy='dynamic')
    
    def __init__(self, labeler_id="", training_image_id="", date="", time_start="", time_end="", initial_label="", correct_label="", labeler_correct=""):
        self.labeler_id = labeler_id
        self.training_image_id = training_image_id
        self.date = date
        self.time_start = time_start
        self.time_end = time_end
        self.initial_label = initial_label
        self.correct_label = correct_label
        self.labeler_correct = labeler_correct
    
    def __repr__(self):
        return 'Training image ' + str(self.training_image_id) + ', label ' + str(self.id) + ', labeler ' + str(self.labeler)
    
    def __str__(self):
        return 'Training image ' + str(self.training_image_id) + ', label ' + str(self.id) + ', labeler ' + str(self.labeler)

class TrainingImageLabelCell(db.Model):
    __tablename__ = 'trainingimagelabelcell'
    
    id = db.Column(db.Integer, primary_key=True)
    training_image_label_id = db.Column(db.Integer, db.ForeignKey('trainingimagelabel.id'))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    nearest_cell_x = db.Column(db.Float)
    nearest_cell_y = db.Column(db.Float)
    
    def __init__(self, training_image_label_id="", x="", y="", nearest_cell_x="", nearest_cell_y=""):
        self.training_image_label_id = training_image_label_id
        self.x = x
        self.y = y
        self.nearest_cell_x = nearest_cell_x
        self.nearest_cell_y = nearest_cell_y
        
    def __str__(self):
        return 'Marker at ' + str(x) + ', ' + str(y)
