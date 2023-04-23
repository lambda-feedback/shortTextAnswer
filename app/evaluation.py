import pickle
import string
import time

import numpy as np
import numpy.linalg

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

    similarity, response_scores, answer_scores = sentence_similarity(response, answer)


    if params is not None and "keywords" in params:
        keywords = params["keywords"]
        for keyword in keywords:
            for resp_score in response_scores:
                if resp_score[1] == keyword:
                    continue
            return {
                "is_correct": False,
                "result": {
                    "similarity_value": similarity,
                    "Problematic_word": keyword
                },
                "feedback": f"Cannot determine if the answer is correct. Please provide more details about '{keyword}"
            }

    if similarity > 0.8:
        return {
            "is_correct": True,
            "result": {
                "similarity_value": similarity
            },
            "feedback": "Correct!"
        }

    else:
        dif = 0
        word = None
        for (resp_score, ans_score) in zip(response_scores, answer_scores):
            if ans_score[0] - resp_score[0] > dif:
                dif = ans_score[0] - resp_score[0]
                word = resp_score[1]

        return {
            "is_correct": False,
            "result": {
                "similarity_value": similarity,
                "Problematic_word": word
            },
            "feedback": f"Cannot determine if the answer is correct. Please provide more details about '{word}"
        }


def word_information_content(word, blen, freqs):
    if word not in freqs:
        f = 0
    else:
        f = freqs[word]
    return 1 - (np.log(f + 1)) / (np.log(blen + 1))


def word_similarity(word1, word2, w2v):
    if word1 == word2:
        return 1
    if not w2v.has_index_for(word1) or not w2v.has_index_for(word2):
        return 0
    return w2v.similarity(word1, word2)


def sentence_similarity(response: str, answer: str):
    response = response.lower()
    answer = answer.lower()
    for punc in string.punctuation:
        response = response.replace(punc, ' ')
        answer = answer.replace(punc, ' ')
    response_words = response.split()
    answer_words = answer.split()
    all_words = list(set((response_words + answer_words)))

    with open('brown_length', 'rb') as fp:
        blen = pickle.load(fp)
    with open('word_freqs', 'rb') as fp:
        freqs = pickle.load(fp)
    with open('w2v', 'rb') as fp:
        w2v = pickle.load(fp)

    def sencence_scores(common_words, sentence):
        scores = []
        for word in common_words:
            best_similarity = -1
            best_word = word
            for other_word in sentence:
                similarity = word_similarity(word, other_word, w2v)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_word = other_word
            scores.append(
                (best_similarity * word_information_content(word, blen, freqs) * word_information_content(best_word, blen, freqs), word))
        return scores

    response_scores = sencence_scores(all_words, response_words)
    answer_scores = sencence_scores(all_words, answer_words)

    resp_scores = response_scores.copy()
    ans_scores = answer_scores.copy()
    for idx in range(len(response_scores)):
        response_scores[idx] = response_scores[idx][0]
        answer_scores[idx] = answer_scores[idx][0]
    score = np.dot(response_scores, answer_scores) / (np.linalg.norm(response_scores) * np.linalg.norm(answer_scores))
    return score, resp_scores, ans_scores

def sentence_similarity_mean_w2v(response: str, answer: str):
    response = response.lower()
    answer = answer.lower()
    for punc in string.punctuation:
        response = response.replace(punc, ' ')
        answer = answer.replace(punc, ' ')
    response_words = response.split()
    answer_words = answer.split()
    # TODO

# if __name__ == "__main__":
#     pass
#     print(time.process_time())
#     print(word_similarity('density', 'density'))
#     print(word_similarity('density', 'velocity'))
#     print(word_similarity('density', 'viscosity'))
#     print(word_similarity('density', 'length'))
#     print(evaluation_function("rho,u,mu,L", "Density, Velocity, Viscosity, Length", None))
#     print(time.process_time())
