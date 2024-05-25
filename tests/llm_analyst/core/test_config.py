""" Test Cases for Config """
import os
import pytest
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings.ollama import OllamaEmbeddings

from tests.utils_for_pytest import  get_resource_file_path
from llm_analyst.chat_models.openai import OPENAI_Model
from llm_analyst.core.config import Config


def test_use_local_config():
    """Test finding the config file from an environment variable
    """
    file_path = get_resource_file_path("llm_analyst_test.config")
    os.environ['LLM_ANALYST_CONFIG'] = file_path
    config = Config()
    os.environ.pop('LLM_ANALYST_CONFIG', None)
    expected_result = OllamaEmbeddings(model="llama3")
    actual_result = config.embedding_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_embedding_provider_lookup():
    """Test if the embedding provider lookup sets the value using defualt config
    """
    os.environ.pop('LLM_ANALYST_CONFIG', None)
    config = Config()
    expected_result = OpenAIEmbeddings()
    actual_result = config.embedding_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_llm_provider_lookup():
    """Test if the LLM Model get set on config"""
    config = Config()
    expected_result = OPENAI_Model
    actual_result = config.llm_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

if __name__ == "__main__":
    pytest.main([__file__])
