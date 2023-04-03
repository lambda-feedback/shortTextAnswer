import pickle
from nltk.corpus import brown
freqs = {}
def preprocess_word_freqs():
    for word in brown.words():
        if not word in freqs:
            freqs[word] = 0
        freqs[word] = freqs[word] + 1

    with open('word_freqs', 'wb') as fp:
        pickle.dump(freqs, fp)

    with open('brown_length', 'wb') as fp:
        pickle.dump(len(brown.words()), fp)

if __name__ == "__main__":
    preprocess_word_freqs()