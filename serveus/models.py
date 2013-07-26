from serveus import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), index = True, unique = True)
    password = db.Column(db.String(50), index = True, unique = False)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    
    def __repr__(self):
        return self.username + ' ' + self.password