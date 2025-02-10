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
        load_dotenv()

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
        remaining_answers = set(answers)  # Use a set for faster removal
        
        for res in responses:
            matched_word = None
            for ans in list(remaining_answers):  # Convert set to list for iteration
                eval_result = chain.invoke({"word": res, "target": ans})
                eval_result_content = eval_result.content if config.mode == 'gpt' else eval_result
                similarity_result = parser.invoke(eval_result_content)
                
                if similarity_result == "True":
                    matched_word = ans
                    matched_pairs.append((res, ans))
                    remaining_answers.discard(ans)  # Ensure immediate removal
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

# Example Usage
if __name__ == "__main__":
    custom_config = Config()
    print(evaluation_function(
        ["Density","Density","Density"], #response
        ["Density","Viscosity","Length","Density","Gravity","Viscosity","Length"], #answer
        custom_config
    ))
    
    # print(evaluation_function(
    #     "Molecules are made out of atoms", 
    #     "Many atoms form a molecule", 
    #     {'keystrings': [{'string': 'molecule'}, {'string': 'proton', 'exact_match': True}]},
    #     custom_config
    # ))