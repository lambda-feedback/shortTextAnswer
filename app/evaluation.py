import time
import os
import re
import pandas as pd
from langchain.schema.runnable import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

class Param:
    def __init__(self, mode='gpt', llama_version='3_1_8B', temperature=0.01, max_new_token=5):
        load_dotenv()

        self.mode = mode  # Options: 'gpt', 'llama3'
        self.llama_version = llama_version
        self.temperature = temperature
        self.max_new_token = max_new_token
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.huggingfacehub_api_token = os.getenv("HUGGINGFACE_AUTHORIZATION")
        self.endpoint_3_1_8B = os.getenv("LLAMA3_1_8B_ENDPOINT")

        self.response_num_required = 0 #initialise it with 0


def parse_input(input_data):
    """
    Parses input data, handling both semicolon-separated strings and nested list structures.
    
    Args:
        input_data (str or list): A semicolon-separated string or a nested list.
    
    Returns:
        list: A processed list of elements.
    """
    if isinstance(input_data, str):
        if input_data == "":
            return []
        return [item for item in input_data.split(';') if item]
    elif isinstance(input_data, list) and all(isinstance(sublist, list) for sublist in input_data):
        return [item for sublist in input_data for item in sublist]
    else:
        raise ValueError("Input must be either a semicolon-separated string or a nested list.")


def setup_llm(param: Param):
    """Initialize the LLM model (GPT-4o or LLaMA 3) based on the given configuration."""
    if param.mode == 'gpt':
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=param.temperature,
            max_tokens=param.max_new_token,
            openai_api_key=param.openai_api_key
        )
    # elif config.mode == 'llama3': # NOTE: langchain_huggingface expected "linux/arm64"
    #     from langchain_huggingface import HuggingFaceEndpoint
    #     return HuggingFaceEndpoint(
    #         endpoint_url=config.endpoint_3_1_8B,
    #         max_new_tokens=config.max_new_token,
    #         temperature=config.temperature,
    #         huggingfacehub_api_token=config.huggingfacehub_api_token
    #     )


def parse_last_boolean(response):
    """Extracts the last boolean value (True/False) from model response."""
    matches = re.findall(r'\b(true|false)\b', response, re.IGNORECASE)
    return matches[-1].capitalize() if matches else "Unsure"

def recursive_evaluation(responses, answers, chain, parser):
    """Evaluates a list of responses against a list of answers."""
    results = []
    matched_pairs = []  # Store matched word pairs
    unmatched_responses = []  # Store unmatched responses
    remaining_answers = set(answers)  # Use a set for faster removal
    
    for res in responses:
        matched_word = None
        for ans in list(remaining_answers):  # Convert set to list for iteration
            eval_result = chain.invoke({"word": res, "target": ans})
            eval_result_content = eval_result.content
            print("eval_result_content: ", eval_result_content) #TODO: debugging
            similarity_result = parser.invoke(eval_result_content)

            print("similarity_result: ", similarity_result, "; res: ", res, "; ans: ", ans) #TODO: debugging
            
            if similarity_result == "True":
                matched_word = ans
                #matched_pairs.append((res, ans))
                matched_pairs.append(res) #we dong want exact answer being given in the feedback
                remaining_answers.discard(ans)  # Ensure immediate removal
                break  # Exit loop after first match
        
        if matched_word:
            results.append(True)
        else:
            results.append(False)
            unmatched_responses.append(res)
    
    return all(results), matched_pairs, unmatched_responses

def evaluation_function(response, answer, param=None):
    """Evaluates the given response against the answer using LLaMA 3 or GPT-4o."""
    start_time = time.process_time()



    #split the response and answer into lists with semicolons
    response = parse_input(response)
    answer = parse_input(answer)

    print("response: ", response, "; answer: ", answer, "; param: ", param) #TODO: debugging

    
    # Ensure config is provided
    if param is None:
        print("param is None, set default...") #TODO: debugging
        param = Param()
    elif type(param) is dict:
        print("param is dict, load them...") #TODO: debugging
        param = Param(**param)
    print("param: ", param) #TODO: debugging
    
    # Initialize LLM
    print("Setting up LLM...") #TODO: debugging
    llm = setup_llm(param)
    print("LLM setup done") #TODO: debugging
    
    # Define prompt template
    prompt_template = PromptTemplate(
        template='''
        ### Instruction:
        Determine if the 2 words are semantically similar. Provide one of the following responses:
        - "True" if the words are semantically the same.
        - "False" if the words are semantically different.


        ### Examples:
        Word1: "velocity", Word2: "speed"  
        Response: True

        Word1: "Pressure", Word2: "pressure"  
        Response: True

        Word1: "molecule", Word2: "molecules"  
        Response: True

        Word1: "math function", Word2: "math formulae"  
        Response: True

        Word1: "photosynthesis", Word2: "plant energy conversion"  
        Response: True

        Word1: "neuron", Word2: "planet"  
        Response: False

        Word1: "gravity", Word2: "voltage"  
        Response: False

        Word1: "robotic", Word2: "not robotic"  
        Response: False

        Word1: "molecular", Word2: "atomic"  
        Response: False

        Word1: "dark blue", Word2: "light blue"  
        Response: False

        ### Input:
        Word1:{target}, Word2:{word}

        ### Response:
        ''',
        input_variables=["target", "word"]
    )
    
    parser = RunnableLambda(parse_last_boolean)
    chain = prompt_template | llm
    
    # Validate inputs
    if not (isinstance(response, list) and all(isinstance(item, str) for item in response) and 
            isinstance(answer, list) and all(isinstance(item, str) for item in answer)):
        return {"is_correct": False, "error": "Invalid input: response and answer must be lists of strings."}
    print("Valid Inputs received: response: ", response, "; answer: ", answer) #TODO: debugging

    print("Starting recursive evaluation...") #TODO: debugging
    is_correct, correct_answers, incorrect_answers = recursive_evaluation(response, answer, chain, parser)
    print("correct_answers: ", correct_answers, "; incorrect_answers: ", incorrect_answers) #TODO: debugging

    #check if student is inputting enough answers
    if len(response) < param.response_num_required:
        is_correct = False
    
    return {
        "is_correct": is_correct,
        "result": {
            "response": {"correct": correct_answers, "incorrect": incorrect_answers},
            "processing_time": time.process_time() - start_time,
            "method": "LLM-based comparison"
        },
        "feedback": f"Correct answers: {correct_answers}. Incorrect answers: {incorrect_answers}."
    }


# Example Usage
if __name__ == "__main__":
    custom_config = Param()
    print(evaluation_function(
        "speed,red", #response
        "red, velocity", #answer
        custom_config
    ))
    
    # print(evaluation_function(
    #     "Molecules are made out of atoms", 
    #     "Many atoms form a molecule", 
    #     {'keystrings': [{'string': 'molecule'}, {'string': 'proton', 'exact_match': True}]},
    #     custom_config
    # ))