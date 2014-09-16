import os, time, sys, logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)

# CONFIG
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.getcwd().replace('\\','/')+ '/cs198pythontest.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'cvmig.group.23@gmail.com'
app.config['MAIL_PASSWORD'] = 'prosnaval'
mail = Mail(app)
db = SQLAlchemy(app)

# MIGRATION
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# LOGGING
DATE_INIT = time.strftime("%Y-%m-%d")
TIME_INIT = time.strftime("%H.%M.%S")
LOG_FILE = os.path.join(app.config['BASE_DIR'], "logs", DATE_INIT, TIME_INIT + ".log")

try:
    os.mkdir(os.path.join(app.config['BASE_DIR'], "logs", time.strftime("%Y-%m-%d")))
except OSError:
    pass
    
class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
 
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
        
    def flush(self):
        self.logger.flush()
         

logging.basicConfig(
   level=logging.DEBUG,
   format='> %(message)s',
   stream=sys.stderr
)

formatter = logging.Formatter("> %(message)s")
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount = 5)
file_handler.setFormatter(formatter) 
root = logging.getLogger('')
sys.stderr = StreamToLogger(root, logging.INFO)
root.addHandler(file_handler)

try:
    root.log(logging.DEBUG, "Initialized logger")
except IOError as e:
    # Remove stderr logger if console is hidden. Print statements will not be logged
    root.removeHandler(root.__dict__['handlers'][0])

from crowd import crowd
app.register_blueprint(crowd)    
# IMPORT PARTS OF APP
from serveus import views, models, admin

