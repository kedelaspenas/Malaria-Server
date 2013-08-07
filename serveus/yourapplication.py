from flask import Flask
import os
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
        self.name=name
    
    def __repr__(self):
        return '<UserType %r>' % self.name

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120), unique=True)
    usertype_id= db.Column(db.Integer,db.ForeignKey('usertype.id'))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date())
    age = db.Column(db.Integer)
    address = db.Column(db.String(120))
    human_diagnosis = db.Column(db.String(80))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    maltype_id = db.Column(db.Integer, db.ForeignKey('maltype.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
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
    level = db.Column(db.Integer)
    cases = db.relationship('Case',backref='maltype',lazy='dynamic')
    def __init__(self,type, level):
        self.type = type
        self.level = level
class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key= True)
    images= db.relationship('Case',backref='image',lazy ='dynamic')
    im = db.Column(db.BLOB)