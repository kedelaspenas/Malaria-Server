'''import os
os.remove('cs198pythontest.db')'''

from serveus.yourapplication import *
from datetime import date
db.create_all()
db.session.add(User('Rodolfo','genius123'))
db.session.add(User('Noel','qwert'))
db.session.add(User('Juancho','12345'))
db.session.commit()