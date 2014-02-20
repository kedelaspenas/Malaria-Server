import os
import datetime
import hashlib
from sqlalchemy.orm import validates
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin

from serveus import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.getcwd().replace('\\','/')+ '/cs198pythontest.db'
db = SQLAlchemy(app)

class UserType(db.Model):
    __tablename__ = 'usertype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    users = db.relationship('User', backref='usertype', lazy='dynamic')
    
    def __init__(self, name=""):
        self.name = name
    
    def __repr__(self):
        return '<UserType %r>' % self.name
        
    def __str__(self):
        return self.name

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    usertype_id = db.Column(db.Integer, db.ForeignKey('usertype.id'))
    case =  db.relationship('Case', backref='user', lazy='dynamic')
    contact = db.Column(db.String(80))

    @validates('password')
    def update_password(self, key, value):
        Database.query.first().modified = datetime.datetime.now()
        return value

    @staticmethod
    def hash_password(password):
        return hashlib.sha1(password).hexdigest()

    def __init__(self, username="", password="", contact=""):
        self.username = username
        self.password = password
        self.contact = contact

    def __repr__(self):
        return '<User %r>' % self.username
        
    def __str__(self):
        return self.username

class Case(db.Model):
    __tablename__ = 'case'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime())
    parasite = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    comment = db.Column(db.String(1000))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    images = db.relationship('Image', backref='case', lazy='dynamic')

    def __init__(self, date="", parasite="", description="", lat="", lng=""):
        self.date = date
        self.parasite = parasite
        self.description = description
        self.lat = lat
        self.lng = lng

    def __repr__(self):
        return '<Case %r>' % self.id

    def __str__(self):
        return str(self.id)

class Image(db.Model):
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'))
    im = db.Column(db.BLOB)
    
    '''
    def __init__(self, path="", case=""):
        with open(path, 'r') as f:
            self.im = f.read()
        self.case = case
    '''
    def create_image(self, path="", case=""):
        with open(path, 'rb') as f:
            self.im = f.read()
        self.case = case

    def __repr__(self):
        return '<Image %r>' % self.id

class Database(db.Model):
    __tablename__ = 'database'

    id = db.Column(db.Integer, primary_key=True)
    modified = db.Column(db.DateTime())

    def __init__(self):
        self.modified = datetime.datetime.now()
    
    @staticmethod
    def need_update(app_db_date):
        year, month, day, hours, minutes, seconds = map(int, app_db_date.split('-'))
        return Database.query.first().modified > datetime.datetime(year, month, day, hours, minutes, seconds)

    def __repr__(self):
        return '<Database %r>' % self.id

class Key(db.Model):
    __tablename__ = 'key'

    id = db.Column(db.Integer, primary_key=True)
    private_key = db.Column(db.String(2000))
    public_key = db.Column(db.String(2000))

    def __init__(self, private_key, public_key):
        self.private_key = private_key
        self.public_key = public_key
    
    def __repr__(self):
        return str(self.public_key)
