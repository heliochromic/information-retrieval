import os
import re
from typing import List, Tuple, Dict
from trie import Trie


def __read_file(filename: str, regex_pattern: str = r'.+'):
    with open(file=filename, mode='r') as file:
        for line in file:
            translation_pattern = re.compile('[^a-zA-Z\']+')
            for word in line.split():
                clean_word = re.sub(translation_pattern, '', word.lower())
                if re.match(regex_pattern, clean_word):
                    yield clean_word


def trie_builder(path: str, size: int) -> Tuple[Trie, Trie]:
    trie = Trie()
    reversed_trie = Trie()
    filenames = os.listdir(path)[:size]
    for idx, filename in enumerate(filenames):
        full_path = os.path.join(path, filename)
        for word in __read_file(filename=full_path, regex_pattern=r'\b[a-z]{3,15}\b'):
            trie.insert(word)
            reversed_trie.insert(word[::-1])
    return trie, reversed_trie


def trie_index(prefixes, suffixes, joker) -> List[str]:
    splitted_word = joker.split('*')
    prefix, suffix = f"{splitted_word[0]}*", f"*{splitted_word[-1]}"
    prefix_voc = set(prefixes.startsWith(prefix))
    suffix_voc = set([word[::-1] for word in suffixes.startsWith(suffix[::-1])])

    return list(prefix_voc & suffix_voc)


def permuterm_index(path: str, size: int) -> Trie:
    trie = Trie()
    filenames = os.listdir(path)[:size]
    for idx, filename in enumerate(filenames):
        full_path = os.path.join(path, filename)
        for word in __read_file(filename=full_path, regex_pattern=r'\b[a-z]{3,15}\b'):
            permuterm_vocabulary = [f"{word[i:]}${word[:i]}" for i in range(len(word) + 1)]
            for vocabulary_word in permuterm_vocabulary:
                trie.insert(vocabulary_word)
    return trie


def word_permuterm_preprocess(joker: str) -> str:
    splitted_word = joker.split('*')
    prefix, suffix = splitted_word[0], splitted_word[-1]
    return f"{suffix}${prefix}*"


def word_rotate(matching_words: set) -> List[str]:
    return [f"{word.split('$')[-1]}{word.split('$')[0]}" for word in matching_words]


def k_gram_builder(path: str, size: int, k: int = 3) -> Dict[str, List[str]]:
    dictionary = {}
    filenames = os.listdir(path)[:size]
    for filename in filenames:
        full_path = os.path.join(path, filename)
        for word in __read_file(filename=full_path, regex_pattern=r'\b[a-z]{3,15}\b'):
            padded_word = '$' * k + word + '$' * k
            for i in range(len(padded_word) - k + 1):
                k_gram = padded_word[i:i + k]
                if k_gram not in dictionary:
                    dictionary[k_gram] = []
                dictionary[k_gram].append(word)
    return dictionary


def k_word_splitter(joker: str, dictionary: Dict[str, List[str]], k: int = 3) -> List[str]:
    searched_slices = []
    padded_word = '$' * k + joker + '$' * k
    prefix, suffix = padded_word.split('*')[0], padded_word.split('*')[-1]
    for i in range(len(prefix) - k + 1):
        searched_slices.append(prefix[i:i + k])
    for i in range(len(suffix) - k + 1):
        searched_slices.append(suffix[i:i + k])

    init_slice = set(dictionary[next(iter(searched_slices))])
    for searched_slice in searched_slices:
        init_slice &= set(dictionary[searched_slice])

    return list(init_slice)

# query = 'w*tc*se'
# permuterm_trie = permuterm_index(path='Dataset', size=10)
#
# prefix, middle = word_permuterm_preprocess(joker=query)
# result = word_rotate(permuterm_trie.startsWith(prefix), middle)
# print(sorted(result), len(result))
