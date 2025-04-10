import random

class Dict:
    def __init__(self, dict_file_path="dictionary.txt"):
        self.words = open(dict_file_path).readlines()
        self.words = [word.strip() for word in self.words]

    def get_random_word(self, min_len = 0, max_len = 0):
        if min_len > 0 and max_len > min_len:
            return random.choice([word for word in self.words if min_len <= len(word) <= max_len])
        return random.choice(self.words)