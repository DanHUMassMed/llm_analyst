""" Test Cases for VectorStore """

import inspect
import os
import logging
from tests.utils_for_pytest import (
    dump_test_results,
    get_resource_file_path,
    OUTPUT_PATH,
)
import pytest

from llm_analyst.documents.vector_store import VectorStore


logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_vector_storecreate():
    function_name = inspect.currentframe().f_code.co_name

    cache_directory = os.path.join(OUTPUT_PATH, "cache")
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)

    local_store_dir = get_resource_file_path("tst_documents")

    vector_db = await VectorStore.create(cache_directory, local_store_dir)

    # dump_test_results(function_name, document_data)


@pytest.mark.asyncio
async def test_vector_storeretrieve_docs_for_query():
    function_name = inspect.currentframe().f_code.co_name

    cache_directory = os.path.join(OUTPUT_PATH, "cache")
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)

    local_store_dir = get_resource_file_path("tst_documents")

    vector_db = await VectorStore.create(cache_directory, local_store_dir)
    query = "stress response"
    docs = await vector_db.retrieve_docs_for_query(query)

    dump_test_results(function_name, docs, to_json=False)


@pytest.mark.asyncio
async def test_vector_storeretrieve_pages_for_query():
    function_name = inspect.currentframe().f_code.co_name

    cache_directory = os.path.join(OUTPUT_PATH, "cache")
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)

    local_store_dir = get_resource_file_path("tst_documents")

    vector_db = await VectorStore.create(cache_directory, local_store_dir)
    query = "stress response"
    pages = await vector_db.retrieve_pages_for_query(query)
    # # Assert we did get some data
    # assert len(document_data) > 1
    # sorted_keys = sorted(list(document_data[0].keys()))

    # # Assert the data is a dictionary with the below keys
    # expected_value = ["raw_content", "url"]
    # assert  isinstance(document_data[0], dict)
    # assert sorted_keys == expected_value

    dump_test_results(function_name, pages, to_json=True)

if __name__ == "__main__":
    pytest.main([__file__])
    