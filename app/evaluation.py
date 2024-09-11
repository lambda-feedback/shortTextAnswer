try:
    from .nlp_evaluation import evaluation_function as nlp_evaluation_function
except ImportError:
    from nlp_evaluation import evaluation_function as nlp_evaluation_function

try:
    from .slm_evaluation import evaluation_function as slm_evaluation_function
except ImportError:
    from slm_evaluation import evaluation_function as slm_evaluation_function

try:
    from .evaluation_response_utilities import EvaluationResponse
except ImportError:
    from evaluation_response_utilities import EvaluationResponse

def evaluation_function(response, answer, params) -> EvaluationResponse:
    """
    Function that allows for various types of evaluation of a short text answer.
    params can contain the following:
    - evaluation_type: 'nlp' or 'slm' (default is 'nlp')
    """

    eval_response = EvaluationResponse()
    eval_response.is_correct = False

    if params is not None and "evaluation_type" in params:
        evaluation_type = params["evaluation_type"]
    else:
        evaluation_type = "nlp"

    if evaluation_type == "nlp":
        eval_response = nlp_evaluation_function(response, answer, params)
    elif evaluation_type == "slm":
        eval_response = slm_evaluation_function(response, answer, params)

    return eval_response