"""Loads prompts for LLM calls"""

import importlib.util
import importlib
import os
import json
import re
from llm_analyst.core.exceptions import LLMAnalystsException
from llm_analyst.utils.app_logging import logging
from llm_analyst.core.config import Config

class Prompts:
    """Loads prompts for LLM calls"""
    _instance = None
    _prompts = None

    def __new__(cls,config=Config()):
        if cls._instance is None:
            cls._instance = super(Prompts, cls).__new__(cls)
            cls._prompts = cls._load_prompts(config)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        cls._instance = None
        cls._prompts = None

    @classmethod
    def _load_prompts(cls, config):
        prompts_json = None
        prompts = {}
        try:
            config_file_path = config.get_prompt_json_path()

            with open(config_file_path, "r", encoding='utf-8') as json_file:
                prompts_json = json.load(json_file)                

            for prompt_key in prompts_json:
                prompt_raw = prompts_json[prompt_key]
                if isinstance(prompt_raw, str):
                    prompt_value = prompt_raw
                elif isinstance(prompt_raw, list) and all(isinstance(x, str) for x in prompt_raw):
                    prompt_value = ''.join(prompt_raw)
                else:
                    logging.error("The prompt MUST be a list of Strings. All elements in the list are NOT Strings!")

                prompts[prompt_key]=prompt_value

        except Exception as e:
            logging.error("Error in Prompts._load_prompts %s",e)
            raise LLMAnalystsException("Error Prompts._load_prompts.") from e
        
        return prompts
    
    
    def print_params(self):
        """Helper function prints the available prompts and the required params for each"""
        ret_val = ""
        for prompt_key, prompt_value in self._prompts.items():
            params = self._extract_variables(prompt_value)
            ret_val += f"prompt: \"{prompt_key}\" params({params})\n"
        return ret_val
            
            
    def get_prompt(self, prompt_nm, **kwargs):
        """Get the formated prompt after appling the passed in key words if required"""
        prompt = self._prompts.get(prompt_nm, None)
        
        if prompt and kwargs:
            try:
                prompt = prompt.format(**kwargs)
            except KeyError as e:
                variables = self._extract_variables(prompt)
                error_msg = f"ERROR: The PROMPT: [{prompt_nm}] expects the following VARIABLES: [{variables}]"
                logging.error(error_msg)
                raise LLMAnalystsException(error_msg) from e

        if prompt is None:
            error_msg = f"ERROR: Prompt [{prompt_nm}] is not found in the prompt json."
            logging.error(error_msg)
            raise LLMAnalystsException(error_msg)
        
        return prompt
    
    def _extract_variables(self, text):
        variable_list = re.findall(r'\{(.*?)\}', text)
        variables = ', '.join(variable_list)
        return variables
