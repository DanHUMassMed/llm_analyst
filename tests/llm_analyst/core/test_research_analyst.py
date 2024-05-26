""" Test Cases for Config """
import os
import json
import inspect
from tests.utils_for_pytest import dump_api_call, get_resource_file_path
import pytest

from llm_analyst.core.research_analyst import LLMAnalyst
from llm_analyst.core.research_state import ResearchState
from llm_analyst.core.config import Config

CONFIG_PARAMS = {
    "internet_search" :"ddg_search",
    "max_iterations"  :3,
    "llm_temperature" :0
}

def setup_research_analysts(function_name):
    test_json_file_path = get_resource_file_path(f"{function_name}.json")
    research_state = ResearchState.load(test_json_file_path)
    
    config = Config()
    config._set_values_for_config(CONFIG_PARAMS)
    
    llm_analyst = LLMAnalyst(research_state.active_research_topic, config = config)
    return llm_analyst, research_state

    
@pytest.mark.asyncio
async def test_choose_agent():
    """Test choosing the Agent Tyep and Prompt base upon the Reseach Topic
    """
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_analysts("tst_research_state_1")
    actual_result = await llm_analyst.choose_agent()
    
    # actual_result.dump(test_json_file_path)
    # Assertion: Check that the function returns the expected result
    assert actual_result.agent_type == research_state.agent_type
    dump_api_call(function_name, actual_result.dump())
    

@pytest.mark.asyncio
async def test_get_sub_queries():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_analysts("tst_research_state_1")
    
    llm_analyst.agent_type = research_state.agent_type
    llm_analyst.agents_role_prompt = research_state.agents_role_prompt
    
    expected_result = llm_analyst.cfg.max_iterations
    
    actual_result = await llm_analyst._get_sub_queries()
    # llm_analyst.dump(test_json_file_path)
    
    # Assertion: Check that the function returns the expected result
    assert len(actual_result) == expected_result
    dump_api_call(function_name, actual_result)

@pytest.mark.asyncio
def test_scrape_urls():
    function_name = inspect.currentframe().f_code.co_name
    test_json_file_path = get_resource_file_path(f"{function_name}.json")
    research_state = ResearchState.load(test_json_file_path)

    config = Config()
    config._set_values_for_config(CONFIG_PARAMS)
    
    llm_analyst = LLMAnalyst(research_state.active_research_topic, config = config)


    actual_result = llm_analyst._scrape_urls(TOPIC_URLS)
    # Just check that you doe get results
    assert len(actual_result) >0
    dump_api_call(function_name, actual_result)

@pytest.mark.asyncio
async def test_keep_unique_urls():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst = LLMAnalyst(QUERY)
    llm_analyst.visited_urls.add(TOPIC_URLS[0])

    actual_result = await llm_analyst._keep_unique_urls(TOPIC_URLS)
    assert len(actual_result) == 2,f"Expected 2 found {len(actual_result)}"
    dump_api_call(function_name, actual_result)

@pytest.mark.asyncio
async def test_get_similar_content_by_query():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst = LLMAnalyst(QUERY)
    file_path = get_resource_file_path("example_scraped_sites.json")
    with open(file_path, 'r') as file:
        data = json.load(file)

    actual_result = await llm_analyst._get_similar_content_by_query(SUB_QUERY, data)
    assert len(actual_result) > 2
    dump_api_call(function_name, actual_result,to_json=False)

@pytest.mark.asyncio
async def test_conduct_research():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst = LLMAnalyst(QUERY)
    await llm_analyst.conduct_research()
    actual_result = llm_analyst.research_findings
    assert len(actual_result) > 2
    dump_api_call(function_name, actual_result,to_json=False)

@pytest.mark.asyncio
async def test_write_report():
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst = LLMAnalyst(QUERY)
    llm_analyst.agent_type = AGENT_NM
    llm_analyst.agents_role_prompt = AGENT_ROLE_PROMPT
    
    
    # llm_analyst.research_findings = data
    # sub_query = "latest news on Burning Man floods May 2024"
    actual_result = await llm_analyst.write_report()
    # dump_api_call(function_name, actual_result.report_md,to_json=False)

if __name__ == "__main__":
    pytest.main([__file__])
