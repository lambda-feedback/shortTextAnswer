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
        # DEFAULT CASE: now in use
        case = similarity + " or if " + include
    else:
        raise ValueError("Invalid case. Please provide a valid case: 'perfect_match', 'include', 'exclude_word' or 'similarity'")

    instruction = example_scenario + base_instruction.format(response=response, answer=answer, case=case)
    return instruction

example_scenario = """Example Response='A cat is in the house' & Example Answer='A dog is in the house' -> False; 
Example Response='John's cat is in the house' & Example Answer='An animal in the building' -> True; \n"""
base_instruction = "Write 'True' if {case}; 'False' otherwise. Do not provide any explanation. \nResponse='{response}' & Answer='{answer}' ->"

# CASES for evaluation
# Include, Exclude of words are done by an algorithm and not by the model
perfect_match = "the Response perfectly matches the Answer"
include = "the Response is a subset of the Answer"          # descriptive version
include_word = "the Response contains the exact word '{keystring}'"
exclude_word = "the Response does not contain the exact word '{keystring}'"
similarity = "the Response is similar to or describes the Answer"

