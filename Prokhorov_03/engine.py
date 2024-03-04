import os

from typing import Dict, List
from time import perf_counter
from file_parser import biword_index, coordinate_inverted_index


def timer(func):
    def wrapper(*args, **kwargs):
        ts = perf_counter()
        result = func(*args, **kwargs)
        te = perf_counter()
        print(f"Function: {func.__name__}\n"
              f"Took: {te - ts:.6f} seconds")
        return result

    return wrapper


def index_to_list(filenames: str, index: list) -> list:
    r_list = list()
    for i in index:
        r_list.append(filenames[i - 1])
    return r_list


@timer
def biword_parser(query: str, dictionary: Dict[str, List[int]]) -> List[int]:
    sets_list = []
    query = [word.lower().strip('.,!:?') for word in query.split()]
    for i in range(len(query) - 1):
        biword = f'{query[i]} {query[i + 1]}'
        current_set = set(dictionary.get(biword, []))
        sets_list.append(current_set)
    if sets_list:
        result_set = set.intersection(*sets_list)
        return list(result_set)
    else:
        return []


def inverted_intersection(num_1: List[int], num_2: List[int], k: int = 0) -> List[int]:
    res_num = list()
    i = j = 0

    while i < len(num_1) and j < len(num_2):
        if num_1[i] + k == num_2[j]:
            res_num.append(num_1[i])
            i += 1
            j += 1
        elif num_1[i] + k < num_2[j]:
            i += 1
        else:
            j += 1

    return res_num


def positional_intersection(index_1: Dict[int, List[int]], index_2: Dict[int, List[int]], k: int = 1):
    res_num = list()
    intersected_list = inverted_intersection(list(index_1.keys()), list(index_2.keys()))

    for idx in intersected_list:
        coordinates_1 = index_1[idx]
        coordinates_2 = index_2[idx]
        if len(inverted_intersection(coordinates_1, coordinates_2, k)) > 0:
            res_num.append(idx)

    return res_num


@timer
def positional_parser(query: str, dictionary: Dict[str, Dict[int, List[int]]]) -> List[int]:
    sets_list = []
    query = [word.lower().strip('.,!:?') for word in query.split()]

    if not query:
        return []

    for i in range(len(query) - 1):
        common_indices = positional_intersection(dictionary[query[i]], dictionary[query[i + 1]], k=1)

        sets_list.append(set(common_indices))

    if sets_list:
        result_set = set.intersection(*sets_list)
        return list(result_set)
    else:
        return []


query = 'Copyright laws are changing all over the world. Be sure to check the copyright laws for your country before downloading'
filenames = os.listdir('../Dataset')[:10]

biword_indeces = biword_index(filenames, path='../Dataset')
print(index_to_list(filenames, biword_parser(query=query, dictionary=biword_indeces)))

coordinate_index = coordinate_inverted_index(filenames, path='../Dataset')
print(index_to_list(filenames, positional_parser(query=query, dictionary=coordinate_index)))
