import sys

from serveus import app

port = 5000
if len(sys.argv) > 1 and sys.argv[1]:
	port = int(sys.argv[1])
app.run('0.0.0.0', port=port, debug = True)
