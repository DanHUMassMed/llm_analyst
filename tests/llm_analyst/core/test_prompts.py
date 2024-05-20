""" Test Cases for Prompts """
import os
import pytest
from datetime import datetime, timezone
from langchain_openai import OpenAIEmbeddings
from llm_analyst.chat_models.openai import OPENAI_Model
from llm_analyst.core.prompts import Prompts
from llm_analyst.core.exceptions import LLMAnalystsException


def test_load_prompts():
    prompts = Prompts()
    expected_result = 9
    actual_result = len(prompts._prompts)
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_prompt_no_params():
    prompts = Prompts()
    expected_result = "This task involves researching"
    actual_result = prompts.get_prompt("auto_agent_instructions")
    # Assertion: Check that the function returns the expected result
    assert actual_result.startswith(expected_result)

def test_prompt_exception():
    prompts = Prompts()
    expected_result = "The PROMPT: [search_queries_prompt] expects the following VARIABLES: [max_iterations, task, datetime_now]"
    actual_result = ""
    with pytest.raises(LLMAnalystsException) as exc_info:
        prompts.get_prompt("search_queries_prompt",max_iterations=2)
    actual_result = str(exc_info.value)

    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_prompt_with_params():
    prompts = Prompts()
    expected_result = "Write 2 Google search queries to search online"
    max_iterations=2
    task="Research this task"
    datetime_now=datetime.now().strftime('%B %d, %Y')
    actual_result = prompts.get_prompt("search_queries_prompt",
                                       max_iterations=max_iterations,
                                       task=task,
                                       datetime_now=datetime_now)

    # Assertion: Check that the function returns the expected result
    assert actual_result.startswith(expected_result)

if __name__ == "__main__":
    pytest.main([__file__])
