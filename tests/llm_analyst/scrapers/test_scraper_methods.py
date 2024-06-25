""" Test Cases for scraper_methods """

import inspect

import pytest

from llm_analyst.core.config import Config
from llm_analyst.core.research_analyst import LLMAnalyst
from llm_analyst.core.research_state import ResearchState
from llm_analyst.scrapers.scraper_methods import scrape_urls
from tests.utils_for_pytest import dump_test_results, get_resource_file_path

CONFIG_PARAMS = {
    "internet_search": "ddg_search",
    "llm_provider": "openai",
    "llm_model": "gpt-3.5-turbo",
    "max_iterations": 3,
    "llm_temperature": 0,
    "max_subtopics": 3,
}


def setup_research_state(function_name):
    test_json_file_path = get_resource_file_path(f"{function_name}.json")
    research_state = ResearchState.load(test_json_file_path)

    config = Config()
    config.set_values_for_config(CONFIG_PARAMS)

    llm_analyst = LLMAnalyst(config=config, **research_state.dump())
    return llm_analyst, research_state


def test_scraper_scrape_urls():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_state("tst_research_state_4")

    actual_result = scrape_urls(list(research_state.visited_urls)[:3])

    # Just check that you do get results
    assert len(actual_result) > 0
    dump_test_results(function_name, actual_result)

if __name__ == "__main__":
    pytest.main([__file__])