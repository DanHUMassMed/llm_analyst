"""Utility methods for pytests"""
import os
import json

DUMP_API_CALL = True
OUTPUT_PATH = "test_output"

def dump_test_results(function_name, actual_result, to_json=True):
    if DUMP_API_CALL:
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)
        if to_json:
            actual_result = json.dumps(actual_result, indent=4)
        if not isinstance(actual_result, str):
            actual_result = str(actual_result)

        with open(f"{OUTPUT_PATH}/{function_name}.txt", 'w', encoding='utf-8') as file:
            file.write(actual_result)

def get_resource_file_path(file_nm):
    current_directory = os.getcwd()
    path_to_resources = "tests/resources/"
    file_path = os.path.join(current_directory, path_to_resources, file_nm)
    return file_path