"""Utility methods for pytests"""
import os
import json

DUMP_API_CALL = True
OUTPUT_PATH = "test_output"

def dump_api_call(function_name, actual_result, to_json=True):
    if DUMP_API_CALL:
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)
        if to_json:
            actual_result = json.dumps(actual_result, indent=4)

        with open(f"{OUTPUT_PATH}/{function_name}.txt", 'w', encoding='utf-8') as file:
            file.write(actual_result)
