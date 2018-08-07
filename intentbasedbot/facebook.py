#!/usr/bin/env python3
# Main packages of the application
from intentbasedbot import app, utils, intents
from intentbasedbot.config import *

# System
import random
import requests as req

# Facebook Messenger
from pymessenger.bot import Bot
from pymessenger import Element

# Flask
# TODO Improvement, we should not call controller methods in modules.
# TODO Return as JSON.
from flask import abort, jsonify

bot = Bot(FACEBOOK_ACCESS_TOKEN)

########################################## Webhook ##########################################
def verify_token(mode, token, challenge):
	"""
		Take token sent by facebook and verify it matches the verify token you sent
		if they match, allow the request, else return an error.
		:mode: 'subscribe' only for now
		:token: Verify Token in Facebook Developers UI.
		:challenge:	Value for reflect, should be sended back to client.
		:return: JSON response for the controller.
	"""
	if mode and token:
		if mode == 'subscribe' and token == FACEBOOK_VERIFY_TOKEN:
			app.logger.info('Webhook verified')
			# Responds with the challenge
			return challenge
		else:
			app.logger.error('Invalid verification token')
			abort(403, jsonify(message='Invalid verification token'))
	else:
		app.logger.error('Missing URL parameters: mode or token')
		abort(403, jsonify(message='Missing URL parameters: mode or token'))


def decode_messaging(messaging, channel='messaging'):
	# TODO For debugging purposes
	# app.logger.info(messaging)
	""" Decodes the message and handles according to type """
	sender = messaging['sender']['id']
	recipient = messaging['recipient']['id']
	date = utils.get_iso_date(messaging['timestamp'])

	# TODO Beautify this
	# app.logger.info(f'{date} Text message from {interlocutors[sender]} to {interlocutors[recipient]} "{text}"')

	if messaging.get('pass_thread_control'):
		handle_pass_thread_control(sender, messaging.get('pass_thread_control'))
	elif messaging.get('take_thread_control'):
		handle_take_thread_control(sender, messaging.get('take_thread_control'))
	elif messaging['message'].get('quick_reply'):
		# Can I respond?
		if channel == 'messaging':
			handle_quick_reply(sender, messaging['message']['quick_reply'])
		else:
			app.logger.info(f"I'm the bot listening all this conversation in channel '{channel}' with quick reply")
	# TODO An attachment usually comes wih text too
	elif messaging['message'].get('attachments'):
		handle_attachments(sender, messaging['message'].get('attachments'))
	elif messaging['message'].get('text'):
		# responses.append(handle_text(sender, text))
		# Can I respond?
		if channel == 'messaging':
			# text = 'Welcome! The bot is currently in control. \n\n Tap "Pass to Inbox" to pass control to the Page Inbox.'
			# title = 'Pass to Inbox'

			# Send one quick reply to enable the user talks with person
			text = f'Soy el bot {apps[I_AM]}'
			if I_AM == PRIMARY_APP_ID:
				payload = ['pass_to_inbox', 'pass_to_secondary']
			elif I_AM == SECONDARY_APP_ID:
				payload = ['pass_to_inbox', 'pass_to_primary']
			else:
				app.logger.info("I'm the operator")
				payload = ['pass_to_primary', 'pass_to_secondary']

			# send_quick_reply(sender, text, payload)
			# Consuming our model for detect intent
			intent = intents.get_intent(messaging['message'].get('text'))
			text_response(sender, text + '\n' + intent)
		else:
			app.logger.info(f"I'm the bot listening all this conversation in channel '{channel}'")
	else:
		app.logger.info(f"Unknow message type")

	# elif messaging['message'].get('nlp') and messaging['message'].get('nlp').get('entities'):
	# 	# TODO Check responses.
	# 	# Facebook built-in
	# 	# responses.append(handle_entities(sender, messaging['message'].get('nlp').get('entities')))
	# # Empty dic {}
	# else:
	# 	app.logger.info('No entities found')
	# 	responses.append('\nNo encontre entidades')

	# One point of response
	# response_text = ' '.join(filter(None, responses))
	# text_response(sender, response_text)
	# return response_text


def handle_text(sender, text):
	# TODO Random fancy responses by now
	# return get_response_message(text)
	return ''


def handle_entities(sender, entities) -> str:
	""" Check the built-in NLP entities sent by Facebook """
	response = ''
	# Array of intents
	for intent in entities.get('intent'):
		intent_detected = intent['value']
		intent_confidence = round(intent['confidence'] * 100, 2)
		app.logger.info(f'Intent detected {intent_detected} {intent_confidence}%')
		response += f'\nEncontre esta intencion {intent_detected} {intent_confidence}%'

	return response


def handle_attachments(sender, attachments):
	""" if user sends us a GIF, photo, video or any other non-text item """
	elements = []
	element = Element(title="Este es el adjunto que me mandaste", image_url=attachments[0]['payload']['url'], subtitle="", item_url="https://www.cliengo.com/")
	elements.append(element)

	bot.send_generic_message(sender, elements)

def handle_quick_reply(sender, quick_reply):
	# Primary passing the conversation to inbox
	if quick_reply.get('payload') and quick_reply.get('payload') == 'pass_to_inbox':
		# Quick reply to pass to Page inbox was clicked
		page_inbox_app_id = '263902037430900'
		# text = 'The Primary Receiver is passing control to the Page Inbox. \n\n Tap "Take From Inbox" to have the Primary Receiver take control back.'
		# title = 'Take From Inbox'
		text = 'Pasaste a hablar con un operador'
		title = 'Bot'
		payload = 'take_from_inbox'

		send_quick_reply(sender, text, [payload])
		pass_thread_control(sender, page_inbox_app_id)

	# Primary take the conversation from the inbox
	if quick_reply.get('payload') and quick_reply.get('payload') == 'take_from_inbox':
		# Quick reply to take from Page inbox was clicked
		# text = 'The Primary Receiver is taking control back. \n\n Tap "Pass to Inbox" to pass thread control to the Page Inbox.'
		# title = 'Pass to Inbox'
		text = f'Pasaste a hablar con {apps[I_AM]}'
		payload = 'pass_to_inbox'

		send_quick_reply(sender, text, [payload])
		take_thread_control(sender)

	# Primary giving control to secondary
	if quick_reply.get('payload') and quick_reply.get('payload') == 'pass_to_secondary':
		text = f'Pasaste a hablar con {apps[SECONDARY_APP_ID]}'

		payload = 'pass_to_primary'

		send_quick_reply(sender, text, [payload])
		pass_thread_control(sender, SECONDARY_APP_ID)

	# Primary taking control again
	if quick_reply.get('payload') and quick_reply.get('payload') == 'pass_to_primary':
		text = f'Pasaste a hablar con {apps[I_AM]}'
		payload = 'pass_to_inbox'

		send_quick_reply(sender, text, [payload])
		take_thread_control(sender)

def handle_pass_thread_control(sender, pass_thread_control):
	# thread control was passed back to bot manually in Page inbox
	new_owner_app_id = str(pass_thread_control['new_owner_app_id'])
	metadata = pass_thread_control['metadata']
	app.logger.info(f'Conversation is now handled by "{apps[new_owner_app_id]}" with metadata "{metadata}"')

	text = f'La conversacion cambio de dueño. Pasaste a hablar con {apps[SECONDARY_APP_ID]}'
	# For give the option of return to person
	payload = ['pass_to_inbox']
	if I_AM == PRIMARY_APP_ID:
		payload.append('pass_to_secondary')
	elif I_AM == SECONDARY_APP_ID:
		payload.append('pass_to_primary')

	send_quick_reply(sender, text, payload)

def handle_get_thread_owner(sender):
	params = {
		'access_token': {FACEBOOK_ACCESS_TOKEN},
		'recipient' : sender
	}
	res = req.get(f'{GRAPH_URL}{GET_THREAD_OWNER_URI}', params=params)
	return res['data'][0]['thread_owner']['app_id']

def handle_take_thread_control(sender, take_thread_control):
	previous_owner_app_id = str(take_thread_control['previous_owner_app_id'])
	metadata = take_thread_control['metadata']
	app.logger.info(f'Im delivering this conversation "{apps[previous_owner_app_id]}" with metadata "{metadata}"')

def handle_post_back(sender, post_back):
	# messaging.get('postback'):
	# https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/messaging_postbacks
	text_response(sender, f"Me contestaste con un {post_back['payload']}")


def get_response_message(text):
	""" Chooses a random message to send to the user """
	sample_responses = ["Dejame pensarlo un rato", "Me lo explicas como si fuera Doña Rosa.",
	                    "Para Para Para vos me estas diciendo...", "En el futbol lo diriamos de esta forma"]
	return random.choice(sample_responses)


def text_response(recipient, response):
	""" uses PyMessenger to send response to user if enabled. Anyway logs in the stdout """
	app.logger.info(f'Sending response from bot to {interlocutors[recipient]} "{response}"')

	if SEND_MESSAGE:
		bot.send_text_message(recipient, response)

####################################### Graph API Call #######################################
def send_quick_reply(recipient, text, postback_payload):
	# Simple text message template
	quick_replies = []
	for element in postback_payload:
		quick_replies.append({
			'content_type': 'text',
			'title': parse_quick_replies(element),
			'payload': element
		})

	payload = {
		'recipient': {'id': recipient},
		'message': {
			'text': text,
			'quick_replies': quick_replies
		}
	}

	app.logger.info(f'Sending Quick Reply from "bot" to "{interlocutors[recipient]}" "{quick_replies}"')

	if SEND_MESSAGE:
		req.post(f'{GRAPH_URL}{MESSAGES_URI}', params=GRAPH_PARAMS, json=payload)

def parse_quick_replies(postback_payload):
	reply_lookup = {
		'pass_to_inbox':'Pasar a Operador',
		'pass_to_primary':'Pasar a Primario',
		'pass_to_secondary':'Pasar a Secundario',
		'take_from_inbox': 'Tomar del Operador',
		'take_from_secondary': 'Tomar del Secundario'
	}
	return reply_lookup[postback_payload]

def pass_thread_control(user_id, target_app_id):
	app.logger.info(f'Passing thread control to "{apps[target_app_id]}"')
	payload = {
		'recipient': { 'id': user_id },
		 'target_app_id': target_app_id
	}

	req.post(f'{GRAPH_URL}{PASS_THREAD_CONTROL_URI}', params=GRAPH_PARAMS, json=payload)

# only the Primary Receiver can take thread control
def take_thread_control(user_id):
	app.logger.info(f'Taking thread control')
	payload = {
		'recipient': { 'id': user_id },
	}

	req.post(f'{GRAPH_URL}{TAKE_THREAD_CONTROL_URI}', params=GRAPH_PARAMS, json=payload)