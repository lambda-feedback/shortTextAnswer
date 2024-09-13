def build_instruction(response, answer, case, keystring=""):
    """
    Build instruction for the SLM task
    """

    if case == 'include_word':
        # CASE for keystring check
        case = include_word.format(keystring=keystring)
        instruction = example_scenario_keystring + base_instruction_keystring.format(keystring=keystring, answer=answer, case=case)
    elif case == 'exclude_word':
        # NOTE: (should_countain == false) this is done by NLP function
        case = exclude_word.format(keystring=keystring)
    elif case == 'similarity':
        # DEFAULT CASE for whole sentence check
        case = similarity + " or if " + include
        instruction = example_scenario + base_instruction.format(response=response, answer=answer, case=case)
    else:
        raise ValueError("Invalid case. Please provide a valid case: 'include', 'exclude_word' or 'similarity'")


    return instruction

example_scenario = """Example Response='A cat is in the house' & Example Answer='A dog is in the house' -> False; 
Example Response='John's cat is in the house' & Example Answer='An animal in the building' -> True; \n"""
base_instruction = "Write 'True' if {case}; 'False' otherwise. Do not provide any explanation. \nResponse='{response}' & Answer='{answer}' ->"

example_scenario_keystring = """Example Keystrings='generate fake data' & Example Answer='The algorithm generates false data.' -> True;
Example Keystrings='generate fake data' & Example Answer='The algorithm receives data of fake people.' -> False; \n"""
base_instruction_keystring = "Write 'True' if {case}; 'False' otherwise. Do not provide any explanation. \nKeystrings='{keystring}' & Answer='{answer}' ->"

# CASES for evaluation
# Include, Exclude of words are done by an algorithm and not by the model
perfect_match = "the Response perfectly matches the Answer"
include_word = "the Response contains mentions the '{keystring}' or describes something similar"
exclude_word = "the Response does not contain '{keystring}'"
similarity = "the Response is similar to or describes the Answer"
include = "the Response is a subset of the Answer"          # descriptive version

