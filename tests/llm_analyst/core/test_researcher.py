""" Test Cases for Config """
import os
import json
import inspect
from tests.utils_for_pytest import dump_api_call
import pytest

from llm_analyst.core.researcher import LLMAnalyst

@pytest.mark.asyncio
async def test_choose_agent():
    # Will find the config from an environment variable
    query = "What happened in the latest burning man floods?"
    llm_analyst = LLMAnalyst(query)
    
    expected_result = "📰 News Agent"
    actual_result, _ = await llm_analyst._choose_agent()
    # Assertion: Check that the function returns the expected result
    
    assert actual_result == expected_result

@pytest.mark.asyncio
async def test_get_sub_queries():
    function_name = inspect.currentframe().f_code.co_name
    # Will find the config from an environment variable
    query = "What happened in the latest burning man floods?"
    llm_analyst = LLMAnalyst(query)
    llm_analyst.agent = "📰 News Agent"
    llm_analyst.role = "You are a well-informed AI news analyst assistant. Your primary goal is to provide comprehensive, accurate, unbiased, and well-structured news reports based on the latest events and developments."
    expected_result = llm_analyst.cfg.max_iterations
    
    actual_result = await llm_analyst._get_sub_queries()
    
    # Assertion: Check that the function returns the expected result
    assert len(actual_result) == expected_result
    dump_api_call(function_name, actual_result)

def test_scrape_urls():
    function_name = inspect.currentframe().f_code.co_name
    urls = [
        "https://www.wgem.com/2023/09/04/tens-thousands-still-stranded-by-burning-man-flooding-nevada-desert/",
        "https://abc11.com/burning-man-death-shelter-in-place-flooding-rain/13731593/",
        "https://edition.cnn.com/2023/09/03/us/burning-man-storms-shelter-sunday/index.html?obInternalId=71118",
    ]
    # Will find the config from an environment variable
    query = "What happened in the latest burning man floods?"
    llm_analyst = LLMAnalyst(query)

    actual_result = llm_analyst._scrape_urls(urls)
    assert len(actual_result) >0
    dump_api_call(function_name, actual_result)

@pytest.mark.asyncio
async def test_keep_unique_urls():
    function_name = inspect.currentframe().f_code.co_name
    urls = [
        "https://www.wgem.com/2023/09/04/tens-thousands-still-stranded-by-burning-man-flooding-nevada-desert/",
        "https://abc11.com/burning-man-death-shelter-in-place-flooding-rain/13731593/",
        "https://edition.cnn.com/2023/09/03/us/burning-man-storms-shelter-sunday/index.html?obInternalId=71118",
    ]

    query = "What happened in the latest burning man floods?"
    llm_analyst = LLMAnalyst(query)
    llm_analyst.visited_urls.add(urls[0])

    actual_result = await llm_analyst._keep_unique_urls(urls)
    assert len(actual_result) == 2,f"Expected 2 found {len(actual_result)}"
    dump_api_call(function_name, actual_result)

@pytest.mark.asyncio
async def test_get_similar_content_by_query():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    llm_analyst = LLMAnalyst(query)

    file_path = os.path.join(os.getcwd(), 'tests/llm_analyst/core/example_scraped_sites.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    sub_query = "latest news on Burning Man floods May 2024"
    actual_result = await llm_analyst._get_similar_content_by_query(sub_query, data)
    dump_api_call(function_name, actual_result,to_json=False)

@pytest.mark.asyncio
async def test_conduct_research():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    llm_analyst = LLMAnalyst(query)
    await llm_analyst.conduct_research()
    actual_result = llm_analyst.context
    dump_api_call(function_name, actual_result,to_json=False)

@pytest.mark.asyncio
async def test_write_report():
    function_name = inspect.currentframe().f_code.co_name
    query = "What happened in the latest burning man floods?"
    llm_analyst = LLMAnalyst(query)

    file_path = os.path.join(os.getcwd(), 'tests/llm_analyst/core/example_scraped_sites.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    sub_query = "latest news on Burning Man floods May 2024"
    actual_result = await llm_analyst._get_similar_content_by_query(sub_query, data)
    dump_api_call(function_name, actual_result,to_json=False)

if __name__ == "__main__":
    pytest.main([__file__])
