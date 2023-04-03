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
        print('dictionary saved successfully to file')

if __name__ == "__main__":
    preprocess_word_freqs()