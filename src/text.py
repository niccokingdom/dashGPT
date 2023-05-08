
from transformers import GPT2Tokenizer

from urllib.parse import urlparse, urlunparse
from collections import defaultdict
import re

"""
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
def split_text(text, max_tokens):

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    sentences = sent_tokenize(text)
    current_piece_tokens = 0
    current_piece = []
    pieces = []

    tot_tokens = len(word_tokenize(text))

    for sentence in sentences:
        sentence_tokens = word_tokenize(sentence)
        num_tokens = len(sentence_tokens)

        if current_piece_tokens + num_tokens <= max_tokens:
            current_piece.append(sentence)
            current_piece_tokens += num_tokens
        else:
            pieces.append(" ".join(current_piece).strip())
            current_piece = [sentence]
            current_piece_tokens = num_tokens

    if current_piece:
        pieces.append(" ".join(current_piece).strip())

    return tot_tokens, pieces
"""


def split_text_gpt(text, max_tokens):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

    tokens = tokenizer.encode(text)
    total_tokens = len(tokens)

    current_piece = []
    current_piece_tokens = 0
    pieces = []

    for token in tokens:
        if current_piece_tokens + 1 <= max_tokens:
            current_piece.append(token)
            current_piece_tokens += 1
        else:
            pieces.append(tokenizer.decode(current_piece).strip())
            current_piece = [token]
            current_piece_tokens = 1

    if current_piece:
        pieces.append(tokenizer.decode(current_piece).strip())

    return total_tokens, pieces