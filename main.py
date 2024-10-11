import pymorphy3
import pprint
import os
import re
from nltk.tokenize import sent_tokenize
from variables import *

os.system('cls')

def module(n: int):
    return n if n >= 0 else -n

def similary(word, word2):
    similarity = (1 - module(len(word2) - len(word)) / 100)
    lenghs = (len(word), len(word2))
    similarity += (sum([int(word[j] == word2[j]) for j in range(min(lenghs))]) / max(lenghs))
    return round(similarity, 2)


def text_parser(text):
    text = sent_tokenize(text)
    text1 = text.copy()
    text.clear()
    for i in text1:
        text.append(re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', i)))
    return text


def find(text, substring):
    s = []
    analizator = pymorphy3.MorphAnalyzer()
    substring = substring.lower().strip()
    for sentense in text:
        for one_word in sentense.split():
            word = analizator.parse(one_word.lower())[0].normal_form
            if ((sim:=similary(word, substring) + similary(one_word.lower(), substring)) > 2):
                s.append((one_word, sim, sentense))
    return sorted(s, key=lambda x: x[1])


pprint.pprint(find(text_parser(text), 'ВЕТЕР')[-10:])
