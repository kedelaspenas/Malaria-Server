from serveus import app
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView

from models import db, User, UserType, Case

admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(UserType, db.session))
admin.add_view(ModelView(Case, db.session))