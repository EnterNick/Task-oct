import pymorphy3
import pprint
import os
from variables import *

os.system('cls')

def module(n: int):
    return n if n >= 0 else -n

def similary(word, word2):
    similarity = (1 - module(len(word2) - len(word)) / 100)
    lenghs = (len(word), len(word2))
    similarity += (sum([int(word[j] == word2[j]) for j in range(min(lenghs))]) / max(lenghs))
    return round(similarity, 2)


def find(text, substring):
    s = []
    analizator = pymorphy3.MorphAnalyzer()
    substring = substring.lower()
    for i in text.split():
        word = analizator.parse(i.lower())[0].normal_form
        if ((sim:=similary(word, substring) + similary(i.lower(), substring)) > 2):
            s.append((i, sim))
    return sorted(s, key=lambda x: x[1])


pprint.pprint(find(text, 'мир')[-10:])