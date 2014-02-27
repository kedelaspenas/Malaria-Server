import os
import datetime
import hashlib
from sqlalchemy.orm import validates
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy, models_committed
from flask.ext.login import UserMixin
from flask_mail import Message

from serveus import app, mail

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.getcwd().replace('\\','/')+ '/cs198pythontest.db'
db = SQLAlchemy(app)

class UserType(db.Model):
	__tablename__ = 'usertype'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True)
	users = db.relationship('User', backref='usertype', lazy='dynamic')

	@staticmethod
	def get_administrator():
		return UserType.query.filter(UserType.name=='Administrator').first()

	@staticmethod
	def get_microscopist():
		return UserType.query.filter(UserType.name=='Medical Technician').first()

	@staticmethod
	def get_doctor():
		return UserType.query.filter(UserType.name=='Validator').first()
	
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
	firstname = db.Column(db.String(100))
	lastname = db.Column(db.String(100))
	usertype_id = db.Column(db.Integer, db.ForeignKey('usertype.id'))
	case =  db.relationship('Case', backref='user', lazy='dynamic')
	contact = db.Column(db.String(80))
	email = db.Column(db.String(80), unique=True)
	chunklists = db.relationship('Chunklist', backref='user', lazy='dynamic')

	"""
	@models_committed.connect_via(app)
	def on_models_committed(sender, changes):
		for obj, method in changes:
			if method == 'insert' and type(obj) == User:
				body = '''Greetings, %s %s! You have successfully been registered to the system. Your temporary password is <b>%s</b>.<br><br>Below are your account details:<br><br>Username: %s<br>User type: %s<br>Contact number: %s<br>Email: %s<br><br>Please login and change your password. Thank you!''' % (obj.firstname, obj.lastname, '123', obj.username, obj.usertype, obj.contact, obj.email)
				msg = Message('Outbreak Monitoring', sender="cvmig.group.23@gmail.com", recipients=['generic@mailinator.com',obj.email])
				msg.html = body
				mail.send(msg)
	"""


	@validates('password')
	def update_password(self, key, value):
		Database.query.first().modified = datetime.datetime.now()
		return value

	@staticmethod
	def hash_password(password):
		return hashlib.sha1(password).hexdigest()

	def is_administrator(self):
		return self.usertype == UserType.get_administrator()

	def is_microscopist(self):
		return self.usertype == UserType.get_microscopist()

	def is_doctor(self):
		return self.usertype == UserType.get_doctor()

	def __init__(self, firstname="", lastname="", username="", password="", contact="", email=""):
		self.firstname = firstname
		self.lastname = lastname
		self.username = username
		self.password = password
		self.contact = contact
		self.email = email

	def __repr__(self):
		return '<User %r %r (%r)>' % (self.firstname, self.lastname, self.username)
		
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
	test = db.Column(db.Boolean)
	region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
	province_id = db.Column(db.Integer, db.ForeignKey('province.id'))
	municipality_id = db.Column(db.Integer, db.ForeignKey('municipality.id'))
	parasite_validator = db.Column(db.String(100))
	description_validator = db.Column(db.String(1000))

	def __init__(self, date="", parasite="", description="", lat="", lng="", test="", region="", province="", municipality=""):
		self.date = date
		self.parasite = parasite
		self.description = description
		self.lat = lat
		self.lng = lng
		if region == '':
			self.region = None
		else:
			self.region = region
			#self.region = Region.query.filter(Region.name==region).first()
		if province == '':
			self.province = None
		else:
			self.province = province
			#self.province = Province.query.filter(Province.name==province).first()
		if municipality == '':
			self.municipality = None
		else:
			self.municipality = municipality
			#self.municipality = Municipality.query.filter(Municipality.name==municipality).first()
		self.test = test

	def __repr__(self):
		return '<Case %r>' % self.id

	def __str__(self):
		return str(self.id)

class Image(db.Model):
	__tablename__ = 'image'

	id = db.Column(db.Integer, primary_key=True)
	case_id = db.Column(db.Integer, db.ForeignKey('case.id'))
	im = db.Column(db.BLOB)
	number = db.Column(db.Integer)
	
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

class Chunklist(db.Model):
	__tablename__ = 'chunklist'

	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(100))
	date = db.Column(db.DateTime())
	chunks = db.relationship('Chunk', backref='chunklist', lazy='dynamic')
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(self, filename='', date='', user_id=''):
		self.filename = filename
		self.date = date
		self.user_id = user_id
	
	def __repr__(self):
		return self.filename

class Chunk(db.Model):
	__tablename__ = 'chunk'

	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(100))
	checksum = db.Column(db.String(50))
	done = db.Column(db.Boolean())
	chunklist_id = db.Column(db.Integer, db.ForeignKey('chunklist.id'))

	def __init__(self, filename='', checksum='', user=''):
		self.filename = filename
		self.checksum = checksum
		self.user = user
		self.done = False
		self.data = None
	
	def __repr__(self):
		return self.filename

class Region(db.Model):
	__tablename__ = 'region'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	code = db.Column(db.String(10))
	cases = db.relationship('Case', backref='region', lazy='dynamic')
	provinces = db.relationship('Province', backref='region', lazy='dynamic')

	def __init__(self, name='', code=''):
		self.name = name
		self.code = code
	
	def __repr__(self):
		return self.name

class Province(db.Model):
	__tablename__ = 'province'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	code = db.Column(db.String(10))
	cases = db.relationship('Case', backref='province', lazy='dynamic')
	municipalities = db.relationship('Municipality', backref='province', lazy='dynamic')
	region_id = db.Column(db.Integer, db.ForeignKey('region.id'))

	def __init__(self, name='', code=''):
		self.name = name
		self.code = code
	
	def __repr__(self):
		return self.name

	@property
	def serialize(self):
		return {'id': self.id, 'name': self.name}

class Municipality(db.Model):
	__tablename__ = 'municipality'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	cases = db.relationship('Case', backref='municipality', lazy='dynamic')
	province_id = db.Column(db.Integer, db.ForeignKey('province.id'))

	def __init__(self, name=''):
		self.name = name
	
	def __repr__(self):
		return self.name

	@property
	def serialize(self):
		return {'id': self.id, 'name': self.name}
