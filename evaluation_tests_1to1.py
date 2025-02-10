import unittest

#from shortTextAnswer.app.evaluation_1to1 import evaluation_function

########################
import time
import os
import re
import pandas as pd
from langchain.schema.runnable import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

class Config:
    def __init__(self, mode='gpt', llama_version='3_1_8B', temperature=0.01, max_new_token=5):
        self.env_path = '/Users/zhuangfeigao/Documents/GitHub/Lambda_Feedback_Gao/login_configs.env'
        load_dotenv(dotenv_path=self.env_path)

        self.mode = mode  # Options: 'gpt', 'llama3'
        self.llama_version = llama_version
        self.temperature = temperature
        self.max_new_token = max_new_token
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.huggingfacehub_api_token = os.getenv("HUGGINGFACE_AUTHORIZATION")
        self.endpoint_3_1_8B = os.getenv("LLAMA3_1_8B_ENDPOINT")

def setup_llm(config):
    """Initialize the LLM model (GPT-4o or LLaMA 3) based on the given configuration."""
    if config.mode == 'gpt':
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=config.temperature,
            max_tokens=config.max_new_token,
            openai_api_key=config.openai_api_key
        )
    elif config.mode == 'llama3':
        from langchain_huggingface import HuggingFaceEndpoint
        return HuggingFaceEndpoint(
            endpoint_url=config.endpoint_3_1_8B,
            max_new_tokens=config.max_new_token,
            temperature=config.temperature,
            huggingfacehub_api_token=config.huggingfacehub_api_token
        )

def evaluation_function(response, answer, config=None):
    """Evaluates the given response against the answer using LLaMA 3 or GPT-4o."""
    start_time = time.process_time()

    # Ensure config is provided
    if config is None:
        config = Config()

    # Initialize LLM
    llm = setup_llm(config)

    # Define prompt template
    prompt_template = PromptTemplate(
        template= '''
        ### Instruction:
        Determine if the 2 words are semantically similar. Provide one of the following responses:
        - "True" if the words are semantically the same.
        - "False" if the words are semantically different.

        ### Examples:
        Word1: "happy", Word2: "happy"  
        Response: True

        Word1: "happy", Word2: "joyful"  
        Response: True

        Word1: "cat", Word 2: "dog"  
        Response: False

        Word1: "bank", Word 2: "actor"  
        Response: False

        ### Input:
        Word1:{target}, Word2:{word}

        ### Response:
        ''',
        input_variables=["target", "word"]
    )

    # Helper function to extract True/False from model response (only extract the last one)
    def parse_last_boolean(response):
        matches = re.findall(r'\b(true|false)\b', response, re.IGNORECASE)
        return matches[-1].capitalize() if matches else "Unsure"

    parser = RunnableLambda(parse_last_boolean)
    
    # Define processing chain
    chain = prompt_template | llm 

    def recursive_evaluation(responses, answers):
        results = []
        matched_pairs = []  # Store matched word pairs
        unmatched_responses = []  # Store unmatched responses
        
        for res in responses:
            matched_word = None
            for ans in answers:
                eval_result = chain.invoke({"word": res, "target": ans})
                eval_result_content = eval_result.content if config.mode == 'gpt' else eval_result
                similarity_result = parser.invoke(eval_result_content)
                
                if similarity_result == "True":
                    matched_word = ans
                    matched_pairs.append((res, ans))
                    break  # Exit loop after first match
            
            if matched_word:
                results.append(True)
            else:
                results.append(False)
                unmatched_responses.append(res)
        
        return all(results), matched_pairs, unmatched_responses

    # # LLM-based evaluation
    # response = chain.invoke({"word": response, "target": answer})
    
    # # openAI and Huggingface has different ways to engage with parser, therefore invoke the parser seperately
    # is_correct = parser.invoke(response.content if config.mode == 'gpt' else response)
    # # similarity_result = parser.invoke(llm_output)
    if not (isinstance(response, list) and all(isinstance(item, str) for item in response) and 
            isinstance(answer, list) and all(isinstance(item, str) for item in answer)):
        return {"is_correct": False, "error": "Invalid input: response and answer must be lists of strings."}
    
    is_correct, correct_answers, incorrect_answers = recursive_evaluation(response, answer)
    return {
        "is_correct": is_correct,
        "result": {
            "response": {"corrrect": correct_answers,
                         "incorrect": incorrect_answers},
            "processing_time": time.process_time() - start_time,
            "method": "LLM-based comparison"
        },
        "feedback": "Feedback generation agent not implemented yet."
    }

########################
class TestEvaluationFunction(unittest.TestCase):
    """
        TestCase Class used to test the algorithm.
        ---
        Tests are used here to check that the algorithm written 
        is working as it should. 
        
        It's best practise to write these tests first to get a 
        kind of 'specification' for how your algorithm should 
        work, and you should run these tests before committing 
        your code to AWS.

        Read the docs on how to use unittest here:
        https://docs.python.org/3/library/unittest.html

        Use evaluation_function() to check your algorithm works 
        as it should.
    """
    def test_returns_is_correct_true(self):
        response, answer, params = "A xor gate takes 2 inputs", "There are 2 inputs in a xor gate", dict()
        result = evaluation_function(response, answer, params)
        
        self.assertEqual(result.get("is_correct"), True)

    def test_reynolds_number_is_correct(self):
        answer, params = 'Density, Velocity, Viscosity, Length', dict()
        correct_responses = [
            'density,velocity,viscosity,length',
            'Density,Velocity,Viscosity,Length',
            'density,characteristic velocity,viscosity,characteristic length',
            'Density,Velocity,Shear viscosity,Length',
            'density,velocity,viscosity,lengthscale',
            'density,velocity,shear viscosity,length',
            'density,characteristic velocity,shear viscosity,characteristic lengthscale',
            'density,velocity,shear viscosity,characteristic lengthscale',
            'density,velocity,viscosity,length scale',
            'pressure,characteristic velocity of flow,shear viscosity,characteristic length scale',
        ]

        for response in correct_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), True, msg=f'Response: {response}')

    def test_reynolds_number_is_incorrect(self):
        answer, params = 'Density, Velocity, Viscosity, Length', dict()
        incorrect_responses = [
            'density,,,',
            'rho,u,mu,L',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), False, msg=f'Response: {response}')

    def test_reynolds_number_is_incorrect_with_keystring(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {'keystrings': [{'string': 'density'}, {'string': 'velocity'}, {'string': 'viscosity'}, {'string': 'length'}]}
        incorrect_responses = [
            'density,velocity,visc,',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), False, msg=f'Response: {response}')

    def test_reynolds_number_exact_match(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {
            'keystrings': [{'string': 'velocity', 'exact_match': True}]}
        incorrect_responses = [
            'density,speed,viscosity, length',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), False, msg=f'Response: {response}')

    def test_reynolds_number_should_not_contain(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {
            'keystrings': [{'string': 'direction', 'should_contain': False}]}
        incorrect_responses = [
            'density,speed,viscosity, length, direction',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), False, msg=f'Response: {response}')

    def test_reynolds_number_custom_feedback(self):
        answer, params = 'Density, Velocity, Viscosity, Length', {
            'keystrings': [{'string': 'banana', 'custom_feedback': 'custom feedback with the word banana'}]}
        incorrect_responses = [
            'An incorrect response',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertIn('banana', result.get("feedback"), msg=f'Response: {response}')

    navier_stokes_answer = "The density of the film is uniform and constant, therefore the flow is incompressible. " \
                           "Since we have incompressible flow, uniform viscosity, Newtonian fluid, " \
                           "the most appropriate set of equations for the solution of the problem is the " \
                           "Navier-Stokes equations. The Navier-Stokes equations in Cartesian coordinates are used: " \
                           "mass conservation and components of the momentum balance"

    navier_stokes_params = {'keystrings': [{'string': 'Navier-Stokes equations'}, {'string': 'mass conservation'},
                                                                    {'string': 'momentum balance'}, {'string': 'incompressible flow'},
                                                                    {'string': 'uniform viscosity'}, {'string': 'Newtonian fluid'}]}

    def test_navier_stokes_equation(self):
        answer, params = self.navier_stokes_answer, dict()
        correct_responses = [
            #'Navier-stokes. Continuum, const and uniform density and viscosity so incompressible, newtonian. Fits all '
            #'requirements for navier stokes',
            'Navier-Stokes in a Cartesian reference coordinates would be chosen for this particular flow. This is due '
            'to the reason that the flow is Newtonian, the viscosity is uniform and constant. Additionally, '
            'the density is uniform and constant; implying that it is an incompressible flow. This flow obeys the '
            'main assumptions in order to employ the Navier Stokes equations.',
        ]

        for response in correct_responses:
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get("is_correct"), True, msg=f'Response: {response}')

    def test_negation(self):
        answer, params = 'light blue', dict()
        correct_responses = [
            'bright blue',
            'light blue',
            'not light blue', # WARNING: THIS test should be False, but the similarity algorithm cannot handle negations
            'dark blue'       # WARNING: THIS test should be False, but the similarity algorithm cannot handle context understanding
        ]

        for response in correct_responses:
            result = evaluation_function(response, answer, params)
            self.assertEqual(result.get("is_correct"), True, msg=f'Response: {response}')

from dotenv import load_dotenv
import os
class Config:
    def __init__(self, mode='gpt', llama_version='3_1_8B', temperature=0.01, max_new_token=5):
        self.env_path = '/Users/zhuangfeigao/Documents/GitHub/Lambda_Feedback_Gao/login_configs.env'
        load_dotenv(dotenv_path=self.env_path)

        self.mode = mode  # Options: 'gpt', 'llama3'
        self.llama_version = llama_version
        self.temperature = temperature
        self.max_new_token = max_new_token
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.huggingfacehub_api_token = os.getenv("HUGGINGFACE_AUTHORIZATION")
        self.endpoint_3_1_8B = os.getenv("LLAMA3_1_8B_ENDPOINT")

params = Config()
if __name__ == "__main__":
    unittest.main()