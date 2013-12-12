import os
import datetime
import sqlite3

from serveus.models import *
from crowd.models import *

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

# Malaria types
malaria_types = ['Falciparum', 'Vivax', 'Ovale', 'Malariae']
for i in malaria_types:
	for j in xrange(1,5):
		temp = MalType(i, j)
		db.session.add(temp)
		log(temp)

# User types
user_types = ['Administrator', 'Doctor', 'Microscopist']
for user_type in user_types:
	temp = UserType(user_type)
	db.session.add(temp)
	log(temp)

# Region
db.session.add(Region('NCR (National Capital Region)'))
db.session.add(Region('CAR (Cordillera Administrative Region)'))
db.session.add(Region('Region I (Ilocos Region)'))
db.session.add(Region('Region II (Cagayan Valley)'))
db.session.add(Region('Region III (Central Luzon)'))
db.session.add(Region('Region IV-A (CALABARZON)'))
db.session.add(Region('Region IV-B (MIMAROPA)'))
db.session.add(Region('Region V (Bicol Region)'))
db.session.add(Region('Region VI (Western Visayas)'))
db.session.add(Region('Region VII (Central Visayas)'))
db.session.add(Region('Region VIII (Eastern Visayas)'))
db.session.add(Region('Region IX (Zamboanga Peninsula)'))
db.session.add(Region('Region X (Northern Mindanao)'))
db.session.add(Region('Region XI (Davao Region)'))
db.session.add(Region('Region XII (Soccsksargen)'))
db.session.add(Region('Region XIII (Caraga)'))
db.session.add(Region('ARMM (Autonomous Region in Muslim Mindanao)'))

db.session.commit()


# DUMMY DATA

log('dummy data')

# Users
x = []
x.append(User('Rodolfo', User.hash_password('genius123')))
x[-1].usertype_id = 1
x.append(User('Noel', User.hash_password('qwert')))
x[-1].usertype_id = 2
x.append(User('Juancho', User.hash_password('12345')))
x[-1].usertype_id = 3
x.append(User('Marven', User.hash_password('asd')))
x[-1].usertype_id = 3
x.append(User('Jasper', User.hash_password('asd')))
x[-1].usertype_id = 2
x.append(User('Cat', User.hash_password('asd')))
x[-1].usertype_id = 1
for i in x:
    db.session.add(i)

# Cases

x = Case(datetime.date(2010,5,15),20,'El Nido','Vivax',11.2,119.41)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2005,8,26),20,'El Nido','Vivax',11.2,119.41)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2010,5,15),18,'Taytay','Falciparum',10.49,119.31)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2007,1,5),24,'Narra','Ovale',9.17,118.25)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2009,9,9),20,'Taytay','No Malaria',10.42,119.2)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2011,9,9),15," Brooke's Point",'Malariae',8.4,117.2)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2008,9,9),39,'Narra','No Malaria',9.25,118.05)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2012,9,9),45,'Arbolan','Malariae',9.26,118.33)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2013,1,10),12,'San Vicente','Falciparum',10.32,119.17)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2013,9,10),23,'Dumaran','Ovale',10.32,119.46)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2011,5,15),12,"Brooke's Point",'No Malaria',8.47,117.5)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

x = Case(datetime.date(2012,5,9),23,'Cuyo','Vivax',10.51,121.0)
x.region = Region.query.filter(Region.name == 'Region IV-B (MIMAROPA)').first()
db.session.add(x)

# Images
for i in xrange(1,9):
    tmp = Image()
    tmp.create_image('reset_images/' + str(i) + '.jpg', None)
    tmp.case_id = i
    db.session.add(tmp)
log('images')    
    
# CROWDSOURCING START

#LabelerType
db.session.add(LabelerType('Novice'))
db.session.add(LabelerType('Regular'))
db.session.add(LabelerType('Expert'))

#Labeler
# comment out the loop so rodolfo stays as a novice
'''
for i in xrange(1,7):
    db.session.add(Labeler(i,0,0,None,datetime.datetime(2013,12,5,0,0), 1.0, (i%3)+1))
'''
db.session.add(Labeler(1,0,0,None,datetime.datetime(2013,12,5,0,0), 1.0, 1))
db.session.add(Labeler(2,0,0,None,datetime.datetime(2013,12,5,0,0), 1.0, 2))
db.session.add(Labeler(3,0,0,None,datetime.datetime(2013,12,5,0,0), 1.0, 3))
db.session.add(Labeler(4,0,0,None,datetime.datetime(2013,12,5,0,0), 1.0, 2))
db.session.add(Labeler(5,0,0,None,datetime.datetime(2013,12,5,0,0), 1.0, 2))
db.session.add(Labeler(6,0,0,None,datetime.datetime(2013,12,5,0,0), 1.0, 2))

#TrainingImage
for i in xrange(1,9):
    db.session.add(TrainingImage(i,0,'Unlabeled','Unlabeled',None))
'''
#TrainingImageLabel
for i in xrange(1,9):
    for j in range(1,9):
        db.session.add(TrainingImageLabel((j%3)+1, i,datetime.date(2013,12,5),datetime.time(j,j), datetime.time(j,j+2),1, None, None))

#TrainingImageLabelCell
for i in xrange(1,9):
    for j in xrange(1,9):
        for k in xrange(1,9):
            db.session.add(TrainingImageLabelCell(j,k*100,k*100, None,None))
'''
log('dummy crowdsourcing data')
# CROWDSOURCING END

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
