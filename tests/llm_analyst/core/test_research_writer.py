import os
import json
import inspect
import logging
from tests.utils_for_pytest import dump_test_results, get_resource_file_path
import pytest

from llm_analyst.core.research_publisher import LLMPublisher
logger = logging.getLogger(__name__)
QUERY    = "What happened in the latest burning man floods?"

@pytest.mark.asyncio
async def test_write_to_pdf():
    function_name = inspect.currentframe().f_code.co_name
    llm_writer = LLMWriter(QUERY)
    file_path = get_resource_file_path("tst_report_markdown.md")
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
    llm_writer.report_md = data
    
    output_file = await llm_writer.write_to_pdf()
    logger.debug("output_file %s", output_file)
    # # Assertion: Check that the function returns the expected result
    # assert actual_result == expected_result
    # dump_api_call(function_name, dump_result)
