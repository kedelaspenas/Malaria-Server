from flask.ext.wtf import Form, TextField, PasswordField
from flask.ext.wtf import Required

class LoginForm(Form):
    username = TextField('username', validators = [Required()])
    password = PasswordField('password', validators = [Required()])
    
class RecoveryForm(Form):
    username = TextField('username', validators = [Required()])