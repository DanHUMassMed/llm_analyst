import importlib.util
import importlib
import os
import json
import re
from llm_analyst.core.exceptions import LLMAnalystsException


class Prompts:
    _instance = None
    _prompts = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Prompts, cls).__new__(cls)
            cls._prompts = cls._load_prompts()
        return cls._instance


    @classmethod
    def _load_prompts(self):
        prompts_json = None
        try:
            package_nm="llm_analyst.resources"
            module_spec = importlib.util.find_spec(package_nm)
            package_path = os.path.dirname(module_spec.origin)
            config_file_path = os.path.join(package_path, 'prompts.json')

            with open(config_file_path, "r", encoding='utf-8') as json_file:
                prompts_json = json.load(json_file)

        except Exception as exc:
            raise LLMAnalystsException("Error loading prompts.") from exc
    
        if not prompts_json:
            raise LLMAnalystsException("Prompts json is empty.")
        
        return prompts_json


    def get_prompt(self, prompt_nm, **kwargs):
        prompt_raw = self._prompts.get(prompt_nm, None)
        prompt = None
        if prompt_raw:
            if isinstance(prompt_raw, str):
                prompt = prompt_raw
            elif isinstance(prompt_raw, list) and all(isinstance(x, str) for x in prompt_raw):
                prompt = ''.join(prompt_raw)
            else:
                print("The prompt MUST be a list of Strings. All elements in the list are NOT Strings!!!")
        
        if prompt and kwargs:
            try:
                prompt = prompt.format(**kwargs)
            except KeyError:
                variables = self._extract_variables(prompt)
                error_msg = f"The PROMPT: [{prompt_nm}] expects the following VARIABLES: [{variables}]"
                raise LLMAnalystsException(error_msg)


        if prompt is None:
            raise LLMAnalystsException("Prompt failed to process")
        
        return prompt
    
    def _extract_variables(self,text):
        variable_list = re.findall(r'\{(.*?)\}', text)
        variables = ', '.join(variable_list)
        return variables
