import math
import string
import numpy as np
import numpy.linalg

from nltk.corpus import wordnet

def evaluation_function(response, answer, params):
    """
    Function used to evaluate a student response.
    ---
    The handler function passes three arguments to evaluation_function():

    - `response` which are the answers provided by the student.
    - `answer` which are the correct answers to compare against.
    - `params` which are any extra parameters that may be useful,
        e.g., error tolerances.

    The output of this function is what is returned as the API response
    and therefore must be JSON-encodable. It must also conform to the
    response schema.

    Any standard python library may be used, as well as any package
    available on pip (provided it is added to requirements.txt).

    The way you wish to structure you code (all in this function, or 
    split into many) is entirely up to you. All that matters are the 
    return types and that evaluation_function() is the main function used 
    to output the evaluation response.
    """

    print(wordnet.synsets("test")[0])

    return {
        "is_correct": True
    }

def word_similarity(word1, word2):
    synsets1 = wordnet.synsets(word1)
    synsets2 = wordnet.synsets(word2)

    # Find LCA
    dist = 0
    for synset1, synset2 in zip(synsets1, synsets2):
        if synset1.pos() is not synset2.pos():
            continue
        dist = max(dist, synset1.wup_similarity(synset2))
        break
    return dist

def sentence_similarity(response: str, answer: str):
    for punc in string.punctuation:
        response = response.replace(punc, ' ')
        answer = answer.replace(punc, ' ')
    response_words = response.split()
    answer_words = answer.split()
    all_words = list(set((response_words + answer_words)))

    response_scores = []
    answer_scores = []

    for word in all_words:
        best_similarity = 0
        best_word = word
        if word in response_words:
            best_similarity = 1
        else:
            for other_word in response_words:
                if word_similarity(word, other_word) > best_similarity:
                    best_similarity = word_similarity(word, other_word)
                    best_word = other_word
        response_scores.append(best_similarity * 1) # TODO: Use word freq

    for word in all_words:
        best_similarity = 0
        best_word = word
        if word in answer_words:
            best_similarity = 1
        else:
            for other_word in answer_words:
                if word_similarity(word, other_word) > best_similarity:
                    best_similarity = word_similarity(word, other_word)
                    best_word = other_word
        answer_scores.append(best_similarity * 1) # TODO: Use word freq

    print(response_scores)
    print(answer_scores)
    score = np.dot(response_scores, answer_scores)/(np.linalg.norm(response_scores) * np.linalg.norm(answer_scores))
    return score

if __name__ == "__main__":
    print(evaluation_function("This is the response", "This is the answer", None))
    print(sentence_similarity("Solid, liquid, gas", "boat, plane, volcano"))
