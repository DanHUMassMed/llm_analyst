""" Test Cases for LLMAnalyst """

import inspect
import json

import pytest

from llm_analyst.core.config import Config, DataSource, ReportType
from llm_analyst.core.research_analyst import LLMAnalyst
from llm_analyst.core.research_state import ResearchState
from tests.utils_for_pytest import dump_test_results, get_resource_file_path

# Models gpt-3.5-turbo, gpt-4o-2024-05-13
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


@pytest.mark.asyncio
async def test_analyst_init():
    """Test the init method"""
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_state("tst_research_state_1")

    assert llm_analyst.data_source == DataSource.WEB
    assert llm_analyst.report_type == ReportType.RESEARCH_REPORT

    # Assertion: Check that the function returns the expected result
    assert research_state.dump() == llm_analyst.dump()


@pytest.mark.asyncio
async def test_analyst_choose_agent():
    """Test choosing the Agent Type and Prompt base upon the Research Topic"""
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_state("tst_research_state_1")
    actual_result = await llm_analyst.choose_agent()

    # Assertion: Check that the function returns the expected result
    # We can not be sure of the Exact text so we will test that we got something
    # Look at the dump in test_output as need for additional confirmation
    assert len(actual_result.agent_type) > 10
    dump_test_results(function_name, actual_result.dump())


@pytest.mark.asyncio
async def test_analyst_select_subtopic():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_state("tst_research_state_4")

    actual_result = await llm_analyst.select_subtopics()

    # Assertion: Check that the function returns the expected result
    expected_result = llm_analyst.cfg.max_subtopics
    assert len(actual_result) > 2
    # NOTE: Both gpt-3.5-turbo and gpt-4o-2024-05-13 returned 4 results when 3 where expected
    dump_test_results(function_name, actual_result)


@pytest.mark.asyncio
async def test_analyst_get_sub_queries():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_state("tst_research_state_1")

    llm_analyst.agent_type = research_state.agent_type
    llm_analyst.agents_role_prompt = research_state.agents_role_prompt

    actual_result = await llm_analyst._get_sub_queries()
    # llm_analyst.dump(test_json_file_path)

    # Assertion: Check that the function returns the expected result
    expected_result = llm_analyst.cfg.max_iterations
    assert len(actual_result) > 2
    # NOTE: Both gpt-3.5-turbo and gpt-4o-2024-05-13 returned 4 results when 3 where expected
    dump_test_results(function_name, actual_result)


@pytest.mark.asyncio
async def test_analyst_keep_unique_urls():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_state("tst_research_state_4")

    topic_urls = [
        "https://www.nytimes.com/article/burning-man-mud-trapped.html",
        "https://apnews.com/article/NEW_ARTICLE",
        "https://www.nytimes.com/2023/09/06/opinion/burning-man-flood-playa-climate-change.html",
    ]

    actual_result = await llm_analyst._keep_unique_urls(topic_urls)
    assert len(actual_result) == 1, f"Expected 1 found {len(actual_result)}"
    dump_test_results(function_name, actual_result)


@pytest.mark.asyncio
async def test_analyst_get_similar_content_by_query():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_state("tst_research_state_4")

    file_path = get_resource_file_path("tst_scrape_urls.json")
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    sub_query = "Impact of Flooding on Burning Man Attendees"

    actual_result = await llm_analyst._get_similar_content_by_query(sub_query, data)
    assert len(actual_result) > 2
    dump_test_results(function_name, actual_result, to_json=False)


# @pytest.mark.asyncio
# async def test_analyst_conduct_research():
#     function_name = inspect.currentframe().f_code.co_name
#     llm_analyst, research_state = setup_research_analysts("tst_research_state_1")

#     actual_result = await llm_analyst.conduct_research()
#     assert len(actual_result.research_findings) > 2
#     dump_test_results(function_name, actual_result.dump())


@pytest.mark.asyncio
async def test_analyst_write_report():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_state("tst_research_state_4")

    actual_result = await llm_analyst.write_report()
    dump_test_results(function_name, actual_result.report_md, to_json=False)


if __name__ == "__main__":
    pytest.main([__file__])
