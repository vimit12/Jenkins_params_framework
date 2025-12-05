# Jenkins Parameter Validator Framework

A Python-based validation framework for Jenkins pipeline parameters using JSON Schema with support for type coercion and custom validators.

## Overview

This framework provides:
- **JSON Schema validation** (Draft 2020-12) for Jenkins pipeline parameters
- **Type coercion** to convert string inputs to proper types (integer, boolean, etc.)
- **Custom plugin validators** for domain-specific validation rules
- **Strict mode** to reject unknown parameters
- **CLI tool** for easy integration into Jenkinsfiles

## Project Structure

```
.
├── Jenkinsfile                          # Jenkins pipeline definition
├── scripts/
│   └── validate_params.py               # CLI entry point
├── schemas/
│   └── deploy-service.schema.json       # Example schema
└── jenkins_param_validator/
    ├── __init__.py
    ├── engine.py                        # Core validation engine
    ├── coercion.py                      # Type coercion logic
    ├── plugins.py                       # Custom validator plugin system
    └── utils.py
```

## Installation

```bash
pip install jsonschema
```

## Quick Start

### 1. Define Your Schema

Create a JSON Schema file (e.g., `schemas/deploy-service.schema.json`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "APP_NAME": { "type": "string", "minLength": 2 },
    "REPLICAS": { "type": "integer", "minimum": 1, "x-coerce": true }
  },
  "required": ["APP_NAME"],
  "additionalProperties": false
}
```

### 2. Validate Parameters

```bash
python3 scripts/validate_params.py \
  --input input.json \
  --schema schemas/deploy-service.schema.json \
  --strict
```

### Usage

```
usage: validate_params.py [-h] --input INPUT --schema SCHEMA [--no-coerce] [--strict]

options:
  --input INPUT      Path to input.json
  --schema SCHEMA    Path to schema.json
  --no-coerce        Disable type coercion
  --strict           Reject unknown parameters
```

## Features

### Type Coercion

Enable automatic type conversion using the `x-coerce` property in your schema:

```json
{
  "REPLICAS": {
    "type": "integer",
    "x-coerce": true
  },
  "RUN_TESTS": {
    "type": "boolean",
    "x-coerce": true
  }
}
```

Supported coercions:
- `integer`: `"42"` → `42`
- `number`: `"3.14"` → `3.14`
- `boolean`: `"true"`, `"yes"`, `"1"` → `true`; `"false"`, `"no"`, `"0"` → `false`
- `string`: Any value → string

### Custom Validators

Define custom validation logic using plugins:

```json
{
  "x-validators": [
    "team_validators.deploy_rules:validate_deploy"
  ]
}
```

Your validator function receives the data and schema:

```python
def validate_deploy(data: Dict[str, Any], schema: Dict[str, Any]):
    if data.get("ENV") == "prod" and not data.get("ALLOW_PROD_DEPLOY"):
        raise ValueError("Production deployment not allowed")
```

### Strict Mode

Enable strict mode to reject parameters not defined in the schema:

```bash
python3 scripts/validate_params.py --input input.json --schema schema.json --strict
```

## Jenkins Integration

The [Jenkinsfile](Jenkinsfile) demonstrates full integration:

```groovy
stage('Validate Parameters') {
    steps {
        sh """
            python3 scripts/validate_params.py \
              --input input.json \
              --schema ${env.PARAM_SCHEMA} \
              --strict
        """
    }
}
```

## API Reference

### [`validate_params()`](jenkins_param_validator/engine.py)

```python
def validate_params(
    input_file: str,
    schema_file: str,
    *,
    coerce: bool = True,
    strict: bool = False
) -> Dict[str, Any]
```

Returns validated (and optionally coerced) configuration dictionary.

Raises `ValidationError` on schema violations or custom validator failures.

### [`coerce_data()`](jenkins_param_validator/coercion.py)

Converts top-level properties based on schema type definitions and `x-coerce` flag.

### [`run_custom_validators()`](jenkins_param_validator/plugins.py)

Executes custom validators specified in schema's `x-validators` array.

## Example Schema

See [schemas/deploy-service.schema.json](schemas/deploy-service.schema.json) for a complete example with:
- Required parameters
- Type constraints (string patterns, integer ranges)
- Enum restrictions
- Conditional coercion rules

## Error Handling

The CLI provides clear error messages:

```
❌ Parameter validation failed

Schema validation failed:
[REPLICAS] 25 is greater than the maximum of 20
[IMAGE_TAG] 'invalid/tag' does not match '^[a-zA-Z0-9._-]+$'
```

Exit codes:
- `0`: Validation successful
- `1`: Validation error
- `2`: Unexpected error

## Development

Extend the framework by:
1. Adding custom coercion types in [`coercion.py`](jenkins_param_validator/coercion.py)
2. Creating custom validators as Python modules
3. Adding new schema properties with `x-` prefix convention

## License

Vimit