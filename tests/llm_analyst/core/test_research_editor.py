import inspect
import json
import inspect
import logging
from tests.utils_for_pytest import dump_test_results, get_resource_file_path
import pytest

from llm_analyst.core.research_editor import LLMEditor
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
    
    llm_editor = LLMEditor.init(research_state, config = config)
    return llm_editor, research_state


@pytest.mark.asyncio
async def test_editor_init():
    """Test the init method
    """
    function_name = inspect.currentframe().f_code.co_name
    llm_editor, research_state = setup_research_state("tst_research_state_4")
    llm_editor_from_research_state = LLMEditor.init(research_state)
        
    # actual_result.dump(test_json_file_path)
    # Assertion: Check that the function returns the expected result
    assert research_state.dump() == llm_editor_from_research_state.dump()

@pytest.mark.asyncio
async def test_create_detailed_report():
    function_name = inspect.currentframe().f_code.co_name
    research_topic = "What happened in the latest burning man floods?"

    config = Config()
    config._set_values_for_config(CONFIG_PARAMS)
    llm_editor = LLMEditor(research_topic, config = config)

    actual_result = await llm_editor.create_detailed_report()
    dump_test_results(function_name, actual_result.dump())
     
     
     