import inspect
import json
import inspect
import logging
from tests.utils_for_pytest import dump_test_results, get_resource_file_path, OUTPUT_PATH
import pytest

from llm_analyst.core.research_publisher import LLMPublisher
from llm_analyst.core.research_state import ResearchState
from llm_analyst.core.config import Config

logger = logging.getLogger(__name__)

CONFIG_PARAMS = {
    "internet_search" :"ddg_search",
    "max_iterations"  :3,
    "llm_temperature" :0,
    "max_subtopics"   :3,
    "report_out_dir"  :OUTPUT_PATH
}

def setup_research_state(function_name):
    test_json_file_path = get_resource_file_path(f"{function_name}.json")
    research_state = ResearchState.load(test_json_file_path)
    
    config = Config()
    config._set_values_for_config(CONFIG_PARAMS)
    
    llm_publisher = LLMPublisher.init(research_state, config = config)
    return llm_publisher, research_state


@pytest.mark.asyncio
async def test_publisher_init():
    """Test the init method
    """
    function_name = inspect.currentframe().f_code.co_name
    llm_analyst, research_state = setup_research_state("tst_research_state_5")
    llm_publisher_from_research_state = LLMPublisher.init(research_state)
        
    # actual_result.dump(test_json_file_path)
    # Assertion: Check that the function returns the expected result
    assert research_state.dump() == llm_publisher_from_research_state.dump()
    
@pytest.mark.asyncio
async def test_publish_to_md_file():
    function_name = inspect.currentframe().f_code.co_name
    llm_publisher, research_state = setup_research_state("tst_research_state_5")
    report_intro = await llm_publisher.publish_to_md_file()
    dump_test_results(function_name, report_intro, to_json=False)

@pytest.mark.asyncio
async def test_publish_to_pdf_file():
    function_name = inspect.currentframe().f_code.co_name
    llm_publisher, research_state = setup_research_state("tst_research_state_5")
    report_intro = await llm_publisher.publish_to_pdf_file()
    dump_test_results(function_name, report_intro, to_json=False)
    
@pytest.mark.asyncio
async def test_publish_to_word_file():
    function_name = inspect.currentframe().f_code.co_name
    llm_publisher, research_state = setup_research_state("tst_research_state_5")
    report_intro = await llm_publisher.publish_to_word_file()
    dump_test_results(function_name, report_intro, to_json=False)
    