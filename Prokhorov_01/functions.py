import re
import os
import csv
import pickle


def _read_file(filename: str, regex_pattern: str = r'.+'):
    with open(file=filename, mode='r', encoding='utf-8') as file:
        for line in file:
            translation_pattern = re.compile('[^a-zA-Z\']+')
            for word in line.split():
                clean_word = re.sub(translation_pattern, '', word.lower())
                if re.match(regex_pattern, clean_word):
                    yield clean_word


def calculate_frequency(filenames: list) -> dict:
    dictionary = dict()
    for idx, filename in enumerate(filenames):
        file_path = os.path.join('../texts', filename)
        for word in _read_file(filename=file_path, regex_pattern=r'\b[a-z]{3,15}\b'):
            if word not in dictionary.keys():
                dictionary[word] = [0] * len(filenames)
            dictionary[word][idx] += 1

    sorted_word_counts = dict(sorted(dictionary.items()))
    return sorted_word_counts


def to_csv(filenames: list, dictionary: dict, output_file: str = 'output.csv') -> None:
    fieldnames = ['word', *filenames]
    with open(output_file, mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',')
        writer.writerow(fieldnames)
        for key, value in dictionary.items():
            writer.writerow([key, *value])


def to_dict(input_file: str = 'output.csv') -> dict:
    dictionary = dict()
    with open(input_file, mode='r', encoding='utf-8') as input_file:
        reader = csv.reader(input_file, delimiter=',')
        next(reader)
        for row in reader:
            dictionary[row[0]] = [int(x) for x in row[1:]]
    return dictionary


def serialize(dictionary: dict, filename: str = 'serialized.pkl') -> None:
    with open(filename, mode='wb') as output_file:
        pickle.dump(dictionary, output_file)


def deserialize(filename: str = 'serialized.pkl ') -> dict:
    with open(filename, mode='rb') as input_file:
        data = pickle.load(input_file)
    return data


def stats(filename: str, dictionary: dict) -> None:
    size = os.path.getsize(filename)
    unique_words = len(dictionary)
    total_words = sum(sum(value) for value in dictionary.values())
    print(f"Filename             : {filename}\n"
          f"Collection size      : {round(size / (1024 * 1024), 4)}Mb\n"
          f"Unique number words  : {unique_words}\n"
          f"Total number of words: {total_words}\n")
