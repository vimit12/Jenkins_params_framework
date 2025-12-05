# jenkins_param_validator/engine.py
import json
from jsonschema import Draft202012Validator
from .coercion import coerce_data
from .plugins import run_custom_validators


class ValidationError(Exception):
    """Custom validation error with detailed error info"""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or []


def load_json(path: str):
    with open(path) as f:
        return json.load(f)


def validate_params(input_file: str, schema_file: str, *, coerce: bool = True, strict: bool = False):
    data = load_json(input_file)
    schema = load_json(schema_file)
    collected_errors = []

    if coerce:
        try:
            data = coerce_data(data, schema)
        except ValueError as e:
            # Extract field name from coercion error
            error_str = str(e)
            collected_errors.append({
                "field": error_str.split("'")[1] if "'" in error_str else "unknown",
                "value": str(e),
                "type": "coercion",
                "error": str(e)
            })
            raise ValidationError("Coercion failed", errors=collected_errors)

    if strict:
        # No unknown keys allowed:
        allowed_keys = set(schema.get("properties", {}).keys())
        unknown = set(data.keys()) - allowed_keys
        if unknown:
            for key in sorted(unknown):
                collected_errors.append({
                    "field": key,
                    "value": str(data[key]),
                    "type": "unknown",
                    "error": f"Unknown parameter"
                })
            raise ValidationError("Unknown parameters found", errors=collected_errors)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    if errors:
        for err in errors:
            field_path = ".".join(map(str, err.path)) or "<root>"
            field_value = data.get(field_path, "N/A") if field_path != "<root>" else "N/A"
            prop_schema = schema.get("properties", {}).get(field_path, {})
            field_type = prop_schema.get("type", "unknown")
            
            collected_errors.append({
                "field": field_path,
                "value": str(field_value),
                "type": field_type,
                "error": err.message
            })
        
        raise ValidationError("Schema validation failed", errors=collected_errors)

    # Run optional custom plugin validators
    run_custom_validators(data, schema)

    return data  # validated+coerced config