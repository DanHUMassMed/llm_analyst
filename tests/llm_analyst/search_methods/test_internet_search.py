""" Test Cases for internet_search """

import inspect
import os

import pytest

from llm_analyst.core.config import Config
from llm_analyst.search_methods.internet_search import (bing_search,
                                                        ddg_search,
                                                        google_search,
                                                        serp_api_search,
                                                        serper_search,
                                                        tavily_search)
from tests.utils_for_pytest import dump_test_results

MAX_SEARCH_RESULTS = 4


def setup_search_config(search_method_nm, search_method):
    os.environ.pop("LLM_ANALYST_CONFIG", None)
    config_json = {"internet_search": search_method_nm}

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

    actual_result = config.internet_search(query, MAX_SEARCH_RESULTS)
    assert 0 < len(actual_result) <= MAX_SEARCH_RESULTS
    dump_test_results(function_name, actual_result)


def test_serper_search():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    config = setup_search_config("serper_search", serper_search)

    actual_result = config.internet_search(query, MAX_SEARCH_RESULTS)
    assert 0 < len(actual_result) <= MAX_SEARCH_RESULTS
    dump_test_results(function_name, actual_result)


def test_serp_api_search():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    config = setup_search_config("serp_api_search", serp_api_search)

    actual_result = config.internet_search(query, MAX_SEARCH_RESULTS)
    assert 0 < len(actual_result) <= MAX_SEARCH_RESULTS
    dump_test_results(function_name, actual_result)


def test_ddg_search():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    config = setup_search_config("ddg_search", ddg_search)

    actual_result = config.internet_search(query, MAX_SEARCH_RESULTS)
    assert 0 < len(actual_result) <= MAX_SEARCH_RESULTS
    dump_test_results(function_name, actual_result)


def test_google_search():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    config = setup_search_config("google_search", google_search)

    actual_result = config.internet_search(query, MAX_SEARCH_RESULTS)
    assert 0 < len(actual_result) <= MAX_SEARCH_RESULTS
    dump_test_results(function_name, actual_result)


def test_bing_search():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    config = setup_search_config("bing_search", bing_search)

    actual_result = config.internet_search(query, MAX_SEARCH_RESULTS)
    assert 0 < len(actual_result) <= MAX_SEARCH_RESULTS
    dump_test_results(function_name, actual_result)

if __name__ == "__main__":
    pytest.main([__file__])
