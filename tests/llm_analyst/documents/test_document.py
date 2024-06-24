""" Test Cases for DocumentLoader """

import inspect
import logging

import pytest

from llm_analyst.documents.document import DocumentLoader
from tests.utils_for_pytest import dump_test_results, get_resource_file_path

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_document_loader_load_document():
    function_name = inspect.currentframe().f_code.co_name
    local_store_dir = get_resource_file_path("tst_documents")
    file_path = f"{local_store_dir}/Nature-An ARC-Mediator_subunit_required_for_SREBP_control_of_cholesterol_and_lipid_homeostasis.pdf"
    document_loader = DocumentLoader(local_store_dir)
    document = await document_loader._load_document(file_path, "pdf")
    assert len(document) == 5

    dump_test_results(function_name, len(document), to_json=False)


@pytest.mark.asyncio
async def test_document_loader_load_documents():
    function_name = inspect.currentframe().f_code.co_name
    local_store_dir = get_resource_file_path("tst_documents")
    document_loader = DocumentLoader(local_store_dir)
    document = await document_loader.load_local_documents()
    assert len(document) == 31

    dump_test_results(function_name, document, to_json=False)


@pytest.mark.asyncio
async def test_document_loader_load():
    function_name = inspect.currentframe().f_code.co_name
    local_store_dir = get_resource_file_path("tst_documents")

    document_loader = DocumentLoader(local_store_dir)
    document_data = await document_loader.load()

    # Assert we did get some data
    assert len(document_data) > 1
    sorted_keys = sorted(list(document_data[0].keys()))

    # Assert the data is a dictionary with the below keys
    expected_value = ["raw_content", "url"]
    assert isinstance(document_data[0], dict)
    assert sorted_keys == expected_value

    dump_test_results(function_name, document_data)

if __name__ == "__main__":
    pytest.main([__file__])
    
    