import inspect
import json
import inspect
import logging
from tests.utils_for_pytest import dump_test_results, get_resource_file_path
import pytest

from llm_analyst.embedding_methods.compressor import ContextCompressor
from llm_analyst.document.document import DocumentLoader
from llm_analyst.core.research_analyst import LLMAnalyst
from llm_analyst.core.research_state import ResearchState
from llm_analyst.core.config import Config

logger = logging.getLogger(__name__)


@pytest.mark.asyncio   
async def test_load():
    function_name = inspect.currentframe().f_code.co_name

    config = Config()
    local_store_dir = get_resource_file_path("tst_documents")
    config._set_values_for_config({"local_store_dir":local_store_dir})
        
    document_data = await DocumentLoader(config.local_store_dir).load()
    
    # Assert we did get some data
    assert len(document_data) > 1
    sorted_keys = sorted(list(document_data[0].keys()))
    
    # Assert the data is a dictionary with the below keys 
    expected_value = ["raw_content", "url"]
    assert sorted_keys == expected_value
    
    dump_test_results(function_name, document_data)
    
