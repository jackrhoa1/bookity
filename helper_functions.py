from difflib import SequenceMatcher


# compares similarity of authors
def compare_authors(s1, s2):
    res = SequenceMatcher(None, s1, s2).ratio()
    return res

if __name__ == "__main__":
    compare_authors("C.S. Lewis","CS Lewis")