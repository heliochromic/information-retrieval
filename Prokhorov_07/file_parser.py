from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
import re
import os
import csv


def normalize(word: str) -> str:
    translation_pattern = re.compile('[^a-zA-Z\']+')
    clean_word = re.sub(translation_pattern, '', word.lower())
    return clean_word


def parse_xml_bs4(file_path: str) -> Tuple[List[str], List[str], List[str]]:
    regex_pattern = r'\b[a-z]{2,15}\b'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'xml')

    xml_title = [word.lower() for word in soup.find('book-title').text.split()]
    xml_author_first_name = soup.find('first-name').text.lower()
    xml_author_last_name = soup.find('last-name').text.lower()

    p_tags = soup.find_all('p')
    xml_body = sorted(
        list(
            set(normalize(word) for p in p_tags for word in p.text.split() if
                re.match(regex_pattern, normalize(word)))
        )
    )
    xml_author = [xml_author_first_name, xml_author_last_name]

    return xml_title, xml_author, xml_body


def posting_builder(dictionary: Dict[str, List[str]], word: str, block_name: str, idx: int) -> None:
    if word not in dictionary.keys():
        dictionary[word] = []
    if f"{idx}.{block_name}" not in dictionary[word]:
        dictionary[word].append(f"{idx}.{block_name}")


def inverted_index(path: str) -> Dict[str, List[str]]:
    dictionary = {}

    for idx, filename in enumerate(os.listdir(path), 1):
        full_path = os.path.join(path, filename)
        title, author, body = parse_xml_bs4(full_path)

        for word in title:
            posting_builder(dictionary, word, 'title', idx)
        for word in author:
            posting_builder(dictionary, word, 'author', idx)
        for word in body:
            posting_builder(dictionary, word, 'body', idx)

    sorted_word_counts = dict(sorted(dictionary.items()))
    return sorted_word_counts


def to_csv(dictionary: Dict[str, List[str]], output_file: str) -> None:
    with open(output_file, mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',')
        for key, value in dictionary.items():
            writer.writerow([key, *value])


def to_dict(input_file: str = 'output.csv') -> Dict[str, List[str]]:
    dictionary = {}
    with open(input_file, mode='r') as input_file:
        reader = csv.reader(input_file, delimiter=',')
        for row in reader:
            dictionary[row[0]] = row[1:]
    return dictionary


def zone_score(word: str, path: str) -> Dict[str, float]:
    id_to_file = os.listdir(path)
    scores = {
        'title': 0.2,
        'author': 0.3,
        'body': 0.5
    }
    dictionary = {}
    postings = to_dict('output.csv')
    posting = postings.get(word, None)
    init_id = "0"
    score = 0
    if len(posting) > 0:
        for ids in posting:
            idx, zone = ids.split('.')
            if idx != init_id:
                init_id = idx
                score = 0
            score += scores[zone]
            dictionary[id_to_file[int(idx)-1]] = score
    return dictionary


if __name__ == "__main__":
    pth = '../books'
    inverted_index = inverted_index(pth)

    to_csv(inverted_index, 'output.csv')

    print(zone_score('the', pth))
