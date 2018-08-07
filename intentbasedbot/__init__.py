#!/usr/bin/env python3
from flask import Flask
import os
import warnings

app = Flask(__name__)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import intentbasedbot.controllers

# TODO Obsolete with Flask CLI?
# Running without flask command
if __name__ == "__main__":
	###################################### Environment variables ######################################
	FLASK_PORT = int(os.environ.get('FLASK_PORT')) if os.environ.get('FLASK_PORT') else 5000
	DEBUG = bool(os.environ.get('DEBUG')) if os.environ.get('DEBUG') else True	

	print('Running from script')
	app.run(host='0.0.0.0', port=FLASK_PORT, debug=DEBUG)