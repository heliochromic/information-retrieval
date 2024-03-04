from typing import Dict, List, Tuple
from time import perf_counter


def timer(func):
    def wrapper(*args, **kwargs):
        ts = perf_counter()
        result = func(*args, **kwargs)
        te = perf_counter()
        print(f"Function: {func.__name__}\n"
              f"Took: {te - ts:.6f} seconds")
        return result

    return wrapper


def query_parser(query: str, dataset: Dict[str, List[int]], logical_not, vector_length: int) -> \
        Tuple[List[List[int]], List[str]]:
    query = query.split()
    stack_words = []
    i = 0
    while i < len(query):
        if query[i] not in ['AND', 'OR']:
            next_word = query[i]
            while i < len(query) and next_word == 'NOT':
                i += 1
                next_word = query[i]
                if next_word != 'NOT' and i % 2 == 1:
                    if next_word not in dataset.keys():
                        stack_words.append(dataset['_UNKNOWN_WORD_'])
                    else:
                        stack_words.append(logical_not(dataset[next_word], vector_length))
            if i < len(query) and next_word != 'NOT':
                if next_word not in dataset.keys():
                    stack_words.append(dataset['_UNKNOWN_WORD_'])
                else:
                    stack_words.append(dataset[next_word])
        i += 1

    stack_operators = [token for token in query if token in ['AND', 'OR']]
    return stack_words, stack_operators


class IncidenceSearch:

    def __init__(self, vector_length: int):
        self.vector_length = vector_length

    @staticmethod
    def intersection(num_1: List[int], num_2: List[int]) -> List[int]:
        return [1 if a == b == 1 else 0 for a, b in zip(num_1, num_2)]

    @staticmethod
    def union(num_1: List[int], num_2: List[int]) -> List[int]:
        return [1 if a == 1 or b == 1 else 0 for a, b in zip(num_1, num_2)]

    @staticmethod
    def logical_not(num_1: List[int], vector_length) -> List[int]:
        return [1 if not a else 0 for a in num_1]

    @timer
    def search(self, query: str, dataset: Dict[str, List[int]]):
        stack_words, stack_operators = query_parser(query, dataset, self.logical_not, self.vector_length)
        for operator in stack_operators:
            word_1 = stack_words.pop(0)
            word_2 = stack_words.pop(0)
            if operator == "AND":
                stack_words.insert(0, self.intersection(word_1, word_2))
            elif operator == "OR":
                stack_words.insert(0, self.union(word_1, word_2))

        return stack_words[0]


class InvertedSearch:

    def __init__(self, vector_length: int):
        self.vector_length = vector_length

    @staticmethod
    def intersection(num_1: List[int], num_2: List[int]) -> List[int]:
        res_num = list()
        i, j = 0, 0

        while i < len(num_1) and j < len(num_2):
            if num_1[i] == num_2[j]:
                res_num.append(num_1[i])
                i += 1
                j += 1
            elif num_1[i] < num_2[j]:
                i += 1
            else:
                j += 1

        return res_num

    @staticmethod
    def union(num_1: List[int], num_2: List[int]) -> List[int]:
        return list(set(num_1 + num_2))

    @staticmethod
    def logical_not(num_1: List[int], vector_length: int) -> List[int]:
        res_num = list()
        i = 0
        while i < vector_length:
            i += 1
            if i not in num_1:
                res_num.append(i)

        return res_num

    @timer
    def search(self, query: str, dataset: Dict[str, List[int]]):
        stack_words, stack_operators = query_parser(query, dataset, self.logical_not, self.vector_length)
        for operator in stack_operators:
            word_1 = stack_words.pop(0)
            word_2 = stack_words.pop(0)
            if operator == "AND":
                stack_words.insert(0, self.intersection(word_1, word_2))
            elif operator == "OR":
                stack_words.insert(0, self.union(word_1, word_2))

        return stack_words[0]

