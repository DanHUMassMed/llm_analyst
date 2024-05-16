""" Configuration Class for LLM Analyst """
import importlib.util
import importlib
import os
import json
from enum import Enum
from llm_analyst.exceptions import LLMAnalystsException



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
        config_json = self._get_config_file()
        self.__data = self._get_values_for_config(config_json)

    def __getattr__(self, name):
        try:
            return getattr(self.__data, name)
        except AttributeError:
            return self.__data[name]
       
    def __dir__(self):
        return self.__data.keys()
    
    def _get_config_file(self):
        """ Get config file from environment or use the default config.
        """
        config_json = None
        module_spec = importlib.util.find_spec(__name__)
        package_path = os.path.dirname(module_spec.origin)
        config_file_path = os.path.join(package_path, 'resources/llm_analyst.config')
        config_file = os.getenv('LLM_ANALYST_CONFIG',config_file_path) 
        with open(config_file, "r", encoding='utf-8') as json_file:
            config_json = json.load(json_file)
        return config_json


    def _get_values_for_config(self, config_json):
        config_data = {}
        for key in config_json.keys():
            default_value = config_json[key]['default_val']
            env_var = config_json[key]['env_var']
            env_value = os.getenv(env_var)
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

            # if key == "search_retriever":
            #     value = self._get_search_retriever(value)

            # if key == "llm_provider":
            #     value = self._get_llm_provider(value)

            config_data[key]=value

        return config_data

    def _get_search_retriever(self, search_retriever: str):
        module_name = "llm_analyst.retrievers.search_retrievers"

        try:
            module = importlib.import_module(module_name)
            retriever = getattr(module, search_retriever)
            print(f"Successfully imported function {search_retriever}")
        except (ImportError, AttributeError) as exc:
            raise LLMAnalystsException("Retriever not found.") from exc
        
        return retriever


    
    def _get_llm_provider(self, llm_provider: str):
        match llm_provider:
            case "openai":
                from llm_analyst.llm_provider.openai import OpenAIProvider
                llm_provider = OpenAIProvider
            case _:
                raise LLMAnalystsException("LLM provider not found.")

        return llm_provider
