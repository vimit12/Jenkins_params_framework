# jenkins_param_validator/coercion.py
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

    # arrays, objects — handled elsewhere or left untouched
    return value


def coerce_data(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Walks top-level properties and coerces based on schema["properties"][key]["type"]
    if x-coerce=true is set.
    You can extend this to nested objects later.
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