import os
import importlib

def get_resource_path():
    package_nm="llm_analyst.resources"
    module_spec = importlib.util.find_spec(package_nm)
    package_path = os.path.dirname(module_spec.origin)
    return package_path


