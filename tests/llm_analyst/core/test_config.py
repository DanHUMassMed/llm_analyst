""" Test Cases for Config """
import os
import pytest

from langchain_openai import OpenAIEmbeddings
from llm_analyst.chat_models.openai import OPENAI_Model
from llm_analyst.core.config import Config


def test_use_local_config():
    # Will find the config from an environment variable
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, 'tests/llm_analyst/core/llm_analyst_test.config')
    print(f"LLM_ANALYST_CONFIG path={file_path}")
    os.environ['LLM_ANALYST_CONFIG'] = file_path
    config = Config()
    os.environ.pop('LLM_ANALYST_CONFIG', None)
    expected_result = "TEST_RESULT"
    actual_result = config.embedding_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_embedding_provider_lookup():
    os.environ.pop('LLM_ANALYST_CONFIG', None)
    config = Config()
    expected_result = OpenAIEmbeddings()
    actual_result = config.embedding_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_llm_provider_lookup():
    config = Config()
    expected_result = OPENAI_Model
    actual_result = config.llm_provider
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

if __name__ == "__main__":
    pytest.main([__file__])
