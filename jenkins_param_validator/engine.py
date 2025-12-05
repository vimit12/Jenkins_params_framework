# jenkins_param_validator/engine.py
import json
from jsonschema import Draft202012Validator
from .coercion import coerce_data
from .plugins import run_custom_validators


class ValidationError(Exception):
    pass


def load_json(path: str):
    with open(path) as f:
        return json.load(f)


def validate_params(input_file: str, schema_file: str, *, coerce: bool = True, strict: bool = False):
    data = load_json(input_file)
    schema = load_json(schema_file)

    if coerce:
        data = coerce_data(data, schema)

    if strict:
        # No unknown keys allowed:
        allowed_keys = set(schema.get("properties", {}).keys())
        unknown = set(data.keys()) - allowed_keys
        if unknown:
            raise ValidationError(f"Unknown parameters: {', '.join(sorted(unknown))}")

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    if errors:
        msgs = []
        for err in errors:
            path = ".".join(map(str, err.path)) or "<root>"
            msgs.append(f"[{path}] {err.message}")
        raise ValidationError("Schema validation failed:\n" + "\n".join(msgs))

    # Run optional custom plugin validators
    run_custom_validators(data, schema)

    return data  # validated+coerced config