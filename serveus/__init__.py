import os, time
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

LOG_FILE = "logs/" + time.strftime("%Y-%m-%d %H.%M.%S") + ".log"

app = Flask(__name__)

app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.getcwd().replace('\\','/')+ '/cs198pythontest.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'cvmig.group.23@gmail.com'
app.config['MAIL_PASSWORD'] = 'prosnaval'
mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from serveus import views, models, admin

