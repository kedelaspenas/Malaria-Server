import os
import datetime
import sqlite3

from serveus.models import *

if os.path.isfile('cs198pythontest.db'):
	os.remove('cs198pythontest.db')

if os.path.isfile('updated.db'):
	os.remove('updated.db')

db.create_all()

OUTPUT_LOG = True
def log(s):
	if OUTPUT_LOG:
		print 'Added', str(s)

# DEFAULT VALUES

# Database
temp = Database()
db.session.add(temp)
db.session.commit()
log(temp)

# Updated database
conn = sqlite3.connect('updated.db')
c = conn.cursor()
c.execute('''CREATE TABLE user (id INTEGER NOT NULL, username VARCHAR(80), password VARCHAR(80), PRIMARY KEY (id), UNIQUE (username))''')
conn.commit()
conn.close()

# User types
user_types = ['Administrator', 'Doctor', 'Microscopist']
for user_type in user_types:
	temp = UserType(user_type)
	db.session.add(temp)
	log(temp)

db.session.commit()


# DUMMY DATA

log('dummy data')

# Users
x = []
x.append(User('Rodolfo', 'Kirong', 'Rodolfo', User.hash_password('genius123'), '0912-345-6789', 'rodolfo@mailinator.com'))
x[-1].usertype_id = 1
x.append(User('Noel', 'Sison', 'Noel', User.hash_password('qwert'), '0912-345-6789', 'noel@mailinator.com'))
x[-1].usertype_id = 2
x.append(User('Juancho', 'Coronel', 'Juancho', User.hash_password('12345'), '0912-345-6789', 'juancho@mailinator.com'))
x[-1].usertype_id = 1
x.append(User('Marven', 'Sanchez', 'Marven', User.hash_password('asd'), '0912-345-6789', 'marven@mailinator.com'))
x[-1].usertype_id = 3
x.append(User('Jasper', 'Cacbay', 'Jasper', User.hash_password('asd'), '0912-345-6789', 'jasper@mailinator.com'))
x[-1].usertype_id = 2
x.append(User('Cat', 'Angangco', 'Cat', User.hash_password('asd'), '0912-345-6789', 'cat@mailinator.com'))
x[-1].usertype_id = 1
for i in x:
    db.session.add(i)

# Cases

x = Case(datetime.date(2010,5,15),'Vivax','Description',11.2,119.41,'Palawan')
x.user_id = 1
db.session.add(x)

x = Case(datetime.date(2005,8,26),'Vivax','Description',11.2,119.41,'Palawan')
x.user_id = 2
db.session.add(x)

x = Case(datetime.date(2010,5,15),'Falciparum','Description',10.49,119.31,'Palawan')
x.user_id = 3
db.session.add(x)

x = Case(datetime.date(2007,1,5),'Ovale','Description',9.17,118.25,'Palawan')
x.user_id = 4
db.session.add(x)

x = Case(datetime.date(2009,9,9),'No Disease','Description',10.42,119.2,'Palawan')
x.user_id = 5
db.session.add(x)

x = Case(datetime.date(2011,9,9),'Malariae','Description',8.4,117.2,'Palawan')
x.user_id = 6
db.session.add(x)

x = Case(datetime.date(2008,9,9),'No Disease','Description',9.25,118.05,'Palawan')
x.user_id = 1
db.session.add(x)

x = Case(datetime.date(2012,9,9),'Malariae','Description',9.26,118.33,'Palawan')
x.user_id = 2
db.session.add(x)

x = Case(datetime.date(2013,1,10),'Falciparum','Description',10.32,119.17,'Palawan')
x.user_id = 3
db.session.add(x)

x = Case(datetime.date(2013,9,10),'Ovale','Description',10.32,119.46,'Palawan')
x.user_id = 4
db.session.add(x)

x = Case(datetime.date(2011,5,15),'No Disease','Description',8.47,117.5,'Palawan')
x.user_id = 5
db.session.add(x)

x = Case(datetime.date(2012,5,9),'Vivax','Description',10.51,121.0, 'Palawan')
x.user_id = 6
db.session.add(x)

x = Case(datetime.date(2014,2,19),'Malariae','Severe',14.565454,120.993973, 'Manila')
x.user_id = 6
db.session.add(x)

x = Case(datetime.date(2014,2,19),'Malariae','Severe',14.565454,120.993973,'Manila')
x.user_id = 6
db.session.add(x)

x = Case(datetime.date(2014,2,10),'Malariae','Severe',14.565454,120.993973, 'Manila')
x.user_id = 6
db.session.add(x)

x = Case(datetime.date(2014,2,17),'Malariae','Severe',14.64836399, 121.0684764, 'Quezon City')
x.user_id = 6
db.session.add(x)

x = Case(datetime.date(2014,2,18),'Malariae','Severe',14.64836399, 121.0684764, 'Quezon City')
x.user_id = 6
db.session.add(x)

x = Case(datetime.date(2014,2,19),'Malariae','Severe',14.64836399, 121.0684764, 'Quezon City')
x.user_id = 6
db.session.add(x)

x = Case(datetime.date(2014,2,19),'Malariae','Severe',14.639946,121.0781, 'Quezon City')
x.user_id = 6
db.session.add(x)

# Images
for i in xrange(1,9):
    tmp = Image()
    tmp.create_image('reset_images/' + str(i) + '.jpg', None)
    tmp.case_id = i
    db.session.add(tmp)
log('images')    

# TODO: remove when keys are synced with accounts
"""
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES

private_key = RSA.generate(1024)
public_key = private_key.publickey()
private_key = private_key.exportKey()
public_key = public_key.exportKey().replace('-----BEGIN PUBLIC KEY-----','').replace('-----END PUBLIC KEY-----','').replace('\n','')
db.session.add(Key(private_key, public_key))
"""
#public_key = """MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbMiQNyj/Nzj7QQBj8nAx3WKPy4r72Onnw/E9KQY1gUwepRtCKYgJz9typvvfi7zNROFp5o8OBL5mVWFShxMIh57entYRpZUGtTZtb7YT5Bx3ZM5FPKQzHcJDyPJFloJW6V0+jmmZSosvM4nrZknVW3DABdmiVadGXtdy9DNevyQIDAQAB"""
public_key = """009b32240dca3fcdce3ed04018fc9c0c7758a3f2e2bef63a79f0fc4f4a418d605307a946d08a620273f6dca9bef7e2ef3351385a79a3c3812f99955854a1c4c221e7b7a7b584696541ad4d9b5bed84f9071dd933914f290cc77090f23c9165a095ba574fa39a6652a2cbcce27ad9927556dc300176689569d197b5dcbd0cd7afc9"""
private_key = """-----BEGIN RSA PRIVATE KEY-----\nMIICXQIBAAKBgQCbMiQNyj/Nzj7QQBj8nAx3WKPy4r72Onnw/E9KQY1gUwepRtCK\nYgJz9typvvfi7zNROFp5o8OBL5mVWFShxMIh57entYRpZUGtTZtb7YT5Bx3ZM5FP\nKQzHcJDyPJFloJW6V0+jmmZSosvM4nrZknVW3DABdmiVadGXtdy9DNevyQIDAQAB\nAoGAF7J9TNnAClXew3+2EQRm5uZTCmhTDlf5fLGaDdWal8W12sQkXaz/gOOF6Clv\nwmgR5un67q3x0U0KX4KAUb8wgS2wlkWYlT062+mE7cYKZh07ZxCFy+yrfM6qRrvA\nHJPa60TTAQTRXSeoX9DrWHld+JVKml74vV3oQSThdgj70d0CQQC1Ei48dhfmCurY\nsVPjHR6Sx0URqtHvZMHJrW1eMa0X0QHSs9iSXFZmQGD5qprQBjNmMrQe8zd4Uwto\ntPMnPSxjAkEA22rd7deGlaWaaTosMF12ikzMd1KP42IK+BWMIh6HfoXcxj7H1pQ7\nS7oSNgqqIojgGLZfIc9bKfa0sSp6GE+c4wJBAKd2vRRmFAxKJJFsz6zJDbGqYpLI\nbYj+osunffMT9oaEYy8/7hjPFYlUGVxPEQc79OWcF0JYpwC9rVuVnxy3UwkCQQCw\nnCk8OyGyLFTIZDGTUHeMxFpDpSn6PT1VCIr+H5KyLW9SBtB1kGTWBFSKOTVOjNvM\nKGcUYMIhWdmBTQ5vqQ0/AkAx2XcV90V/6i89F2SElT3OcQsjznPJ58TupP5Ckr6l\n3i8SY+/pip4zPV0/gdS21VbaOEvwxaVOUcm1anNmBmRs\n-----END RSA PRIVATE KEY-----"""
db.session.add(Key(private_key, public_key))

# COMMIT
db.session.commit()
