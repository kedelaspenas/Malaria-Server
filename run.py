import sys
import socket
from serveus import app

port = 5000
if len(sys.argv) > 1 and sys.argv[1]:
	port = int(sys.argv[1])
print ' * IP: ' + socket.gethostbyname(socket.gethostname()) + ':' + str(port)
app.run('0.0.0.0', port=port, debug = True)
