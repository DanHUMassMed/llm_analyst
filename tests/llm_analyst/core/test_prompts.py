""" Test Cases for Prompts """
import os
import inspect
import pytest
from tests.utils_for_pytest import dump_api_call, get_resource_file_path
from datetime import datetime, timezone
from langchain_openai import OpenAIEmbeddings
from llm_analyst.chat_models.openai import OPENAI_Model
from llm_analyst.core.prompts import Prompts
from llm_analyst.core.config import Config
from llm_analyst.core.exceptions import LLMAnalystsException
from tests.utils_for_pytest import dump_api_call, get_resource_file_path


def test_load_prompts():
    """ Test loading the default prompts"""
    prompts = Prompts()
    expected_result = 9
    actual_result = len(prompts._prompts)
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result
    
def test_load_prompts_from_env():
    """ Test prompts loading from an environment configuration"""
    expected_result = "Write {max_iterations} Google search queries"
    prompt_json_path = get_resource_file_path("tst_prompts.json")
    config_params = {"prompt_json_path" :prompt_json_path}
    
    config = Config()
    config._set_values_for_config(config_params)
    
    actual_results = Prompts(config).get_prompt('this_is_a_test_prompt')
    assert actual_results.startswith(expected_result)
    

def test_prompt_no_params():
    """Tes a prompt that has no parameters"""
    prompts = Prompts()
    expected_result = "This task involves researching"
    actual_result = prompts.get_prompt("choose_agent_prompt")
    # Assertion: Check that the function returns the expected result
    assert actual_result.startswith(expected_result)

def test_prompt_exception():
    """Test the exception from calling a prompt with the wrong parameters"""
    prompts = Prompts()
    expected_result = "ERROR: The PROMPT: [search_queries_prompt] expects the following VARIABLES: [max_iterations, task, datetime_now]"

    actual_result = ""
    with pytest.raises(LLMAnalystsException) as exc_info:
        prompts.get_prompt("search_queries_prompt", max_iterations=2)
    actual_result = str(exc_info.value)

    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_prompt_with_params():
    """Test a prompt and pass parameters"""
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
    """Test the creatation of the report prompt"""
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
