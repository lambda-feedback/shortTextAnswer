from gpt4all import GPT4All
import time
from typing import Any, TypedDict
try:
    from .evaluation_response_utilities import EvaluationResponse
except ImportError:
    from evaluation_response_utilities import EvaluationResponse

try:
    from .slm_instructions import build_instruction
except ImportError:
    from slm_instructions import build_instruction

try:
    from .nlp_evaluation import evaluation_function as nlp_evaluation_function
except ImportError:
    from nlp_evaluation import evaluation_function as nlp_evaluation_function

class Params(TypedDict):
    pass

model = GPT4All(model_name="Phi-3.5-mini-instruct-Q6_K.gguf",model_path="app/models/", allow_download=False) # downloads / loads the model
# instruction = "Compare the following two sections: Response='{response}' & Answer='{answer}'. Write 'True' if the response perfectly matches the answer, 'False' otherwise. Do not provide any explanation."

def evaluation_function(response: Any, answer: Any, params: Any) -> EvaluationResponse:
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
    start_time = time.process_time()

    eval_response = EvaluationResponse() 
    eval_response.is_correct = False
    eval_response.add_evaluation_type("slm")
    evaluation_instruction = ""
    
    """
    (Reverted) Cases for exact_match or inclusion of a given word to distinguish between instruction prompts for the model
        -> such checks are done by the NLP algorithm and not by the model
        -> model only checks for context similarity between the response and the answer
    TODO: Could the eval function receive the question for context checking? 
    """

    # if params is not None and "keystrings" in params:
    #     keystrings = params["keystrings"]
    #     # problematic_keystring = None
    #     for keystring_object in keystrings:

    #         # if either exact_match , should_contain or custom_feedback is in the keystring object
    #         # then --- NLP evaluation function --- is called
    #         # if 'exact_match' in keystring_object or 'should_contain' in keystring_object or 'custom_feedback' in keystring_object:
    #         #     return nlp_evaluation_function(response, answer, params)
    #         # else:
    #         #     evaluation_instruction = build_instruction(response, answer, "similarity")

    #         # Unpack keystring object
    #         keystring = keystring_object['string']      # string that evaluation and feedback will be focused on
    #         exact_match = keystring_object['exact_match'] if 'exact_match' in keystring_object else False   #TODO(change naming): this looks for inclusion of a word, not exact match of the whole answer
    #         should_contain = keystring_object['should_contain'] if 'should_contain' in keystring_object else True 
    #         custom_feedback = keystring_object['custom_feedback'] if 'custom_feedback' in keystring_object else None
            
    #         if exact_match:
    #             evaluation_instruction = build_instruction(response, answer, "include_word", keystring)
    #         elif should_contain:
    #             evaluation_instruction = build_instruction(response, answer, "include")
    #         elif not should_contain:
    #             evaluation_instruction = build_instruction(response, answer, "exclude_word", keystring)
    #         else:
    #             # default to similarity case
    #             evaluation_instruction = build_instruction(response, answer, "similarity")
    # else:
    # default to similarity case if no parameters are provided
    evaluation_instruction = build_instruction(response, answer, "similarity")

    with model.chat_session():
        llm_response = model.generate(evaluation_instruction, max_tokens=10)
        end_time = time.process_time()

        eval_response.add_processing_time(end_time - start_time)
        eval_response.add_metadata("response", response)
        is_correct = process_response_corectness(llm_response)
        feedback = ""
        if is_correct is not None:
            eval_response.is_correct = is_correct
            feedback = "The response is {}.".format("correct" if is_correct else "incorrect")
            eval_response.add_feedback(("feedback", feedback))
        else:
            eval_response.is_correct = False
            feedback = "<LLM RESPONSE ERROR> The response could not be evaluated."
            eval_response.add_feedback(("feedback", feedback))

        # print("~~~~~~~~~~~~~~~~")
        # print("Instruction: ", evaluation_instruction)
        # print("Feedback:", llm_response)
        # for feedback_index in eval_response.get_feedback("feedback"):
        #     print(eval_response._feedback[feedback_index])
        # print("-- Time taken to generate response: ", end_time - start_time, " seconds --")

    return eval_response

def process_response_corectness(result: Any) -> bool:
    result = result.lower()
    if "true" in result:
        return True
    elif "false" in result:
        return False
    else:
        return None