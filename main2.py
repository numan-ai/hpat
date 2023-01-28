import pickle
from collections import defaultdict, Counter

import nltk

def main():
    with open('datasets/frequencies/ANC-all-count.txt', 'rb') as f:
        lines = f.readlines()

    TAG_MAP = {
        "-LRB-": "PUNCT",
        "-RRB-": "PUNCT",
        "#": "SYM",
        "$": "SYM",
        "''": "PUNCT",
        ",": "PUNCT",
        ".": "PUNCT",
        ":": "PUNCT",
        "AFX": "ADJ",
        "CC": "CCONJ",
        "CD": "NUM",
        "DT": "DET",
        "EX": "PRON",
        "FW": "X",
        "HYPH": "PUNCT",
        "IN": "ADP",
        "JJ": "ADJ",
        "JJR": "ADJ",
        "JJS": "ADJ",
        "LS": "X",
        "MD": "VERB",
        "NIL": "X",
        "NN": "NOUN",
        "NNP": "PROPN",
        "NNPS": "PROPN",
        "NNS": "NOUN",
        "PDT": "DET",
        "POS": "PART",
        "PRP": "PRON",
        "PRP$": "DET",
        "RB": "ADV",
        "RBR": "ADV",
        "RBS": "ADV",
        "RP": "ADP",
        "SYM": "SYM",
        "TO": "PART",
        "UH": "INTJ",
        "VB": "VERB",
        "VBD": "VERB",
        "VBG": "VERB",
        "VBN": "VERB",
        "VBP": "VERB",
        "VBZ": "VERB",
        "WDT": "DET",
        "WP": "PRON",
        "WP$": "DET",
        "WRB": "ADV",
        "``": "PUNCT",
    }

    freq = defaultdict(dict)
    for line in lines:
        line = line.decode('utf-8', errors='replace')
        word, lemma, poses, count = line.replace('\r\n', '').split('\t')
        for pos in poses.split('|'):
            if pos == 'UNC':
                continue
            pos = TAG_MAP[pos]
            freq[word][pos] = int(count)

    with open('datasets/frequencies/freqs.pkl', 'wb+') as f:
        pickle.dump(freq, f)

    exit()

    corpus = nltk.corpus.brown.tagged_sents(tagset='universal')

    freq = defaultdict(Counter)

    for sent in corpus:
        for word, tag in sent:
            freq[word.lower()][tag] += 1

    breakpoint()
    pass


if __name__ == '__main__':
    main()
