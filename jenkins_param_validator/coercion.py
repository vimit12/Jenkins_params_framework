# jenkins_param_validator/coercion.py
import json
from typing import Any, Dict


def _coerce_simple(value: Any, target_type: str):
    if value is None:
        return None

    if target_type == "integer":
        if isinstance(value, int):
            return value
        return int(value)

    if target_type == "number":
        if isinstance(value, (int, float)):
            return value
        return float(value)

    if target_type == "boolean":
        if isinstance(value, bool):
            return value
        s = str(value).strip().lower()
        if s in ("true", "1", "yes", "y"):
            return True
        if s in ("false", "0", "no", "n"):
            return False
        raise ValueError(f"Cannot coerce '{value}' to boolean")

    if target_type == "string":
        return str(value)

    if target_type == "object":
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValueError(f"Cannot parse JSON: {value}")
        raise ValueError(f"Cannot coerce to object: {type(value).__name__}")

    if target_type == "array":
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if not isinstance(parsed, list):
                    raise ValueError(f"JSON is not an array: {type(parsed).__name__}")
                return parsed
            except json.JSONDecodeError:
                raise ValueError(f"Cannot parse JSON array: {value}")
        raise ValueError(f"Cannot coerce to array: {type(value).__name__}")

    # arrays, objects — handled elsewhere or left untouched
    return value


def coerce_data(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Walks top-level properties and coerces based on schema["properties"][key]["type"]
    if x-coerce=true is set.
    Supports: integer, number, boolean, string, object, array

    Examples:
    - string '{"key": "value"}' -> object {"key": "value"}
    - string '[1, 2, 3]' -> array [1, 2, 3]
    - string '42' -> integer 42
    """
    props = schema.get("properties", {})
    result = dict(data)

    for key, prop_schema in props.items():
        if key not in result:
            continue

        if not prop_schema.get("x-coerce", False):
            continue

        target_type = prop_schema.get("type")
        if not target_type:
            continue

        try:
            result[key] = _coerce_simple(result[key], target_type)
        except Exception as e:
            raise ValueError(f"Coercion failed for '{key}': {e}") from e

    return result