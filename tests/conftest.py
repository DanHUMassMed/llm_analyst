# conftest.py
import logging

def pytest_configure(config):
    logging.basicConfig(filename='llm_analyst.log', level=logging.DEBUG)
