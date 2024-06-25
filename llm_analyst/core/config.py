"""
This module provides a Config class for the LLM Analyst application, 
enabling configuration management through JSON files and environment variables.

"""

import importlib.util
import importlib
import os
import json
import keyword

from enum import Enum
from llm_analyst.core.exceptions import LLMAnalystsException
from llm_analyst.utils.app_logging import logging
from llm_analyst.utils.utilities import get_resource_path



class ReportType(Enum):
    RESEARCH_REPORT = "research_report"
    RESOURCE_REPORT = "resource_report"
    OUTLINE_REPORT = "outline_report"
    CUSTOM_REPORT = "custom_report"
    DETAILED_REPORT = "detailed_report"
    SUBTOPIC_REPORT = "subtopic_report"


class DataSource(Enum):
    WEB = "web"
    LOCAL_STORE = "local_store"
    SELECT_URLS = "select_urls"


class Config:
    """Config class for LLM Analyst.
    """
    
    def __init__(self):
        # These Attributes are added so the IDE identifies them as valid
        self.internet_search = None              # Any method name from internet_search.py
        self.embedding_provider = None           # embedding_provider options [ollama, huggingface]
        self.llm_provider = None                 # Any module under "chat_models" directory
        self.llm_model = None                    # A capability from chosen llm_provider
        self.llm_token_limit = None              # An attribute of the chosen llm_provider
        self.llm_temperature = None              # An attribute of the chosen llm_provider
        self.browse_chunk_max_length = None      # NOT USED
        self.summary_token_limit = None          # NOT USED
        self.max_search_results_per_query = None # Used by internet_search provider
        self.total_words = None                  # Passed as an attribute to the report prompt
        self.max_subsections = None              # Passed as an attribute to the SUBTOPIC_REPORT prompt
        self.max_iterations = None               # Passed as an attribute to the search_queries_prompt
        self.max_subtopics = None                # Passed as an attribute to the subtopics_prompt
        self.report_out_dir = None               # Location where Publisher places output reports
        self.local_store_dir = None              # Location of the local data store
        self.cache_dir = None                    # Location of the Vector DB
       
        # Set LLM_ANALYST_CONFIG environment variable to override and default configurations
        config_file_path = os.getenv("LLM_ANALYST_CONFIG", None)
        config_json = self._get_config_file(config_file_path=config_file_path)
        self.set_values_for_config(config_json)

    def __str__(self):
        attributes = []
        for key, value in self.__dict__.items():
            attributes.append(f"{key}={value}")
        return "\n".join(attributes)

    def get_prompt_json_path(self):
        """Get the user defined path to prompts json 'prompt_json_path'
        or return the defaults if a configuration is not provided
        """
        prompt_json_path = getattr(self, "prompt_json_path", None)
        if not prompt_json_path:
            package_nm = "llm_analyst.resources"
            module_spec = importlib.util.find_spec(package_nm)
            package_path = os.path.dirname(module_spec.origin)
            prompt_json_path = os.path.join(package_path, "prompts.json")
        return prompt_json_path

    # @trace_log
    def _get_config_file(self, config_file_path=None):
        """Use the default config file override if environment variables are set.
        """
        config_json = None
        if not config_file_path:
            config_file_path = os.path.join(get_resource_path(), "llm_analyst.config")

        try:
            with open(config_file_path, "r", encoding="utf-8") as json_file:
                config_json = json.load(json_file)
        except Exception:
            error_msg = f"IN Config._get_config_file - Config file json failed to load. [{config_file_path}]"
            logging.error(error_msg)
            raise LLMAnalystsException(error_msg)

        return config_json

    def set_values_for_config(self, config_json):
        """Set the config properties in a dictionary.
        Evaluate the the property name to determine the correct data type.
        """
        
        for key, value in config_json.items():
            if keyword.iskeyword(key):
                key += "_"

            if isinstance(value, dict):
                default_val = value.get("default_val", None)
                env_var = value.get("env_var", None)
                env_val = os.getenv(env_var) if env_var else None
                value = env_val if env_val else default_val

            if key.endswith("_dir") and value:
                # If this is a directory key check if special charter ~ is used
                # and if so expand the ~ to the full home dir path
                if value[0] == "~":
                    value = os.path.expanduser(value)

            if key == "internet_search" and value is not None:
                value = self._get_search_method(value)

            if key == "embedding_provider" and value is not None:
                value = self._get_embeddings_provider(value)

            if key == "llm_provider" and value is not None:
                value = self._get_llm_model(value)

            setattr(self, key, value)


    def _get_search_method(self, search_method: str):
        """Convert the search_method from a string to a callable function.
        """
        module_name = "llm_analyst.search_methods.internet_search"
        try:
            module = importlib.import_module(module_name)
            internet_search_method = getattr(module, search_method)
        except (ImportError, AttributeError) as e:
            error_msg = f"IN Config._get_search_method - Search Method not found. [{search_method}]"
            logging.error(error_msg)
            raise LLMAnalystsException(error_msg) from e

        return internet_search_method

    def _get_llm_model(self, llm_model_module: str):
        """Convert the llm_model_module from a string to a Chat Model Object.
        NOTE: Currently relying on a Naming Convention for Model Object
              UPPERCASE_MODEL_NM+"_Model"
              
        """
        chat_model = None
        module_name = f"llm_analyst.chat_models.{llm_model_module}"
        try:
            module = importlib.import_module(module_name)
            chat_model_nm = llm_model_module.upper() + "_Model"
            chat_model = getattr(module, chat_model_nm)
        except (ImportError, AttributeError) as e:
            error_msg = (
                f"IN Config._get_llm_model - Chat Model not found. [{llm_model_module}]"
            )
            logging.error(error_msg)
            raise LLMAnalystsException(error_msg) from e

        return chat_model

    def _get_embeddings_provider(self, embeddings_provider_nm):
        """Map embeddings_provider_nm to a Langchain Embeddings Class"""
        embeddings = None
        match embeddings_provider_nm:
            case "ollama":
                from langchain_community.embeddings.ollama import OllamaEmbeddings

                embeddings = OllamaEmbeddings(model="llama3")
            case "openai":
                from langchain_openai import OpenAIEmbeddings

                embeddings = OpenAIEmbeddings()
            case "huggingface":
                from langchain_huggingface import HuggingFaceEmbeddings

                embeddings = HuggingFaceEmbeddings()
            case _:
                error_msg = f"IN Config._get_embeddings_provider - Embedding provider not found. [{embeddings_provider_nm}]"
                logging.error(error_msg)
                raise LLMAnalystsException(error_msg)

        return embeddings
