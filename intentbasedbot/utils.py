#!/usr/bin/env python3
import pandas as pd

import time
import random
from datetime import datetime

get_iso_date = lambda timestamp: datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
current_milli_time = lambda: int(round(time.time() * 1000))

# Testing the two lambdas from above
# get_iso_date(current_milli_time())

def wrap_message(messaging):
	# Wrapper of the messages
	payload = {
	  "object": "page", # From fanpage
	  "entry": [        # Always only one entry?
		{
		  "messaging": [
			  {} # Placeholder, will be filled
		  ],
		  "standby": [

		  ]
		}
	  ]
	}

	payload['entry'][0]['messaging'][0] = messaging

	return payload


def send_webhook_message(sender, recipient, text):
	""" Simulates a message sent by the Facebook webhook """
	messaging = {
	  'sender': {
		'id': sender
	  },
	  'recipient': {
		'id': recipient
	  },
	  'timestamp': current_milli_time(),
	  'message': {
		'mid': 'F2olYNRgAmxlRvSjX4vuwD4SAFFzgUefpXG-kj6ez_NqFo0OBLGKDq50CLcBvsxD5TmKg60HEH8glPcg_EtTyA',
		'seq': random.randint(0, 2 ** 10),
		'text': text,
		'attachments': [
			# {'payload': {'url' : 'https://files.startupranking.com/startup/thumb/28845_238d9850f2f3f7671a971fd8087cdadc3aca71be_cliengo_m.png'}}
		],
		'nlp': {
		  'entities': {
			'intent': [
			  {
				'confidence': 0.94566211638909,
				'value': 'BookRestaurant',
				'_entity': 'intent'
			  }
			]
		  }
		}
	  }
	}

	return wrap_message(messaging)

def get_sample(amount=1):
	dataset_path = 'data/snips_utterances.csv'
	intent_column = 'Intention'
	language = 'Spanish'

	all_intents_df = pd.read_csv(dataset_path)
	sample_sentence = all_intents_df.sample(amount)

	# Transforming sentences from Series to list
	return sample_sentence[language].tolist()