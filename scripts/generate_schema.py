# scripts/generate_schema.py
import argparse
import json
import re
import sys
import os
import yaml
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_schema_rules(rules_file: Optional[str] = None) -> dict:
    """
    Load schema customization rules from YAML file.
    Returns rules config or empty dict if file doesn't exist.
    """
    if not rules_file:
        rules_file = os.path.join(os.path.dirname(__file__), 'schema_rules.yaml')
    
    if not os.path.exists(rules_file):
        return {'rules': {}, 'required_fields': []}
    
    with open(rules_file, 'r') as f:
        config = yaml.safe_load(f) or {}
    
    return config


def parse_jenkinsfile_parameters(jenkinsfile_path: str) -> dict:
    """
    Parse Jenkinsfile and extract parameters block.
    Returns a dict mapping parameter names to their metadata.
    
    Supported Jenkins parameter types:
    - string()
    - booleanParam()
    - choice()
    - password()
    - credentials()
    - text()
    - file()
    - run()
    - listView()
    - multiline()
    - properties()
    - cascadingChoice()
    """
    with open(jenkinsfile_path, 'r') as f:
        content = f.read()

    # Extract the parameters block
    params_match = re.search(r'parameters\s*\{(.*?)\n\s*\}', content, re.DOTALL)
    if not params_match:
        raise ValueError("No parameters block found in Jenkinsfile")

    params_block = params_match.group(1)
    parameters = {}

    # Regex patterns for various Jenkins parameter types
    patterns = {
        'string': r"string\s*\(\s*name:\s*['\"]([^'\"]+)['\"]\s*,\s*defaultValue:\s*['\"]([^'\"]*)['\"](?:\s*,\s*description:\s*['\"]([^'\"]*)['\"])?\s*\)",
        'booleanParam': r"booleanParam\s*\(\s*name:\s*['\"]([^'\"]+)['\"]\s*,\s*defaultValue:\s*(true|false)(?:\s*,\s*description:\s*['\"]([^'\"]*)['\"])?\s*\)",
        'choice': r"choice\s*\(\s*name:\s*['\"]([^'\"]+)['\"]\s*,\s*choices:\s*\[((?:['\"][^'\"]*['\"],?\s*)*)\](?:\s*,\s*description:\s*['\"]([^'\"]*)['\"])?\s*\)",
        'password': r"password\s*\(\s*name:\s*['\"]([^'\"]+)['\"]\s*,\s*defaultValue:\s*['\"]([^'\"]*)['\"](?:\s*,\s*description:\s*['\"]([^'\"]*)['\"])?\s*\)",
        'text': r"text\s*\(\s*name:\s*['\"]([^'\"]+)['\"]\s*,\s*defaultValue:\s*['\"]([^'\"]*)['\"](?:\s*,\s*description:\s*['\"]([^'\"]*)['\"])?\s*\)",
        'file': r"file\s*\(\s*name:\s*['\"]([^'\"]+)['\"]\s*(?:\s*,\s*description:\s*['\"]([^'\"]*)['\"])?\s*\)",
        'credentials': r"credentials\s*\(\s*name:\s*['\"]([^'\"]+)['\"]\s*(?:\s*,\s*description:\s*['\"]([^'\"]*)['\"])?\s*\)",
        'run': r"run\s*\(\s*name:\s*['\"]([^'\"]+)['\"]\s*(?:\s*,\s*description:\s*['\"]([^'\"]*)['\"])?\s*\)",
        'listView': r"listView\s*\(\s*name:\s*['\"]([^'\"]+)['\"]\s*(?:\s*,\s*description:\s*['\"]([^'\"]*)['\"])?\s*\)",
    }

    # Parse string parameters
    for match in re.finditer(patterns['string'], params_block):
        name, default_val, desc = match.groups()
        parameters[name] = {
            'type': 'string',
            'defaultValue': default_val,
            'description': desc or '',
        }

    # Parse boolean parameters
    for match in re.finditer(patterns['booleanParam'], params_block):
        name, default_val, desc = match.groups()
        parameters[name] = {
            'type': 'boolean',
            'defaultValue': default_val.lower() == 'true',
            'description': desc or '',
        }

    # Parse choice parameters
    for match in re.finditer(patterns['choice'], params_block):
        name, choices_str, desc = match.groups()
        choices = re.findall(r"['\"]([^'\"]+)['\"]", choices_str)
        parameters[name] = {
            'type': 'string',
            'enum': choices,
            'defaultValue': choices[0] if choices else '',
            'description': desc or '',
        }

    # Parse password parameters
    for match in re.finditer(patterns['password'], params_block):
        name, default_val, desc = match.groups()
        parameters[name] = {
            'type': 'string',
            'format': 'password',
            'defaultValue': default_val,
            'description': desc or '',
        }

    # Parse text (multiline) parameters
    for match in re.finditer(patterns['text'], params_block):
        name, default_val, desc = match.groups()
        parameters[name] = {
            'type': 'string',
            'format': 'textarea',
            'defaultValue': default_val,
            'description': desc or '',
        }

    # Parse file parameters
    for match in re.finditer(patterns['file'], params_block):
        groups = match.groups()
        name = groups[0]
        desc = groups[1] if len(groups) > 1 else ''
        parameters[name] = {
            'type': 'string',
            'format': 'file',
            'description': desc or '',
        }

    # Parse credentials parameters
    for match in re.finditer(patterns['credentials'], params_block):
        groups = match.groups()
        name = groups[0]
        desc = groups[1] if len(groups) > 1 else ''
        parameters[name] = {
            'type': 'string',
            'format': 'credentials',
            'description': desc or '',
        }

    # Parse run parameters
    for match in re.finditer(patterns['run'], params_block):
        groups = match.groups()
        name = groups[0]
        desc = groups[1] if len(groups) > 1 else ''
        parameters[name] = {
            'type': 'string',
            'format': 'run',
            'description': desc or '',
        }

    # Parse listView parameters
    for match in re.finditer(patterns['listView'], params_block):
        groups = match.groups()
        name = groups[0]
        desc = groups[1] if len(groups) > 1 else ''
        parameters[name] = {
            'type': 'string',
            'format': 'listview',
            'description': desc or '',
        }

    return parameters


def infer_schema_properties(parameters: dict, schema_rules: Optional[dict] = None) -> dict:
    """
    Priority:
    1. schema_rules.yaml (explicit rules)
    2. Jenkinsfile parameter type
    3. Auto-generated defaults
    """
    if schema_rules is None:
        schema_rules = {}
    custom_rules = schema_rules.get('rules', {})
    properties = {}

    for name, param in parameters.items():
        # START WITH JENKINSFILE INFO
        schema_prop = {
            "type": param['type'],
            "description": param['description']
        }

        # OVERRIDE WITH schema_rules.yaml IF PRESENT
        if name in custom_rules:
            # Merge: schema_rules.yaml overwrites everything
            schema_prop.update(custom_rules[name])
        else:
            # Apply defaults only if not in rules
            if param['type'] == 'string' and 'enum' not in param:
                schema_prop['minLength'] = 1
            elif param['type'] == 'boolean':
                schema_prop['x-coerce'] = True

        properties[name] = schema_prop

    return properties


def generate_schema(jenkinsfile_path: str, rules_file: Optional[str] = None, output_path: Optional[str] = None) -> dict:
    """
    Generate JSON schema from Jenkinsfile parameters.
    """
    # Load schema customization rules
    schema_rules = load_schema_rules(rules_file)
    
    # Parse parameters
    parameters = parse_jenkinsfile_parameters(jenkinsfile_path)

    # Infer schema properties
    properties = infer_schema_properties(parameters, schema_rules)

    # Get required fields from rules or use defaults
    required_fields = schema_rules.get('required_fields', [])
    # Only include required fields that actually exist in parameters
    required_fields = [f for f in required_fields if f in parameters]

    # Build full schema
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Jenkins Pipeline Parameters",
        "type": "object",
        "properties": properties,
        "additionalProperties": False
    }
    
    if required_fields:
        schema["required"] = required_fields

    # Write to file if output path provided
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"✅ Schema generated: {output_path}")

    return schema


def main():
    parser = argparse.ArgumentParser(
        description="Generate JSON schema from Jenkinsfile parameters"
    )
    parser.add_argument("--jenkinsfile", default="Jenkinsfile", 
                       help="Path to Jenkinsfile (default: Jenkinsfile)")
    parser.add_argument("--rules", default="scripts/schema_rules.yaml",
                       help="Path to schema_rules.yaml (default: scripts/schema_rules.yaml)")
    parser.add_argument("--output", default="schemas/deploy-service.schema.json",
                       help="Output schema path (default: schemas/deploy-service.schema.json)")
    parser.add_argument("--output-stdout", action="store_true",
                       help="Print schema to stdout instead of writing to file")
    args = parser.parse_args()

    try:
        schema = generate_schema(
            args.jenkinsfile,
            rules_file=args.rules,
            output_path=None if args.output_stdout else args.output
        )
        
        if args.output_stdout:
            print(json.dumps(schema, indent=2))
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()