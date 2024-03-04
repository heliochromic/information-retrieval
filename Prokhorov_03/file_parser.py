import os
import re
from typing import Dict, List


def read_file(filename: str, regex_pattern: str = r'.+'):
    word_index = 0
    prev_word = None  # Initialize prev_word
    with open(file=filename, mode='r') as file:
        for line in file:
            translation_pattern = re.compile('[^a-zA-Z\']+')
            for word in line.split():
                clean_word = re.sub(translation_pattern, '', word.lower())
                if re.match(regex_pattern, clean_word):
                    word_index += 1
                    yield prev_word, clean_word, word_index
                    prev_word = clean_word


def biword_index(filenames: List[str], path: str) -> Dict[str, List[int]]:
    dictionary = dict()
    dictionary['_UNKNOWN_WORD_'] = dict()

    for idx, filename in enumerate(filenames, 1):
        full_path = os.path.join(path, filename)
        for prev_word, current_word, word_index in read_file(filename=full_path, regex_pattern=r'\b[a-z]{0,15}\b'):
            biword = f"{prev_word} {current_word}"
            if prev_word is not None and biword not in dictionary:
                dictionary[biword] = []
            if prev_word is not None and idx not in dictionary[biword]:
                dictionary[biword].append(idx)

    sorted_word_counts = dict(sorted(dictionary.items()))
    return sorted_word_counts


def coordinate_inverted_index(filenames: List[str], path: str) -> Dict[str, Dict[int, List[int]]]:
    dictionary = dict()
    dictionary['_UNKNOWN_WORD_'] = dict()

    for idx, filename in enumerate(filenames, 1):
        full_path = os.path.join(path, filename)
        for prev_word, current_word, word_index in read_file(filename=full_path, regex_pattern=r'\b[a-z]{0,15}\b'):
            if current_word not in dictionary.keys():
                dictionary[current_word] = {}
            if idx not in dictionary[current_word].keys():
                dictionary[current_word][idx] = []
            dictionary[current_word][idx].append(word_index)

    sorted_word_counts = dict(sorted(dictionary.items()))
    return sorted_word_counts


# print(biword_index(os.listdir('Dataset')[:10], path='Dataset'))
# print(coordinate_inverted_index(os.listdir('Dataset')[:10], path='Dataset'))
