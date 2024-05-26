""" Test Cases for GROQ_Model """
import os
import json
import inspect
from tests.utils_for_pytest import dump_test_results, get_resource_file_path
import pytest

from llm_analyst.chat_models.groq import GROQ_Model

AGENT_ROLE_PROMPT = "You are a well-informed AI news analyst assistant. Your primary goal is to provide comprehensive, accurate, unbiased, and well-structured news reports based on the latest events and developments."

@pytest.mark.asyncio
async def test_chat_response_1():
    function_name = inspect.currentframe().f_code.co_name
    prompt = "Write 5 Google search queries to search online that form an objective opinion from the following task: What happened in the latest burning man floods?\nUse the current date if needed: May 21, 2024.\nAlso include in the queries specified task details such as locations, names, etc.\nYou must respond with a list of strings in the following format: [\"query 1\", \"query 2\", \"query 3\"]. The response should contain ONLY the list"
    model="llama3-70b-8192"
    temperature=0
    max_tokens=4000
    groq_model = GROQ_Model(model=model,temperature=temperature,max_tokens=max_tokens)
    
    messages=[
        {"role": "system", "content": AGENT_ROLE_PROMPT},
        {"role": "user",   "content": prompt}]
    
    actual_result = await groq_model.get_chat_response(messages)
    
    # Assertion: Check that the function returns the expected result
    #assert actual_result == expected_result
    dump_test_results(function_name, actual_result,to_json=False)
