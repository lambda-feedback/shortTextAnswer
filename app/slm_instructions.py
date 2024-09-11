def build_instruction(response, answer, case, keystring=""):
    """
    Build instruction for the SLM task
    """
    if case == 'perfect_match':
        case = perfect_match
    elif case == 'include':
        case = include
    elif case == 'include_word':
        case = include_word.format(keystring=keystring) + " and if " + similarity
    elif case == 'exclude_word':
        case = exclude_word.format(keystring=keystring) #+ " and if " + similarity
    elif case == 'similarity':
        case = similarity
    else:
        raise ValueError("Invalid case. Please provide a valid case: 'perfect_match', 'include', 'exclude_word' or 'similarity'")

    instruction = base_instruction.format(response=response, answer=answer, case=case)
    return instruction

base_instruction = "Compare the following two sections: Response='{response}' & Answer='{answer}'. Write 'True' if {case}; 'False' otherwise. Do not provide any explanation."

# CASES for evaluation
# TODO: Include, Exclude of words should be done by an algorithm and not by the model
perfect_match = "the Response perfectly matches the Answer"
include = "the Answer includes the Response"
include_word = "the Response contains the exact word '{keystring}'"
exclude_word = "the Response does not contain the exact word '{keystring}'"
similarity = "the Response is similar to or describes the Answer"