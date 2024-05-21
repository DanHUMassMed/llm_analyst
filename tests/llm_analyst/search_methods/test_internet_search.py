import os
import pytest
import inspect
from tests.utils_for_pytest import dump_api_call
from llm_analyst.search_methods.internet_search import tavily_search, serper_search, serp_api_search, ddgs_search
from llm_analyst.core.config import Config


def setup_search_config(search_method_nm, search_method):
    os.environ.pop('LLM_ANALYST_CONFIG', None)
    config_json = {"internet_search" :{"default_val":search_method_nm}}

    config = Config()
    config._set_values_for_config(config_json)

    expected_result = search_method
    actual_result = config.internet_search
    assert actual_result == expected_result

    return config
    
    

def test_tavily_search():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    config = setup_search_config("tavily_search", tavily_search)

    actual_result = config.internet_search(query)
    assert len(actual_result) > 0
    dump_api_call(function_name, actual_result)
    
def test_serper_search():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    config = setup_search_config("serper_search", serper_search)

    actual_result = config.internet_search(query)
    assert len(actual_result) > 0
    dump_api_call(function_name, actual_result)

def test_serp_api_search():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    config = setup_search_config("serp_api_search", serp_api_search)

    actual_result = config.internet_search(query)
    assert len(actual_result) > 0
    dump_api_call(function_name, actual_result)

def test_ddgs_search():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    config = setup_search_config("ddgs_search", ddgs_search)

    actual_result = config.internet_search(query)
    assert len(actual_result) > 0
    dump_api_call(function_name, actual_result)

if __name__ == "__main__":
    pytest.main([__file__])

