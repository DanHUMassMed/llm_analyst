""" Test Cases for Config """
import os
import json
import inspect
from tests.utils_for_pytest import dump_api_call, get_resource_file_path
import pytest

from llm_analyst.core.research_analyst import LLMAnalyst
from llm_analyst.core.config import Config

QUERY    = "What happened in the latest burning man floods?"
AGENT_NM = "📰 News Agent"
AGENT_ROLE_PROMPT = "You are a well-informed AI news analyst assistant. Your primary goal is to provide comprehensive, accurate, unbiased, and well-structured news reports based on the latest events and developments."
TOPIC_URLS = [
        "https://www.wgem.com/2023/09/04/tens-thousands-still-stranded-by-burning-man-flooding-nevada-desert/",
        "https://abc11.com/burning-man-death-shelter-in-place-flooding-rain/13731593/",
        "https://edition.cnn.com/2023/09/03/us/burning-man-storms-shelter-sunday/index.html?obInternalId=71118",
       ]
SUB_QUERY = "latest news on Burning Man floods May 2024"

@pytest.mark.asyncio
async def test_choose_agent():
    function_name = inspect.currentframe().f_code.co_name
    config = Config()
    
    llm_analyst = LLMAnalyst(QUERY)
    
    expected_result = AGENT_NM
    result_dict = await llm_analyst.choose_agent()
    actual_result = result_dict['agent_type']
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result
    dump_api_call(function_name, result_dict)

# @pytest.mark.asyncio
# async def test_get_sub_queries():
#     function_name = inspect.currentframe().f_code.co_name
#     llm_analyst = LLMAnalyst(QUERY)
#     llm_analyst.agent = AGENT_NM
#     llm_analyst.role = AGENT_ROLE_PROMPT
#     expected_result = llm_analyst.cfg.max_iterations
    
#     actual_result = await llm_analyst._get_sub_queries()
    
#     # Assertion: Check that the function returns the expected result
#     assert len(actual_result) == expected_result
#     dump_api_call(function_name, actual_result)

# @pytest.mark.asyncio
# def test_scrape_urls():
#     function_name = inspect.currentframe().f_code.co_name
#     llm_analyst = LLMAnalyst(QUERY)

#     actual_result = llm_analyst._scrape_urls(TOPIC_URLS)
#     # Just check that you doe get results
#     assert len(actual_result) >0
#     dump_api_call(function_name, actual_result)

# @pytest.mark.asyncio
# async def test_keep_unique_urls():
#     function_name = inspect.currentframe().f_code.co_name
#     llm_analyst = LLMAnalyst(QUERY)
#     llm_analyst.visited_urls.add(TOPIC_URLS[0])

#     actual_result = await llm_analyst._keep_unique_urls(TOPIC_URLS)
#     assert len(actual_result) == 2,f"Expected 2 found {len(actual_result)}"
#     dump_api_call(function_name, actual_result)

# @pytest.mark.asyncio
# async def test_get_similar_content_by_query():
#     function_name = inspect.currentframe().f_code.co_name
#     llm_analyst = LLMAnalyst(QUERY)
#     file_path = get_resource_file_path("example_scraped_sites.json")
#     with open(file_path, 'r') as file:
#         data = json.load(file)

#     actual_result = await llm_analyst._get_similar_content_by_query(SUB_QUERY, data)
#     dump_api_call(function_name, actual_result,to_json=False)

# @pytest.mark.asyncio
# async def test_conduct_research():
#     function_name = inspect.currentframe().f_code.co_name
#     llm_analyst = LLMAnalyst(QUERY)
#     await llm_analyst.conduct_research()
#     actual_result = llm_analyst.context
#     dump_api_call(function_name, actual_result,to_json=False)

# @pytest.mark.asyncio
# async def test_write_report():
#     function_name = inspect.currentframe().f_code.co_name
#     llm_analyst = LLMAnalyst(QUERY)
#     file_path = get_resource_file_path("example_scraped_sites.json")
#     with open(file_path, 'r') as file:
#         data = json.load(file)
#     llm_analyst.context = data
#     sub_query = "latest news on Burning Man floods May 2024"
#     actual_result = await llm_analyst.write_report()
#     dump_api_call(function_name, actual_result,to_json=False)

if __name__ == "__main__":
    pytest.main([__file__])
