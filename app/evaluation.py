import pickle
import string
import time

import gensim
import numpy as np
import numpy.linalg
from nltk.corpus import stopwords
from nltk import word_tokenize

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

    w2v_similarity = sentence_similarity_mean_w2v(response, answer)

    # if params is not None and "keywords" in params:
    #     keywords = params["keywords"]
    #     for keyword in keywords:
    #         for resp_score in response_scores:
    #             if resp_score[1] == keyword:
    #                 continue
    #         return {
    #             "is_correct": False,
    #             "result": {
    #                 "similarity_value": similarity,
    #                 "Problematic_word": keyword
    #             },
    #             "feedback": f"Cannot determine if the answer is correct. Please provide more details about '{keyword}"
    #         }



    if w2v_similarity > 0.75:
        return {
            "is_correct": True,
            "result": {
                "similarity_value": w2v_similarity
            },
            "feedback": "Correct!"
        }

    else:
        similarity, response_scores, answer_scores = sentence_similarity(response, answer)
        dif = 0
        word = None
        for (resp_score, ans_score) in zip(response_scores, answer_scores):
            if ans_score[0] - resp_score[0] > dif:
                dif = ans_score[0] - resp_score[0]
                word = resp_score[1]

        return {
            "is_correct": False,
            "result": {
                "similarity_value": w2v_similarity,
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


def preprocess_tokens(text: str):
    text = text.lower()
    to_remove = stopwords.words('english') + list(string.punctuation)
    tokens = [word for word in word_tokenize(text) if word not in to_remove]
    return tokens

def sentence_similarity_mean_w2v(response: str, answer: str):
    with open('w2v', 'rb') as fp:
        w2v = pickle.load(fp)
    response = preprocess_tokens(response)
    answer = preprocess_tokens(answer)
    response_embeddings = [w2v[word] for word in response if w2v.has_index_for(word)]
    answer_embeddings = [w2v[word] for word in answer if w2v.has_index_for(word)]
    response_vector = np.mean(response_embeddings, axis=0)
    answer_vector = np.mean(answer_embeddings, axis=0)
    return float(np.dot(response_vector, answer_vector) / (np.linalg.norm(response_vector) * np.linalg.norm(answer_vector)))
    # TODO

if __name__ == "__main__":
    pass
    # print(time.process_time())
    # print(evaluation_function("density, velocity,", "Density, Velocity, Viscosity, Length", None))
    # print(evaluation_function("test", "test", None))
    # print(time.process_time())
