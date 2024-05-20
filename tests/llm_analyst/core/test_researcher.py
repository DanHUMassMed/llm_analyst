""" Test Cases for Config """
import os
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


if __name__ == "__main__":
    pytest.main([__file__])
