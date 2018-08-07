#!/usr/bin/env python3
# Main packages of the application
from intentbasedbot import app
from intentbasedbot.config import *
from intentbasedbot import model

# SciPy
import numpy as np

# Web
import requests as req

def get_intent(text) -> str:
	""" Consume external APIs and our model """
	response = ''
	intents = []

	if USE_WIT:
		intents += consume_wit(text)

	if USE_MODEL:
		intents.append(consume_model(text))

	for intent in intents:
		intent_detected = intent['intent']
		intent_confidence = round(intent['confidence'] * 100, 2)
		# intent_entity = intent.get('_entity') # Another interesting field in WIT
		app.logger.info(f'Intent detected {intent_detected} {intent_confidence}')
		response += f'Me estas preguntando sobre "{intent_detected}" {intent_confidence}%'

	return response

def consume_wit(text) -> list:
	app.logger.info(f'Consuming wit with {text}')
	params = {'v': WIT_VERSION, 'q': text, 'verbose': True, 'n': 2}
	endpoint = 'https://api.wit.ai/message'

	response = req.get(endpoint, params=params, headers=WIT_HEADERS,)
	return response.json()['entities'].get('intent')

def consume_model(text) -> dict:
	app.logger.info(f'Consuming model with {text}')

	# TODO Call with one by now
	intents_result = model.predict(text, company_name='origenes')

	# Check max confidence class
	best_class = np.argmax([intent['confidence'] for intent in intents_result])
	return intents_result[best_class]