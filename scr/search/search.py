import pymorphy3
import re
from nltk.tokenize import sent_tokenize


def module(n: int) -> int:
    """Returns the modulus of the number "n"."""
    return n if n >= 0 else -n


def similary(words: tuple, analyzer: pymorphy3.MorphAnalyzer, register: bool, inaccurances: bool) -> float:
    """Returns an indicator of the similarity of words or sentences (can be case-insensitive or search for misspelled
    words)."""
    similarity = 0
    if register:
        words = (words[0].lower(), words[1].lower())
    similarity += module(1 - module(len(words[1]) - len(words[0])) / 100)
    lenghs = (len(words[0]), len(words[1]))
    if inaccurances:
        similarity += (sum(a := [int(words[0][j] == words[1][j]) for j in range(min(lenghs))]) / len(a))
    else:
        similarity += 1 if words[0] == words[1] else 0
    if analyzer.parse(words[0])[0].normal_form == analyzer.parse(words[1])[0].normal_form and inaccurances:
        similarity += 0.5
    return round(similarity, 2)


def text_parser(text: str) -> list[str]:
    """Splits text to sentenses and delets "\\n", punctuation marks and repeated spaces"""
    text = sent_tokenize(text)
    text1 = []
    for sentense in text:
        text1.append(re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', sentense)).replace('\n', ''))
    return text1


def find(text: str, substring: str, register: bool = True, inaccuracies: bool = True) -> list[tuple]:
    """Searches for similar words or sentenses in the list of sentences"""
    found_words = []
    text = text_parser(text)
    analizator = pymorphy3.MorphAnalyzer()
    substring = text_parser(substring.strip())[0]
    for n, sentense in enumerate(text):
        if ' ' in substring:
            if (sim := similary((sentense, substring), analizator, register, inaccuracies)) > 1:
                found_words.append((sentense, sim, n))
        else:
            for one_word in sentense.split():
                if (sim := similary((one_word, substring), analizator, register, inaccuracies)) > 1:
                    found_words.append((f'Слово: "{one_word}", предложение №{n + 1}: "{text[n]}", оценка: {sim}', sim))
    if found_words:
        return [f'''<b>Слово: "{i[0]}"</b>, предложение №{i[2] + 1}: "{text[i[2]]}", оценка: {i[1]}

    ''' for i in sorted(s, key=lambda x: x[1])][-8:]
    return ['Слов не найдено!']
