import pymorphy3
import os
import re
from nltk.tokenize import sent_tokenize
from variables import *

os.system('cls')


def module(n: int):
    return n if n >= 0 else -n


def similary(words, analyzer, register, inaccurances):
    similarity = 0
    if register:
        words = (words[0].lower(), words[1].lower())
    similarity += module(1 - module(len(words[1]) - len(words[0])) / 100)
    lenghs = (len(words[0]), len(words[1]))
    if inaccurances:
        similarity += (sum(a:=[int(words[0][j] == words[1][j]) for j in range(min(lenghs))]) / len(a))
    else:
        similarity += 1 if words[0] == words[1] else 0
    if analyzer.parse(words[0])[0].normal_form == analyzer.parse(words[1])[0].normal_form and inaccurances:
        similarity += 0.5
    return round(similarity, 2)


def text_parser(text):
    text1 = []
    for i in text:
        text1.append(re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', i)).replace('\n', ''))
    return text1


def find(text: list[str], substring: str, register: bool=True, inaccuracies: bool=True):
    s = []
    analizator = pymorphy3.MorphAnalyzer()
    substring = substring.strip()
    for i, sentense in enumerate(text):
        for one_word in sentense.split():
            if (sim:=similary((one_word, substring), analizator, register, inaccuracies)) > 1:
                s.append((one_word, sim, i))
    return sorted(s, key=lambda x: x[1])

if __name__ == '__main__':
    text = sent_tokenize(text)
    for i in find(text_parser(text), input())[-10:]:
        print(f'Слово: "{i[0]}", предложение №{i[2] + 1}: "{text[i[2]]}", оценка: {i[1]}')
