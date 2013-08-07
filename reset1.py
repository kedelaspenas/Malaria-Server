import os
os.remove('cs198pythontest.db')

from serveus.yourapplication import *
import datetime
db.create_all()
db.session.add(User('Rodolfo','genius123'))
db.session.add(User('Noel','qwert'))
db.session.add(User('Juancho','12345'))


db.session.add(Case(datetime.date(2005,8,26),20,'NCR (National Capital Region) Manila City','Vivax',14.58,121))
db.session.add(Case(datetime.date(2010,5,15),18,'CAR (Cordillera Administrative Region) Baguio City','Falciparum',16.42,120.6))
db.session.add(Case(datetime.date(2007,1,5),24,'NCR (National Capital Region) Quezon City','Ovale',14.67,121))
db.session.commit()

