import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin

from serveus import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.getcwd().replace('\\','/')+ '/cs198pythontest.db'
print 'sqlite:///'+os.getcwd().replace('\\','/')+ '/cs198pythontest.db'

db = SQLAlchemy(app)

class UserType(db.Model):
    __tablename__ = 'usertype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    users = db.relationship('User', backref='usertype', lazy='dynamic')
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return '<UserType %r>' % self.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120), unique=True)
    usertype_id= db.Column(db.Integer, db.ForeignKey('usertype.id'))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime())
    age = db.Column(db.Integer)
    address = db.Column(db.String(120))
    human_diagnosis = db.Column(db.String(80))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    maltype_id = db.Column(db.Integer, db.ForeignKey('maltype.id'))
    images = db.relationship('Image', backref='case', lazy='dynamic')

    def __init__(self, date, age, address, human_diagnosis, lat, lng):
        self.date = date
        self.age = age
        self.address = address
        self.human_diagnosis = human_diagnosis
        self.lat = lat
        self.lng = lng

    def __repr__(self):
        return '<User %r>' % self.id

class MalType(db.Model):
    __tablename__ = 'maltype'

    id = db.Column(db.Integer, primary_key= True)
    type = db.Column(db.String(80))
    stage = db.Column(db.Integer)
    cases = db.relationship('Case', backref='maltype', lazy='dynamic')

    def __init__(self, type, stage):
        self.type = type
        self.stage = stage
	
	def __repr__(self):
		return '<MalType %r>' % self.type

class Image(db.Model):
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'))
    im = db.Column(db.BLOB)

    def __init__(self, path, case):
		with open(path, 'r') as f:
			self.im = f.read()
		self.case = case

# TODO: temporary table; remove when keys are synced with accounts
class Key(db.Model):
	__tablename__ = 'key'

	id = db.Column(db.Integer, primary_key=True)
	private_key = db.Column(db.String(2000))
	public_key = db.Column(db.String(2000))

	def __init__(self, private_key, public_key):
		self.private_key = private_key
		self.public_key = public_key
