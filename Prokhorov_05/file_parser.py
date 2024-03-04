import os
import re
import csv
from typing import List, Dict, Set
from time import perf_counter

all_words = set()


def timer(func):
    def wrapper(*args, **kwargs):
        ts = perf_counter()
        result = func(*args, **kwargs)
        te = perf_counter()
        print(f"Function: {func.__name__}\n"
              f"Took: {te - ts:.6f} seconds")
        return result
    return wrapper


def create_csv_file(words: List[str], csv_file_name: str):
    with open(csv_file_name, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for word in words:
            csv_writer.writerow([word])


def __read_file(filename: str, regex_pattern: str = r'.+'):
    with open(file=filename, mode='r', encoding='utf-8', errors='replace') as file:
        for line in file:
            translation_pattern = re.compile('[^a-zA-Z\']+')
            for word in line.split():
                clean_word = re.sub(translation_pattern, '', word.lower())
                if re.match(regex_pattern, clean_word):
                    yield clean_word


def build_index(filenames: List[str], first_file_index: int = 0, size: int = None) -> Dict[str, List[int]]:
    dictionary = {}
    if size is None:
        size = len(filenames)
    for idx, filename in enumerate(filenames[:size], first_file_index):
        for word in __read_file(filename=filename, regex_pattern=r'\b[a-z]{3,15}\b'):
            all_words.add(word)
            if word not in dictionary.keys():
                dictionary[word] = list()
            if idx + 1 not in dictionary[word]:
                dictionary[word].append(idx + 1)
    sorted_word_counts = dict(sorted(dictionary.items()))
    return sorted_word_counts


def to_csv(filenames: List[str], dictionary: Dict[str, List[int]], output_file: str,
           column_names: bool = True) -> None:
    with open(output_file, mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',')
        if column_names:
            writer.writerow(['word', *filenames])
        for key, value in dictionary.items():
            writer.writerow([key, *value])


def get_all_files_in_directory(directory):
    all_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    return all_files

@timer
def divide_files(input_folder: str, output_folder: str, max_size_per_cluster: int = 1024 * 1024 * 1024) -> None:
    cluster_index = 1
    current_cluster_size = 0
    current_cluster_files = []
    first_cluster_index = 0

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)

            if current_cluster_size + file_size <= max_size_per_cluster:
                current_cluster_size += file_size
                current_cluster_files.append(file_path)
            else:
                create_cluster(output_folder, cluster_index, current_cluster_files, current_cluster_size,
                               first_cluster_index)
                first_cluster_index += len(current_cluster_files)
                cluster_index += 1
                current_cluster_size = file_size
                current_cluster_files = [file_path]

    if current_cluster_files:
        create_cluster(output_folder, cluster_index, current_cluster_files, current_cluster_size, first_cluster_index)
        create_csv_file(sorted(all_words), 'all_words.csv')

@timer
def create_cluster(output_folder: str, cluster_index: int, files: List[str], cluster_size: float = 0,
                   first_file_position: int = 0) -> None:
    cluster_folder = os.path.join(output_folder, f"cluster_{cluster_index}.csv")

    to_csv(files, build_index(files, first_file_position), cluster_folder, column_names=False)

    print(
        f"Cluster {cluster_index} created with {len(files)} files with size {round(cluster_size / (1024 * 1024), 4)}Mb.")
