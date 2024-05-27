import inspect
import json
import inspect
import logging
from tests.utils_for_pytest import dump_test_results, get_resource_file_path
import pytest

from llm_analyst.core.research_writer import LLMWriter
from llm_analyst.core.research_state import ResearchState
from llm_analyst.core.config import Config

logger = logging.getLogger(__name__)

CONFIG_PARAMS = {
    "internet_search" :"ddg_search",
    "max_iterations"  :3,
    "llm_temperature" :0,
    "max_subtopics"   :3
}

def setup_research_state(function_name):
    test_json_file_path = get_resource_file_path(f"{function_name}.json")
    research_state = ResearchState.load(test_json_file_path)
    
    config = Config()
    config._set_values_for_config(CONFIG_PARAMS)
    
    llm_writer = LLMWriter.init(research_state, config = config)
    return llm_writer, research_state


@pytest.mark.asyncio
async def test_writer_init():
    """Test the init method
    """
    function_name = inspect.currentframe().f_code.co_name
    llm_writer, research_state = setup_research_state("tst_research_state_4")
    llm_writer_from_research_state = LLMWriter.init(research_state)
        
    # Assertion: Check that the function returns the expected result
    assert research_state.dump() == llm_writer_from_research_state.dump()
    
def test_extract_headers():
    function_name = inspect.currentframe().f_code.co_name
    llm_writer, research_state = setup_research_state("tst_research_state_5")
    report_headers = llm_writer._extract_headers()
    assert len(report_headers) == 3
    dump_test_results(function_name, report_headers)
    
    
@pytest.mark.asyncio
async def test_write_introduction():
    function_name = inspect.currentframe().f_code.co_name
    llm_writer, research_state = setup_research_state("tst_research_state_5")
    report_intro = await llm_writer.write_introduction()
    dump_test_results(function_name, report_intro, to_json=False)
    
@pytest.mark.asyncio
async def test_write_table_of_contents():
    function_name = inspect.currentframe().f_code.co_name
    llm_writer, research_state = setup_research_state("tst_research_state_5")
    toc = await llm_writer.write_table_of_contents()
    dump_test_results(function_name, toc, to_json=False)
 
@pytest.mark.asyncio  
async def test_write_references():
    function_name = inspect.currentframe().f_code.co_name
    llm_writer, research_state = setup_research_state("tst_research_state_5")
    toc = await llm_writer.write_references()
    dump_test_results(function_name, toc, to_json=False)
