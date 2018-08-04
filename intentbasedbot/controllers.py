#!/usr/bin/env python3
# Main packages of the application
from intentbasedbot import app
from intentbasedbot import facebook as fb
from intentbasedbot import intents
from intentbasedbot.config import *

# System
import time
from datetime import datetime

# Logging
import colors
from rfc3339 import rfc3339

# Flask
from flask import request, abort, jsonify, g

# For disable logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

@app.route("/", methods=['GET'])
def hello():
	return jsonify(message="Hello I'm a Facebook Bot!")


@app.route(WEBHOOK_URI, methods=['GET'])
def verify_webhook():
	"""
		Before allowing people to message your bot, Facebook has implemented a verify token that confirms all requests
		that your bot receives came from Facebook.
	"""	
	mode = request.args.get("hub.mode")
	token = request.args.get("hub.verify_token")
	challenge = request.args.get("hub.challenge")	

	# jsonify() not accepted by Facebook
	return fb.verify_token(mode, token, challenge)


@app.route(WEBHOOK_URI, methods=['POST'])
def receive_message():
	""" We will receive messages that Facebook sends our bot at this endpoint """

	# Get whatever message a user sent the bot
	payload = request.get_json()

	# TODO For debugging purposes
	# app.logger.info(f'Payload received in webhook {payload}')

	# Checking page subscription from Fanpage
	if not payload.get('object') and payload.get('object') != 'page':
		app.logger.error('Unknow object type')
		abort(404, jsonify(status='unknow_object_type'))

	# Checking amount of events
	if payload.get('entry') and len(payload.get('entry')) == 0:
		app.logger.error('No entries in this message')
		abort(404, jsonify(status='no_entries'))

	# Array of events received in the webhook
	for event in payload['entry']:
		####### 'messages' channel #######
		# This Bot is in control - listen for messages
		if event.get('messaging'):
			app.logger.info("I'm listening in 'messages' channel")
			# Array of messages, only one by now
			for message in event['messaging']:
				fb.decode_messaging(message, 'messaging')

		####### 'standby' channel #######
		# Secondary Receiver is in control - listen on standby channel
		# Same criteria of messaging for decoding
		if event.get('standby'):
			app.logger.info("I'm listening in 'standby' channel")
			# Array of messages, only one by now
			for message in event['standby']:
				fb.decode_messaging(message, 'standby')

		# TODO Same wrapper of messaging
		# if event['postback']:
		# 	fb.handle_post_back()

	return jsonify(status='message_processed', events=len(payload['entry']))

@app.route("/intents", methods=['POST'])
def predict_intent():
	"""
		Predicts the intent of the utterance, based on our model.
		This endpoint is for expose the model results.
	"""
	payload = request.get_json()
	utterance = payload.get('utterance')

	if utterance:
		return jsonify(intents.consume_model(utterance))
	else:
		abort(404, jsonify(message='Missing utterance for predict'))

# # For beautiful logging
# @app.before_request
# def start_timer():
# 	g.start = time.time()

# # For beautiful logging
# @app.after_request
# def log_request(response):
# 	if request.path == '/favicon.ico':
# 		return response
# 	elif request.path.startswith('/static'):
# 		return response
#
# 	now = time.time()
# 	duration = round(now - g.start, 2)
# 	dt = datetime.fromtimestamp(now)
# 	timestamp = rfc3339(dt, utc=True)
#
# 	ip = request.headers.get('X-Forwarded-For', request.remote_addr)
# 	host = request.host.split(':', 1)[0]
# 	args = dict(request.args)
#
# 	log_params = [
# 		('method', request.method, 'blue'),
# 		('path', request.path, 'blue'),
# 		('status', response.status_code, 'yellow'),
# 		('duration', duration, 'green'),
# 		('time', timestamp, 'magenta'),
# 		('ip', ip, 'red'),
# 		('host', host, 'red'),
# 		('params', args, 'blue')
# 	]
#
# 	request_id = request.headers.get('X-Request-ID')
# 	if request_id:
# 		log_params.append(('request_id', request_id, 'yellow'))
#
# 	parts = []
# 	for name, value, color in log_params:
# 		part = colors.color("{}={}".format(name, value), fg=color)
# 		parts.append(part)
# 	line = " ".join(parts)
#
# 	app.logger.info(line)
#
# 	return response