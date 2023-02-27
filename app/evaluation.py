def evaluation_function(response, answer, params):

    import math
    import string

    import nltk
    import numpy as np
    import numpy.linalg

    from nltk.corpus import wordnet
    from nltk.corpus import brown

    def preprocess_word_freqs():
        for word in brown.words():
            if not word in freqs:
                freqs[word] = 0
            freqs[word] = freqs[word] + 1
    
    def word_information_content(word):
        if word not in freqs:
            f = 0
        else:
            f = freqs[word]
        return 1 - (np.log(f + 1)) / (np.log(len(brown.words()) + 1))
    
    
    def word_similarity(word1, word2):
        synsets1 = wordnet.synsets(word1)
        synsets2 = wordnet.synsets(word2)
    
        # Find LCA
        dist = 0
        for synset1, synset2 in zip(synsets1, synsets2):
            # if synset1.pos() is not synset2.pos():
            #    continue
            dist = max(dist, synset1.wup_similarity(synset2))
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
            response_scores.append(
                (best_similarity * word_information_content(word) * word_information_content(best_word), word))
    
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
            answer_scores.append(
                (best_similarity * word_information_content(word) * word_information_content(best_word), word))
    
        resp_scores = response_scores.copy()
        ans_scores = answer_scores.copy()
        for idx in range(len(response_scores)):
            response_scores[idx] = response_scores[idx][0]
            answer_scores[idx] = answer_scores[idx][0]
        score = np.dot(response_scores, answer_scores) / (np.linalg.norm(response_scores) * np.linalg.norm(answer_scores))
        return score, resp_scores, ans_scores

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


freqs = {}


if __name__ == "__main__":
    preprocess_word_freqs()
    print(evaluation_function("A banana of characters", "A list of characters", None))
    print(evaluation_function("An undirected graph with no cycles and no double edges", "A simple undirected acyclic graph", {"keywords": ["acyclic"]}))
