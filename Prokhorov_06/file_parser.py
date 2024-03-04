import csv
from typing import List, Dict
from time import perf_counter
import os

OUTPUT_TEXT_FILE = "output_text_file.txt"
OUTPUT_BINARY_FILE = "output_binary_file.bin"


def timer(func):
    def wrapper(*args, **kwargs):
        ts = perf_counter()
        result = func(*args, **kwargs)
        te = perf_counter()
        print(f"Function: {func.__name__}\n"
              f"Took: {te - ts:.6f} seconds")
        return result

    return wrapper


def to_csv(words: List[str], indices: List[List[int]], output_file: str = 'output.csv') -> None:
    with open(output_file, mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',')
        for i in range(len(words)):
            writer.writerow([words[i], *indices[i]])


def file_size(filename: str) -> float:
    size = os.path.getsize(filename)
    return round(size / (1024 * 1024), 4)


def stats(filename: str) -> None:
    print(f"Filename             : {filename}\n"
          f"Collection size      : {file_size(filename)}Mb\n")


def frontal_package(words: List[str]) -> str:
    return "".join([f"{len(word)}{word}" for word in words])


def word_splitter(encoded_string: str) -> List[str]:
    result_list = []
    i = 0

    while i < len(encoded_string):
        if encoded_string[i].isdigit():
            num_length = int(encoded_string[i])
            i += 1

            if i < len(encoded_string) and encoded_string[i].isdigit():
                num_length = num_length * 10 + int(encoded_string[i])
                i += 1

            word = encoded_string[i: i + num_length]
            result_list.append(word)
            i += num_length
        else:
            i += 1

    return result_list


def gamma_encode(num: int):
    if num == 0:
        return '0'
    suffix = bin(num)[3:]
    return f"{len(suffix) * '1'}0{suffix}"


def gamma_decode(encoded_num: str):
    i = 0
    while encoded_num[i] != '0':
        i += 1
    return int(f"1{encoded_num[i + 1:]}", 2)


def decode_splitter(binary_string: str) -> List[List[int]]:
    r_list = []
    temp_list = []
    i = 0
    num_length = 0
    while i < len(binary_string):

        if binary_string[i] == '0':
            temp_list.append(gamma_decode(binary_string[i - num_length: i + num_length + 1]))
            i += num_length + 1
            num_length = 0
            if i > len(binary_string) - 1:
                i = 0
                break
            if binary_string[i: i + 2] == '00':
                r_list.append(temp_list)
                temp_list = []
                i += 1
        if binary_string[i] == '1':
            num_length += 1
        i += 1
    return r_list


def inverted_index_parser(input_file: str) -> Dict[str, List[int]]:
    dictionary = {}
    with open(file=input_file, mode='r', encoding='utf-8', errors='replace') as input_file:
        reader = csv.reader(input_file, delimiter=',')
        for idx, row in enumerate(reader, 1):
            dictionary[row[0]] = [int(x) for x in row[1:]]
    return dictionary


@timer
def compress(input_file: str, output_text_file: str = OUTPUT_TEXT_FILE, output_binary_file: str = OUTPUT_BINARY_FILE):
    indices = inverted_index_parser(input_file)
    keys_list = list(indices.keys())

    with open(output_text_file, "w") as text_file, open(output_binary_file, "wb") as binary_file:
        text_file.write(frontal_package(keys_list))

        r_string = ''.join([
            ''.join([gamma_encode(doc_id) for doc_id in index]) + '00'
            for index in indices.values()
        ])
        remainder = len(r_string) % 8
        if remainder != 0:
            r_string += '0' * remainder

        binary_data = bytes(int(r_string[i:i + 8], 2) for i in range(0, len(r_string), 8))

        binary_file.write(binary_data)


@timer
def decompress(input_binary_file: str, input_txt_file: str):
    with open(input_binary_file, "rb") as binary_file, open(input_txt_file, "r") as txt_file:
        binary_data = binary_file.read()
        binary_string = ''.join(format(byte, '08b') for byte in binary_data)
        indices = decode_splitter(binary_string)

        txt_data = txt_file.read()
        words = word_splitter(txt_data)
        to_csv(words, indices)


if __name__ == "__main__":
    stats('inverted_matrix.csv')
    compress(input_file='inverted_matrix.csv')

    stats('output_binary_file.bin')
    stats('output_text_file.txt')

    decompress(input_binary_file='output_binary_file.bin', input_txt_file='output_text_file.txt')
    stats('output.csv')

    print(
        f"Took: {round(100 * (file_size('output_text_file.txt') + file_size('output_binary_file.bin')) / file_size('inverted_matrix.csv'), 2)} %")
