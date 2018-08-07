#!/usr/bin/env python3
# Main packages of the application
from intentbasedbot import app
from intentbasedbot import text_features as tf

import numpy as np
import os

import pickle
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.models import model_from_json

def get_model_and_encoder(company_name):
	base_path = app.instance_path

	# Model definition
	model_path = os.path.join(base_path, 'models', f'model_{company_name}.json')
	app.logger.info(f'Loading model from {model_path}')
	with open(model_path, 'r') as json_file:
		model = model_from_json(json_file.read())
	app.logger.info('Model definition loaded from disk')

	# Model weights
	weights_path = os.path.join(base_path, 'models', f'model_{company_name}.h5')
	app.logger.info(f'Loading weights from {weights_path}')
	model.load_weights(weights_path)
	app.logger.info("Model weights loaded from disk")

	# Encoder
	encoder_path = os.path.join(base_path, 'models', f'classes_{company_name}.npy')
	app.logger.info(f'Loading encoder from {encoder_path}')
	encoder = LabelEncoder()
	encoder.classes_ = np.load(encoder_path)
	app.logger.info('Encoder definition loaded from disk')

	# Tokenizer
	tokenizer_path = os.path.join(base_path, 'models', f'tokenizer_{company_name}.pickle')
	with open(tokenizer_path, 'rb') as handle:
		tokenizer = pickle.load(handle)

	return model, encoder, tokenizer

def preprocessing(sentences, tokenizer, max_len = 300):
	"""
		:sentences: List of strings
		:returns: (1,100) numpy array
	"""
	sequences = tokenizer.texts_to_sequences(sentences)

	# Transforming the list of indexes to a 2D tensor (sample, maxlen)
	return pad_sequences(sequences, maxlen=max_len)

def predict(utterance, company_name):
	# Fetch the model
	# TODO Save in Flask context for avoid loading in each request
	model, encoder, tokenizer = get_model_and_encoder(company_name)

	# Clean and tokenize the utterance, filter the stop words, then reassemble the utterance and put into a list
	test_data = preprocessing([' '.join(tokenize_utterance(utterance))], tokenizer)
	predictions = model.predict_classes(test_data, batch_size=1, verbose=0)
	y_prob = model.predict(test_data)
	y_classes = y_prob.argmax(axis=-1)

	intent_result = []
	for i in range(0, len(predictions)):
		# app.logger.info('Class for {}: {}'.format(sentences[i], encoder.inverse_transform(predictions[i])))
		predicted_intent = {
			'utterance': utterance,
			'intent': encoder.inverse_transform(predictions[i]),
			'confidence': y_prob.flatten()[y_classes[0]]
		}
		intent_result.append(predicted_intent)

	return intent_result

tokenize_utterance = lambda utterance: [token for token in tf.filter_tokenize(utterance) if token not in tf.get_stop_words_es()]
