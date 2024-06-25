""" Test Cases for LLMEditor """

import inspect
import logging

import pytest

from llm_analyst.core.config import Config
from llm_analyst.core.research_editor import LLMEditor
from llm_analyst.core.research_state import ResearchState
from tests.utils_for_pytest import dump_test_results, get_resource_file_path

logger = logging.getLogger(__name__)

CONFIG_PARAMS = {
    "internet_search": "ddg_search",
    "llm_provider": "openai",
    "llm_model": "gpt-3.5-turbo",
    "max_iterations": 3,
    "llm_temperature": 0,
    "max_subtopics": 3  
}


def setup_research_state(function_name):
    test_json_file_path = get_resource_file_path(f"{function_name}.json")
    research_state = ResearchState.load(test_json_file_path)

    config = Config()
    config._set_values_for_config(CONFIG_PARAMS)

    llm_editor = LLMEditor(config=config, **research_state.dump())
    return llm_editor, research_state


@pytest.mark.asyncio
async def test_editor_create_detailed_report():
    function_name = inspect.currentframe().f_code.co_name
    research_topic = "What is Langchain? And what can we expect from this product in the future?"

    config = Config()
    config._set_values_for_config(CONFIG_PARAMS)
    llm_editor = LLMEditor(active_research_topic=research_topic, config=config)

    actual_result = await llm_editor.create_detailed_report()
    # NOTE: Creating the report does not Publish the report!
    # You can validate the output at test_output/test_create_detailed_report.txt
    dump_test_results(function_name, actual_result.dump())

if __name__ == "__main__":
    pytest.main([__file__])
    