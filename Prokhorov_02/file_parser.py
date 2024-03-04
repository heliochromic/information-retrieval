import re
import os
import csv


def _read_file(filename: str, regex_pattern: str = r'.+'):
    with open(file=filename, mode='r') as file:
        for line in file:
            translation_pattern = re.compile('[^a-zA-Z\']+')
            for word in line.split():
                clean_word = re.sub(translation_pattern, '', word.lower())
                if re.match(regex_pattern, clean_word):
                    yield clean_word


def incidence_matrix(filenames: list, path: str) -> dict:
    dictionary = dict()
    dictionary['_UNKNOWN_WORD_'] = [0] * len(filenames)
    for idx, filename in enumerate(filenames):
        full_path = os.path.join(path, filename)
        for word in _read_file(filename=full_path, regex_pattern=r'\b[a-z]{3,15}\b'):
            if word not in dictionary.keys():
                dictionary[word] = [0] * len(filenames)
            dictionary[word][idx] = 1

    sorted_word_counts = dict(sorted(dictionary.items()))
    return sorted_word_counts


def inverted_index(filenames: list, path: str) -> dict:
    dictionary = dict()
    dictionary['_UNKNOWN_WORD_'] = list()
    for idx, filename in enumerate(filenames, 1):
        full_path = os.path.join(path, filename)
        for word in _read_file(filename=full_path, regex_pattern=r'\b[a-z]{3,15}\b'):
            if word not in dictionary.keys():
                dictionary[word] = list()
            if idx not in dictionary[word]:
                dictionary[word].append(idx)

    sorted_word_counts = dict(sorted(dictionary.items()))
    return sorted_word_counts


def to_csv(filenames: list, dictionary: dict, output_file: str = 'output.csv', column_names: bool = True) -> None:
    with open(output_file, mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',')
        if column_names:
            writer.writerow(['word', *filenames])
        for key, value in dictionary.items():
            writer.writerow([key, *value])


def to_dict(input_file: str = 'output.csv', column_names: bool = True) -> dict:
    dictionary = dict()
    with open(input_file, mode='r') as input_file:
        reader = csv.reader(input_file, delimiter=',')
        if column_names:
            next(reader)
        for row in reader:
            dictionary[row[0]] = [int(x) for x in row[1:]]
    return dictionary


def index_to_list(filenames: str, index: list) -> list:
    r_list = list()
    for i in index:
        r_list.append(filenames[i - 1])
    return r_list


def indices_to_list(filenames: str, indices: list) -> list:
    r_list = list()
    for idx, i in enumerate(indices):
        if i == 1:
            r_list.append(filenames[idx])
    return r_list


def stats(filename: str, dictionary: dict) -> None:
    size = os.path.getsize(filename)
    unique_words = len(dictionary)
    total_words = sum(sum(value) for value in dictionary.values())
    print(f"Filename             : {filename}\n"
          f"Collection size      : m\n"
          f"Unique number words  : {unique_words}\n")
