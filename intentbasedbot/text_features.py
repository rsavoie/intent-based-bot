
# coding: utf-8

# # Text Features
from nltk.tokenize import word_tokenize
import unidecode # pip

# Two sets of stop words: NLTK and generic
from nltk.corpus import stopwords
from stop_words import get_stop_words

# 06/08 August from TF IDF analysis
common_words = ['muchas', 'gracias', 'quiero', 'saber', 'queria', 'quisiera', 'ok', 'buen', 'dia', 'dias', 'hola', 'puede', 'ser', 'buenas', 'buenos', 'tardes', 'q', 'x', 'cualquier']

# Replace accents, remove trailing spaces and lowercase
decode = lambda sentence: unidecode.unidecode(sentence).strip().lower()

# Filter alphabetic tokens, remove stop words (Update: In later stage)
# and token not in all_stop_words
filter_tokenize = lambda sentence: [token for token in word_tokenize(decode(sentence)) if token.isalpha()]

get_stop_words_es = lambda: set(decode(token) for token in get_stop_words('es') + stopwords.words('spanish') + common_words)

