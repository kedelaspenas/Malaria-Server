import logging
import os, sys
from logging.handlers import RotatingFileHandler
from serveus import app, manager, LOG_FILE

LOG_FILE = os.path.abspath(os.path.dirname(__file__)) + "/" + LOG_FILE

class StreamToLogger(object):
   def __init__(self, logger, file_handler, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
 
   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())
         

if __name__ == '__main__':
    logging.basicConfig(
       level=logging.DEBUG,
       format='%(message)s',
       stream=sys.stderr
    )
    
    formatter = logging.Formatter("%(message)s")
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount = 5)
    file_handler.setFormatter(formatter) 
    
    sys.stdout  = StreamToLogger(logging.getLogger('STDOUT'), file_handler, logging.INFO)
    
    root = logging.getLogger('')
    root.addHandler(file_handler)

    manager.run();
