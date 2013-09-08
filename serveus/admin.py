from serveus import app
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.wtf import PasswordField
from flask.ext.login import current_user

from models import db, User, UserType, Case, MalType

# Custom admin index

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated()

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated()
        
admin = Admin(app, index_view=MyAdminIndexView())

# Custom admin pages
# More info in https://github.com/mrjoes/flask-admin/issues/173
class UserView(MyModelView):
    can_create = True
    column_list = ('username', 'usertype')
    column_excluded_list = ('password')
    #column_searchable_list = ('username')
    
    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        form_class.password = PasswordField()
        return form_class
        
    def on_model_change(self, form, model):
        if len(model.password):
            model.password = User.hash_password(form.password.data)
            
# Add pages to the admin page
#admin.add_view(ModelView(User, db.session))
admin.add_view(MyModelView(UserType, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(MyModelView(Case, db.session))
admin.add_view(MyModelView(MalType, db.session))