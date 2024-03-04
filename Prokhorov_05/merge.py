import os
import csv
from file_parser import divide_files, timer


def all_words_reader(filename: str):
    with open(file=filename, mode='r', encoding='utf-8', errors='replace') as file:
        for word in file:
            yield word.strip()


def clusters_reader(filename: str):
    with open(file=filename, mode='r', encoding='utf-8', errors='replace') as file:
        for line in file:
            line = line.strip().split(',')
            yield line[0], [element.strip() for element in line[1:]]


@timer
def merge(all_words_file: str, input_folder: str, output_filename: str) -> None:
    cluster_generators = [clusters_reader(os.path.join(input_folder, file)) for file in os.listdir(input_folder)]
    initial_values = [next(gen, None) for gen in cluster_generators]
    print(initial_values)

    with open(output_filename, 'w', newline='') as f:
        writer_object = csv.writer(f)

        for current_word in all_words_reader(all_words_file):
            full_index = []

            for idx, word_pointer in enumerate(initial_values):
                try:
                    if word_pointer and word_pointer[0] == current_word:
                        full_index.extend(word_pointer[1])
                        word = next(cluster_generators[idx], None)
                        initial_values[idx] = word
                except StopIteration as s:
                    pass

            writer_object.writerow([current_word, *full_index])


if __name__ == "__main__":
    input_folder = "../gutenberg"
    output_folder = "output"
    print("hehe")
    divide_files(input_folder=input_folder, output_folder=output_folder, max_size_per_cluster=1024 * 1024 * 1024)
    merge('all_words.csv', output_folder, 'hehe.csv')
