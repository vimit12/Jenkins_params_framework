import importlib
from typing import Any, Dict, List


def run_custom_validators(data: Dict[str, Any], schema: Dict[str, Any]):
    validators: List[str] = schema.get("x-validators", [])
    for path in validators:
        module_name, func_name = path.split(":", 1)
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        func(data, schema)  # raise on error
