""" Test Cases for ContextCompressor """

import inspect
import json

import logging
from tests.utils_for_pytest import dump_test_results, get_resource_file_path
import pytest

from llm_analyst.embedding_methods.compressor import ContextCompressor
from llm_analyst.core.config import Config

logger = logging.getLogger(__name__)


def test_context_compressor_get_context():
    function_name = inspect.currentframe().f_code.co_name
    config = Config()
    local_store_dir = get_resource_file_path("tst_documents")
    config.set_values_for_config(
        {"local_store_dir": local_store_dir, "embedding_provider": "openai"}
    )

    documents_path = get_resource_file_path("tst_documents.json")
    with open(documents_path, "r") as file:
        documents = json.load(file)

    query = "how is gene expression effected by stress?"
    context_compressor = ContextCompressor(
        documents=documents, embeddings=config.embedding_provider
    )
    context = context_compressor.get_context(query, max_results=8)
    assert len(context_compressor.unique_documents_visited) > 0

    dump_test_results(function_name, context, to_json=False)

if __name__ == "__main__":
    pytest.main([__file__])
    