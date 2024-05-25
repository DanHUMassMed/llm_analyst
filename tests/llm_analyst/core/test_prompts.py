""" Test Cases for Prompts """
import os
import inspect
import pytest
from tests.utils_for_pytest import dump_api_call, get_resource_file_path
from datetime import datetime, timezone
from langchain_openai import OpenAIEmbeddings
from llm_analyst.chat_models.openai import OPENAI_Model
from llm_analyst.core.prompts import Prompts
from llm_analyst.core.exceptions import LLMAnalystsException
from tests.utils_for_pytest import dump_api_call, get_resource_file_path


def test_load_prompts():
    prompts = Prompts()
    expected_result = 9
    actual_result = len(prompts._prompts)
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_prompt_no_params():
    prompts = Prompts()
    expected_result = "This task involves researching"
    actual_result = prompts.get_prompt("choose_agent_prompt")
    # Assertion: Check that the function returns the expected result
    assert actual_result.startswith(expected_result)

def test_prompt_exception():
    prompts = Prompts()
    expected_result = "ERROR: The PROMPT: [search_queries_prompt] expects the following VARIABLES: [max_iterations, task, datetime_now]"

    actual_result = ""
    with pytest.raises(LLMAnalystsException) as exc_info:
        prompts.get_prompt("search_queries_prompt",max_iterations=2)
    actual_result = str(exc_info.value)

    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_prompt_with_params():
    function_name = inspect.currentframe().f_code.co_name
    prompts = Prompts()
    expected_result = "Write 2 Google search queries to search online"
    max_iterations=2
    task="What happened in the latest burning man floods?"
    datetime_now=datetime.now().strftime('%B %d, %Y')
    actual_result = prompts.get_prompt("search_queries_prompt",
                                       max_iterations=max_iterations,
                                       task=task,
                                       datetime_now=datetime_now)

    # Assertion: Check that the function returns the expected result
    assert actual_result.startswith(expected_result)
    dump_api_call(function_name, actual_result)

def test_report_prompt():
    function_name = inspect.currentframe().f_code.co_name
    prompts = Prompts()
    expected_result = "Information: '''context data....'''"
    report_prompt_nm = "research_report_prompt"
    query = "What happened in the latest burning man floods?"
    context="context data...."
    total_words = 1000
    report_format = "APA"
    datetime_now=datetime.now().strftime('%B %d, %Y')
    actual_result = prompts.get_prompt(report_prompt_nm,
                                             context=context,
                                             question=query,
                                             total_words=total_words,
                                             report_format=report_format,
                                             datetime_now = datetime_now)
    

    # Assertion: Check that the function returns the expected result
    assert actual_result.startswith(expected_result)
    dump_api_call(function_name, actual_result)

if __name__ == "__main__":
    pytest.main([__file__])
