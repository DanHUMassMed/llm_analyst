""" Test Cases for Config """

import os
import pytest
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings.ollama import OllamaEmbeddings

from tests.utils_for_pytest import get_resource_file_path
from llm_analyst.chat_models.openai import OPENAI_Model
from llm_analyst.core.config import Config


def test_config_use_local_config():
    """Test finding the config file from an environment variable"""
    file_path = get_resource_file_path("tst_llm_analyst.config")
    os.environ["LLM_ANALYST_CONFIG"] = file_path
    config = Config()
    os.environ.pop("LLM_ANALYST_CONFIG", None)
    expected_result = OllamaEmbeddings(model="llama3")
    actual_result = config.embedding_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result


def test_config_embedding_provider_lookup():
    """Test if the embedding provider lookup sets the value using defualt config"""
    os.environ.pop("LLM_ANALYST_CONFIG", None)
    config = Config()
    expected_result = OpenAIEmbeddings()
    actual_result = config.embedding_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result


def test_config_llm_provider_lookup():
    """Test if the LLM Model gets set on config"""
    config = Config()
    expected_result = OPENAI_Model
    actual_result = config.llm_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result


def test_config_get_prompt_json_path():
    """Test if an environment variable can be used for the prompt json path"""
    prompt_json_path = get_resource_file_path("tst_prompts.json")
    config_params = {"prompt_json_path": prompt_json_path}

    config = Config()
    config._set_values_for_config(config_params)

    actual_results = config.get_prompt_json_path()
    assert actual_results == prompt_json_path


if __name__ == "__main__":
    pytest.main([__file__])
