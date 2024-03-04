import collections


class TrieNode:
    def __init__(self):
        self.children = collections.defaultdict(TrieNode)
        self.is_end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        current = self.root
        for letter in word:
            current = current.children[letter]
        current.is_end = True

    def search(self, word: str) -> str:
        current = self.root
        result = ''
        for letter in word:
            current = current.children.get(letter)
            if current is None:
                return None
            result += letter
        return result if current.is_end else None

    def startsWith(self, prefix: str) -> set:
        current = self.root
        result_set = set()

        if prefix[-1] != '*':
            return self.search(prefix)

        prefix = prefix[:-1]
        for letter in prefix:
            current = current.children.get(letter)
            if not current:
                return result_set

        self._collect_words_with_prefix(current, prefix, result_set)
        return result_set

    def _collect_words_with_prefix(self, node, current_word, result_set):
        if node.is_end:
            result_set.add(current_word)

        for letter, child_node in node.children.items():
            self._collect_words_with_prefix(child_node, current_word + letter, result_set)
