""" Configuration Class for LLM Analyst """
import importlib.util
import importlib
import os
import json
from enum import Enum
from llm_analyst.core.exceptions import LLMAnalystsException
from llm_analyst.embedding_methods.embeddings_provider import get_embeddings_provider

## Explore using **kwargs to pass init params to configuration objects
##"fast_llm_model" :{"default_val":"openai",kwargs"model=gpt-3.5-turbo-16k, temperature="0.55"},

class ReportType(Enum):
    ResearchReport = 'research_report'
    ResourceReport = 'resource_report'
    OutlineReport = 'outline_report'
    CustomReport = 'custom_report'
    DetailedReport = 'detailed_report'
    SubtopicReport = 'subtopic_report'

class Config:
    """Config class for LLM Analyst."""

    def __init__(self):
        self.__data = None
        config_json = self._get_config_file() # Get Default values JSON
        self.__data = self._set_values_for_config(config_json)
        config_file_path = os.getenv('LLM_ANALYST_CONFIG', None)
        if config_file_path:
            # Get User defined values JSON
            config_json = self._get_config_file(config_file_path=config_file_path)
            self.__data = self._set_values_for_config(config_json)


    def __getattr__(self, name):
        try:
            return getattr(self.__data, name)
        except AttributeError:
            return self.__data[name]

    def __dir__(self):
        return self.__data.keys()

    def _get_config_file(self,config_file_path=None):
        """ Use the default config file override if environment vaiables are set.
        """
        config_json = None
        if not config_file_path:
            package_nm="llm_analyst.resources"
            module_spec = importlib.util.find_spec(package_nm)
            package_path = os.path.dirname(module_spec.origin)
            config_file_path = os.path.join(package_path, 'llm_analyst.config')

        with open(config_file_path, "r", encoding='utf-8') as json_file:
            config_json = json.load(json_file)

        if not config_json:
            raise LLMAnalystsException("Config file json failed to load.")
        
        return config_json


    def _set_values_for_config(self, config_json):
        config_data = {}
        if self.__data:
            config_data = self.__data
            
        for key in config_json.keys():
            default_value = config_json[key]['default_val']
            env_var = config_json[key].get('env_var')
            env_value = os.getenv(env_var) if env_var else None
            value = None
            if env_value is not None:
                if isinstance(default_value, int):
                    value = int(env_value)
                elif isinstance(default_value, float):
                    value = float(env_value)
                else:
                    value = env_value
            else:
                value = default_value

            if key == "internet_search" and value is not None:
                value = self._get_search_method(value)

            if key == "embedding_provider" and value is not None:
                value = self._get_embeddings_provider(value)

            if key == "llm_provider" and value is not None:
                value = self._get_llm_model(value)

            config_data[key]=value

        return config_data

    def _get_search_method(self, search_method: str):
        module_name = "llm_analyst.search_methods.internet_search"
        try:
            module = importlib.import_module(module_name)
            internet_search_method = getattr(module, search_method)
        except (ImportError, AttributeError) as exc:
            raise LLMAnalystsException("Search Method not found.") from exc

        return internet_search_method

    def _get_llm_model(self, llm_model_module: str):
        chat_model = None
        module_name = f"llm_analyst.chat_models.{llm_model_module}"
        try:
            module = importlib.import_module(module_name)
            chat_model_nm = llm_model_module.upper()+"_Model"
            chat_model = getattr(module, chat_model_nm)
        except (ImportError, AttributeError) as exc:
            raise LLMAnalystsException("Chat Model not found.") from exc

        return chat_model
    
    def _get_embeddings_provider(self, embeddings_proviver_nm):
        return get_embeddings_provider(embeddings_proviver_nm)
