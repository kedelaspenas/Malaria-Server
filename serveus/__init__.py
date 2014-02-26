from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask.ext.thumbnails import Thumbnail
import os

app = Flask(__name__)

app.config.from_object('config')
app.config['MEDIA_FOLDER'] = os.path.realpath(os.path.dirname(__file__)) + '/media'
app.config['MEDIA_URL'] = '/media/'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'cvmig.group.23@gmail.com'
app.config['MAIL_PASSWORD'] = 'prosnaval'
mail = Mail(app)
thumb = Thumbnail(app)
from serveus import views, models, admin
