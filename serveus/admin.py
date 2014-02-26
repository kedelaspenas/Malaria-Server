from serveus import app
from flask.ext.admin import Admin, AdminIndexView, expose
from flask.ext.admin.base import MenuLink
from flask.ext.admin.contrib.sqlamodel import ModelView
#from flask.ext.wtf import PasswordField
from wtforms import PasswordField, FileField
from flask.ext.login import current_user
from flask import request
from jinja2 import Markup

from models import db, User, UserType, Case, Image, Chunk, Chunklist, Region, Province, Municipality
from views import dashboard

# Custom admin links on navbar

class AuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated()

# Custom admin pages
        
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        admin = UserType.query.filter(UserType.name == 'Administrator').first()
        return current_user.is_authenticated() and current_user.usertype == admin
    @expose('/')
    def index(self):
        return self.render('admin.html', username = current_user.username)

class MyModelView(ModelView):
    def is_accessible(self):
        admin = UserType.query.filter(UserType.name == 'Administrator').first()
        return current_user.is_authenticated() and current_user.usertype == admin

admin = Admin(app, index_view=MyAdminIndexView())

# Custom admin pages
# More info in https://github.com/mrjoes/flask-admin/issues/173
class UserView(MyModelView):
    can_create = True
    column_list = ('username', 'usertype')
    form_excluded_columns = ('case', 'chunklists')
    column_excluded_list = ('password')
    
    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        form_class.password = PasswordField()
        return form_class
        
    def on_model_change(self, form, model):
        if len(model.password):
            model.password = User.hash_password(form.password.data)
            
class ImageView(MyModelView):
    can_create = True
    can_edit = False
    column_list = ('id', 'case_id')
    column_labels = dict(id='ID', case_id='Case')
    column_exclude_list = ('im')
    
    def scaffold_form(self):
        form_class = super(ImageView, self).scaffold_form()
        form_class.im = FileField()
        return form_class
        
    def on_model_change(self, form, model):
        temp = request.files[form.im.name].read()
        if temp:
            model.im = temp
        
    def _image_link(view, context, model, name):
        return Markup(
            '<a href="/pic/%s">%s</a>' % (model.id, model.id)
        ) if model.id else ""

    def _image_view(view, context, model, name):
        return Markup(
            '<a href="/pic/%s/"><img src="/pic/%s/" style="width: 100px; height: 100px"/></a>' % (model.id, model.id)
        ) if model.im else ""
    column_formatters = { 'id': _image_view }
            
# Add pages to the admin page
admin.add_view(MyModelView(UserType, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(MyModelView(Case, db.session))
admin.add_view(ImageView(Image, db.session))
admin.add_view(MyModelView(Chunklist, db.session))
admin.add_view(MyModelView(Chunk, db.session))
admin.add_view(MyModelView(Region, db.session))
admin.add_view(MyModelView(Province, db.session))
admin.add_view(MyModelView(Municipality, db.session))

# Navbar links
admin.add_link(AuthenticatedMenuLink(name='Back to Website', endpoint='monitoring'))
