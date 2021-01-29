#!/usr/bin/env python3
# Main packages of the application
from intentbasedbot import app
from intentbasedbot.config import *
from intentbasedbot import model

# Web
import requests as req

""" Wraps the connection with NLPs APIs and models """

company_name = COMPANY_NAME

def get_intent(text) -> dict:
	""" Consume external APIs or/and our model and returns the best intent prediction  """
	intents = []

	if USE_WIT:
		# intent_entity = intent.get('_entity') # Another interesting field in WIT
		intents += consume_wit(text)

	if USE_MODEL:
		intents.append(consume_model(text))

	# TODO Taking only the first intent by now
	intent = intents[0]
	app.logger.info(f"Intent detected {intent['intent']} {intent['confidence']}")

	return intent

def consume_wit(text) -> list:
	app.logger.info(f'Consuming wit with {text}')
	params = {'v': WIT_VERSION, 'q': text, 'verbose': True, 'n': 2}
	endpoint = 'https://api.wit.ai/message'

	response = req.get(endpoint, params=params, headers=WIT_HEADERS,)
	return response.json()['entities'].get('intent')

def consume_model(text) -> dict:
	app.logger.info(f'Consuming model with "{text}"')

	global company_name
	return model.predict(text, company_name=company_name)

def change_model(new_company_name):
	global company_name
	app.logger.info(f'Changing model from {company_name} to {new_company_name}')
	company_name = new_company_name