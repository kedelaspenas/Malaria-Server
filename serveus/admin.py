from serveus import app
from flask.ext.admin import Admin, AdminIndexView, expose
from flask.ext.admin.base import MenuLink
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
#from flask.ext.wtf import PasswordField
from wtforms import PasswordField, FileField
from flask.ext.login import current_user
from flask import request
from jinja2 import Markup
from flask.ext.admin.actions import action
from flask import redirect, url_for
import os, webbrowser


from models import db, User, UserType, Case, Image, Chunk, Chunklist, Region, Province, Municipality, ParType, Validation
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
    column_list = ('username', 'usertype', 'firstname', 'lastname', 'contact', 'email', 'Download Images')
    form_excluded_columns = ('case', 'chunklists')
    column_excluded_list = ('password')
    
    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        form_class.password = PasswordField()
        return form_class
        
    def on_model_change(self, form, model):
        if len(model.password):
            model.password = User.hash_password(form.password.data)
            
    def _download_column(view, context, model, name):
        hasImages = False;
        for c in User.query.get(model.id).case:
            for i in c.images:
                hasImages = True
                break
            if hasImages:
                break
        return Markup(
            '<a href="/download/?user=%s">Download</a>' % model.id
        ) if hasImages else "No images"
    column_formatters = { 'Download Images': _download_column }
            
class ImageView(MyModelView):
    can_create = True
    can_edit = True
    column_list = ('id', 'case_id', 'number')
    column_labels = dict(id='ID', case_id='Case')
    column_exclude_list = ('im')
    
    @action('open','Open')
    def action_open(self,ids):
        tempids=""
        for i in ids:
            #tempids= tempids + "window.open(\"/pic/"+ str(Image.query.get(i).id) + ");"
            tempids=tempids + '<a href=\"/pic/'+ str(Image.query.get(i).id) + '\" class =\"imlink\" target =\"_blank\"></a>'
        print tempids
        return Markup( '  %s <script> var l= document.getElementsByClassName("imlink"); \
        for (var i=0;i<l.length; i++) {l[i].click();}       </script>  ' % tempids)
        
    @action('download','Download')
    def action_download(self,ids):
        tempids=""
        for i in ids:
            tempids= tempids + str(Image.query.get(i).id)+'|'
        return redirect('/downloadselected?ids=' + tempids)
    
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
            '<a href="/pic/%s/" ><img src="/thumb/pic/%s/" class="thumbnail pull-left" style="width: 160px; height: 120px"/></a>' % (model.id, model.id)
        ) if model.im else ""
    column_formatters = { 'id': _image_view }
    
log_path = os.path.join(app.config['BASE_DIR'], "logs")
            
# Add pages to the admin page
admin.add_view(MyModelView(UserType, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(MyModelView(Case, db.session))
admin.add_view(ImageView(Image, db.session))
admin.add_view(MyModelView(ParType, db.session))
admin.add_view(MyModelView(Chunklist, db.session))
admin.add_view(MyModelView(Chunk, db.session))
admin.add_view(MyModelView(Region, db.session))
admin.add_view(MyModelView(Province, db.session))
admin.add_view(MyModelView(Municipality, db.session))
admin.add_view(MyModelView(Validation, db.session))
admin.add_view(FileAdmin(log_path, '/log/', name='Logs', url="/admin/logview"))

# Navbar links
admin.add_link(AuthenticatedMenuLink(name='Back to Website', endpoint='monitoring'))
