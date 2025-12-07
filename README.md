# Jenkins Parameter Validator Framework

A powerful, flexible Python-based validation framework for Jenkins pipeline parameters using JSON Schema with automatic schema generation, type coercion, and custom validators.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Jenkins Parameter Types](#jenkins-parameter-types)
- [Schema Rules Configuration](#schema-rules-configuration)
- [Type Coercion](#type-coercion)
- [Validation Flow](#validation-flow)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Security Considerations](#security-considerations)
- [Exit Codes](#exit-codes)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## 🎯 Overview

This framework automates validation of Jenkins pipeline parameters by:

1. **Parsing your Jenkinsfile** to extract parameter definitions
2. **Auto-generating a JSON Schema** from those parameters
3. **Applying custom rules** from `schema_rules.yaml`
4. **Validating input parameters** against the generated schema
5. **Coercing types** automatically (strings to integers, booleans, JSON objects, etc.)
6. **Running custom validators** for business logic

## ✨ Features

- ✅ **Automatic Schema Generation** - Parse Jenkinsfile and generate JSON Schema
- ✅ **Type Coercion** - Automatically convert strings to integers, booleans, JSON objects
- ✅ **Rich Error Messages** - Table-formatted validation errors with field details
- ✅ **Custom Validators** - Extend with Python plugins for complex rules
- ✅ **Strict Mode** - Reject unknown/undeclared parameters
- ✅ **Conditional Validation** - Field dependencies and mutual exclusivity
- ✅ **No Plugin Dependencies** - Pure Groovy, works with standard Jenkins
- ✅ **Format Validation** - Email, URI, date-time, regex patterns
- ✅ **Range Constraints** - min/max, minLength/maxLength for all types
- ✅ **Enum Support** - Restrict values to predefined choices
- ✅ **JSON/Array Support** - Parse and validate nested JSON structures

## Project Structure

```
jenkins_param_framework/
├── Jenkinsfile                          # Example Jenkins pipeline with parameters
├── README.md                            # This file
├── requirements.txt                     # Python dependencies (jsonschema, rich, pyyaml)
│
├── scripts/
│   ├── validate_params.py               # CLI validation entry point (main validator script)
│   ├── generate_schema.py               # Schema generator from Jenkinsfile (parses params)
│   └── schema_rules.yaml                # Custom validation rules and constraints
│
├── schemas/
│   └── deploy-service.schema.json       # Generated JSON schema from Jenkinsfile
│
├── jenkins_param_validator/             # Core Python validation package
│   ├── __init__.py
│   ├── engine.py                        # Core validation engine (main logic)
│   ├── coercion.py                      # Type coercion (string → int, bool, json, etc)
│   ├── plugins.py                       # Custom validator plugin system
│   ├── validators.py                    # Example custom validators (business logic)
│   └── utils.py                         # Utility functions
│
├── vars/                                # Jenkins Shared Library entry point
│   └── validateParams.groovy            # Main Groovy wrapper (auto-extracts resources)
│
├── resources/                           # Shared Library packaged resources
│   ├── scripts/
│   │   └── validate_params.py           # Bundled validator script
│   ├── requirements.txt                 # Bundled dependencies
│   └── jenkins_param_validator/         # Bundled minimal package
│       ├── __init__.py
│       ├── engine.py
│       ├── coercion.py
│       ├── plugins.py
│       └── validators.py
│
└── jenkins_shared_lib/                  # Alternative shared library layout (legacy)
    └── vars/
        └── validateParams.groovy
```

### Folder Roles

- **`scripts/`** — Standalone CLI tools (executable directly from Jenkins or development)
- **`jenkins_param_validator/`** — Core Python package (imported by scripts and validators)
- **`schemas/`** — Generated JSON Schema files (output from `generate_schema.py`)
- **`vars/`** — Jenkins Shared Library entry points (Groovy; loaded when repo is used as a library)
- **`resources/`** — Packaged resources bundled with Shared Library (extracted into workspace by `validateParams.groovy` wrapper)
- **`jenkins_shared_lib/`** — Alternative layout for teams preferring explicit shared library structure

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip

## Dependencies
jsonschema>=4.0.0      # JSON Schema validation
rich>=13.0.0           # Formatted table output
pyyaml>=6.0            # Schema rules configuration

### Setup

```bash
# Clone the repository
git clone https://github.com/vimit12/Jenkins_params_framework.git
cd Jenkins_params_framework

# Install dependencies
pip3 install -r requirements.txt
```

## Quick Start

### Step 1: Define Jenkins Parameters
#### Edit your `Jenkinsfile`:

``` groovy
pipeline {
    agent any

    parameters {
        string(name: 'APP_NAME', defaultValue: 'my-api', description: 'Application name')
        string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Docker image tag')
        choice(name: 'ENV', choices: ['dev', 'qa', 'staging', 'prod'], description: 'Environment')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run tests')
        string(name: 'REPLICAS', defaultValue: '2', description: 'Number of replicas')
    }

    stages {
        stage('Validate Parameters') {
            steps {
                sh 'python3 scripts/validate_params.py --input input.json --schema schemas/deploy-service.schema.json --strict'
            }
        }
    }
}

```

### Step 2: Create Schema Rules (Optional)
#### Create `schema_rules.yaml`:

```yaml
rules:
  REPLICAS:
    type: integer
    minimum: 1
    maximum: 20
    x-coerce: true

  IMAGE_TAG:
    type: string
    pattern: "^[a-zA-Z0-9._-]+$"

required_fields:
  - APP_NAME
  - IMAGE_TAG
```

### Step 3: Generate Schema

```bash
python3 scripts/generate_schema.py --jenkinsfile Jenkinsfile --output schemas/deploy-service.schema.json
```

### Step 4: Validate Parameters

```bash
python3 scripts/validate_params.py --input input.json --schema schemas/deploy-service.schema.json --strict
```

### 🔄 How It Works

#### 1. Parameter Parsing

The framework parses your `Jenkinsfile` to extract the following details:

- **Parameter name**
- **Parameter type** (string, boolean, choice, etc.)
- **Default value**
- **Description**

Example :


```json
string(name: 'REPLICAS', defaultValue: '2', description: 'Number of replicas')
                ↓
        {
          "REPLICAS": {
            "type": "string",
            "defaultValue": "2",
            "description": "Number of replicas"
          }
        }
```

### 2. Schema Generation

The schema generator converts **Jenkinsfile parameters** into **JSON Schema**, including:

- **Type information**
- **Default values**
- **Descriptions**
- **Format constraints**

---

### 3. Rule Application

Custom rules from `schema_rules.yaml` override auto-generated constraints.

**Priority Order:**

1. **schema_rules.yaml** (highest) — explicit custom rules  
2. **Jenkinsfile** — parameter definitions  
3. **Auto-defaults** (lowest) — generic constraints  

---

#### Example: Conflict Resolution

```yaml
# schema_rules.yaml
rules:
  REPLICAS:
    type: integer            # Overrides Jenkinsfile's string type
    minimum: 1
    maximum: 20
    x-coerce: true           # Auto-convert "2" → 2
```

#### Result


```json
Input: {"REPLICAS": "2"}
After coercion: {"REPLICAS": 2}
Validation: ✅ Valid (within 1-20 range)
```

### 4. Type Coercion

Strings from Jenkins are automatically converted into proper types:

- `"2"` → **2** (integer)  
- `"true"` → **true** (boolean)  
- `"3.14"` → **3.14** (number)  
- `'{"key":"val"}'` → **{ key: "val" }** (object)  
- `"[1,2,3]"` → **[1, 2, 3]** (array)

---

### 5. Validation

Parameters are validated against the generated schema, including:

- Type checking  
- Range / length constraints  
- Pattern matching  
- Enum restrictions  
- Custom business logic

---

### 6. Error Reporting

Validation errors are displayed in a formatted table:
**Validation Error Details**

| Field Name | Value        | Type    | Error                        |
|------------|--------------|---------|------------------------------|
| REPLICAS   | 25           | integer | 25 is greater than max 20    |
| IMAGE_TAG  | invalid/tag  | string  | does not match pattern       |

### 🔧 Jenkins Parameter Types

The framework supports all common Jenkins parameter types.

| Type        | Syntax             | Schema Type     | Example                                                     |
|-------------|--------------------|------------------|-------------------------------------------------------------|
| String      | `string()`         | string           | `string(name: 'APP', defaultValue: 'my-app')`               |
| Boolean     | `booleanParam()`   | boolean          | `booleanParam(name: 'RUN_TESTS', defaultValue: true)`       |
| Choice      | `choice()`         | string (enum)    | `choice(name: 'ENV', choices: ['dev', 'prod'])`             |
| Password    | `password()`       | string           | `password(name: 'PWD', defaultValue: '')`                   |
| Text        | `text()`           | string           | `text(name: 'CONFIG', defaultValue: '{}')`                  |
| File        | `file()`           | string           | `file(name: 'CERT')`                                        |
| Credentials | `credentials()`    | string           | `credentials(name: 'GIT_CRED')`                             |
| Run         | `run()`            | string           | `run(name: 'BUILD_NUM')`                                    |
| ListView    | `listView()`       | string           | `listView(name: 'VIEW')`                                    |

---

### Example Jenkinsfile with Various Types

```groovy
parameters {
    // String input
    string(name: 'APP_NAME', defaultValue: 'my-app', description: 'App name')
    
    // Dropdown selection
    choice(name: 'ENV', choices: ['dev', 'staging', 'prod'], description: 'Environment')
    
    // Checkbox
    booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run tests')
    
    // Password (masked in UI)
    password(name: 'DB_PASSWORD', defaultValue: '', description: 'DB password')
    
    // Multiline text
    text(name: 'CONFIG_JSON', defaultValue: '{}', description: 'Configuration JSON')
    
    // File upload
    file(name: 'CERT_FILE', description: 'SSL certificate')
    
    // Jenkins credentials
    credentials(name: 'GIT_CREDENTIALS', description: 'Git credentials ID')
}
```

### 📝 Schema Rules Configuration

#### Basic Structure

`schema_rules.yaml` defines custom validation rules:

```yaml
# schema_rules.yaml
rules:
  PARAMETER_NAME:
    type: string|integer|boolean|object|array
    # Type-specific constraints
    minLength: 2
    maxLength: 50
    minimum: 1
    maximum: 100
    pattern: "^regex$"
    enum: [val1, val2]
    
    # Coercion
    x-coerce: true
    
    # Format
    format: email|uri|date-time
    
    # Nested object schema
    properties:
      nested_key: {type: string}
    required: [nested_key]
    
    description: "Field description"

required_fields:
  - REQUIRED_PARAM_1
  - REQUIRED_PARAM_2

conditional_required:
  - condition: "ENV == 'prod'"
    requires: ["ALLOW_PROD_DEPLOY"]

mutually_exclusive:
  - ["PARAM_A", "PARAM_B"]

error_messages:
  PARAMETER_NAME:
    pattern: "Custom error message"
    minimum: "Must be at least X"

custom_validators:
  - "module.path:function_name"

options:
  strict_mode: true
  auto_coerce_numbers: false
  trim_strings: true

```

Comprehensive Example

```yaml
rules:
  # String with pattern
  APP_NAME:
    type: string
    minLength: 2
    maxLength: 50
    pattern: "^[a-z0-9](-?[a-z0-9])*$"
    description: "Application name (lowercase alphanumeric with hyphens)"

  # Docker image tag
  IMAGE_TAG:
    type: string
    pattern: "^[a-zA-Z0-9._-]+$"
    minLength: 1
    maxLength: 128
    description: "Docker image tag"

  # Semantic version
  VERSION:
    type: string
    pattern: "^[0-9]+\\.[0-9]+\\.[0-9]+(-(alpha|beta|rc))?$"
    description: "Semantic version (e.g., 1.2.3 or 1.2.3-rc1)"

  # Integer with range
  REPLICAS:
    type: integer
    minimum: 1
    maximum: 20
    x-coerce: true
    description: "Number of replicas"

  # Enum choice
  LOG_LEVEL:
    type: string
    enum: ["DEBUG", "INFO", "WARNING", "ERROR"]
    description: "Logging level"

  # Email format
  NOTIFICATION_EMAIL:
    type: string
    format: email
    description: "Email for notifications"

  # URI/URL format
  WEBHOOK_URL:
    type: string
    format: uri
    description: "Webhook URL"

  # JSON object with schema
  CONFIG_JSON:
    type: object
    x-coerce: true
    properties:
      replicas:
        type: integer
        minimum: 1
      environment:
        type: string
        enum: ["dev", "prod"]
      debug:
        type: boolean
    required: ["environment"]
    description: "Configuration object"

  # Boolean with coercion
  ENABLE_FEATURE:
    type: boolean
    x-coerce: true
    description: "Enable feature flag"

required_fields:
  - APP_NAME
  - IMAGE_TAG
  - ENV

conditional_required:
  - condition: "ENV == 'prod'"
    requires: ["ALLOW_PROD_DEPLOY", "NOTIFICATION_EMAIL"]
  - condition: "ENABLE_MONITORING == true"
    requires: ["MONITORING_ENDPOINT"]

mutually_exclusive:
  - ["RUN_TESTS", "SKIP_TESTS"]
  - ["ENABLE_CACHE", "DISABLE_CACHE"]

error_messages:
  APP_NAME:
    pattern: "App name must contain only lowercase letters, numbers, and hyphens"
    minLength: "App name must be at least 2 characters"
  
  REPLICAS:
    minimum: "At least 1 replica is required"
    maximum: "Maximum 20 replicas allowed"

custom_validators:
  - "jenkins_param_validator.validators:validate_deployment_rules"
  - "jenkins_param_validator.validators:validate_resource_limits"

options:
  strict_mode: true
  auto_coerce_numbers: false
  trim_strings: true

```

### 💫 Type Coercion

#### What is `x-coerce`?

`x-coerce` is a custom JSON Schema extension that automatically converts **string values into their proper types**.  
This is essential because Jenkins sends **all parameter values as strings**, regardless of their declared type.

#### Why Is It Needed?

Jenkins always passes parameters as strings:

- `"2"` should become **2** (integer)
- `"true"` should become **true** (boolean)
- `"3.14"` should become **3.14** (number)
- `'{"key":"val"}'` should become **{ "key": "val" }** (object)
- `"[1,2,3]"` should become **[1, 2, 3]** (array)

With `x-coerce: true`, your validation system safely normalizes these values before schema validation.

```groovy
parameters {
    string(name: 'REPLICAS', defaultValue: '2')        // String "2"
    booleanParam(name: 'RUN_TESTS', defaultValue: true) // String "true"
}

// In the pipeline, they're passed as:
// {"REPLICAS": "2", "RUN_TESTS": "true"}

```

Without coercion:

```bash
Input: {"REPLICAS": "2"}
Error: "2" is not of type integer
```

With coercion `(x-coerce: true)`:

```bash
Input: {"REPLICAS": "2"}
After coercion: {"REPLICAS": 2}
Result: ✅ Valid
```

### Supported Coercions

| Target Type | From String         | Example                          |
|-------------|----------------------|----------------------------------|
| integer     | Numeric string       | `"42"` → **42**                  |
| number      | Numeric string       | `"3.14"` → **3.14**              |
| boolean     | True values          | `"true"`, `"1"`, `"yes"` → true  |
| boolean     | False values         | `"false"`, `"0"`, `"no"` → false |
| object      | JSON string          | `'{"key":"val"}'` → `{ key: "val" }` |
| array       | JSON array string    | `"[1,2,3]"` → `[1, 2, 3]`         |
| string      | Any value            | `123` → `"123"`                  |

---

### Example Configuration

```yaml
rules:
  REPLICAS:
    type: integer
    x-coerce: true          # "2" → 2

  RUN_TESTS:
    type: boolean
    x-coerce: true          # "true" → true

  CONFIG:
    type: object
    x-coerce: true          # '{"a":"b"}' → {a: "b"}

  TAGS:
    type: array
    x-coerce: true          # '[1,2,3]' → [1, 2, 3]
```


### 🔄 Validation Flow

#### Complete Validation Pipeline

1. **Load Input JSON**  
   ↓  
2. **Load Schema** (from file or generated)  
   ↓  
3. **Type Coercion** (if `x-coerce: true`)  
   - Convert `"2"` → **2**  
   - Convert `"true"` → **true**  
   - Convert `"{}"` → **{}**  
   ↓  
4. **Strict Mode Check** (if `--strict` flag)  
   - Reject unknown parameters  
   - Only allow declared fields  
   ↓  
5. **JSON Schema Validation**  
   - Type checking  
   - Range constraints (min/max)  
   - Length constraints (minLength/maxLength)  
   - Pattern matching (regex)  
   - Enum validation  
   - Required fields  
   ↓  
6. **Custom Validators** (if defined)  
   - Business logic checks  
   - Conditional requirements  
   - Complex rules  
   ↓  
7. **Return Results**  
   - ✅ **Valid:** return coerced data  
   - ❌ **Invalid:** display error table  

---

### Validation Examples

#### Example 1: Simple Type Coercion

```yaml
# schema_rules.yaml
rules:
  PORT:
    type: integer
    minimum: 1024
    x-coerce: true
```

```json
// input.json
{"PORT": "8080"}

// After validation:
{"PORT": 8080}  // ✅ Valid
```

### Example 2: Pattern Validation

```yaml
# schema_rules.yaml
rules:
  IMAGE_TAG:
    type: string
    pattern: "^[a-zA-Z0-9._-]+$"
```

```json
// input.json (valid)
{"IMAGE_TAG": "v1.2.3"}  // ✅ Matches pattern

// input.json (invalid)
{"IMAGE_TAG": "v1.2.3/bad"}  // ❌ Contains slash
```

### Example 3: Range Constraint

```yaml
# schema_rules.yaml
rules:
  REPLICAS:
    type: integer
    minimum: 1
    maximum: 20
    x-coerce: true
```

```json
// input.json (valid)
{"REPLICAS": "5"}  // ✅ Within range 1-20

// input.json (invalid)
{"REPLICAS": "25"}  // ❌ Exceeds maximum
```

### Example 4: Conditional Requirement

```yaml
# schema_rules.yaml
conditional_required:
  - condition: "ENV == 'prod'"
    requires: ["ALLOW_PROD_DEPLOY"]
```

```json
// Valid: Prod with flag
{"ENV": "prod", "ALLOW_PROD_DEPLOY": true}  // ✅

// Invalid: Prod without flag
{"ENV": "prod"}  // ❌ Missing ALLOW_PROD_DEPLOY
```

### 📚 Examples

Complete Jenkinsfile Example

```groovy
pipeline {
    agent any

    parameters {
        string(name: 'APP_NAME', defaultValue: 'my-api', description: 'Application name')
        string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Docker image tag')
        choice(name: 'ENV', choices: ['dev', 'qa', 'staging', 'prod'], description: 'Target environment')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run unit tests')
        string(name: 'REPLICAS', defaultValue: '2', description: 'Number of replicas')
        string(name: 'CPU_LIMIT', defaultValue: '500m', description: 'CPU limit')
        string(name: 'MEMORY_LIMIT', defaultValue: '512Mi', description: 'Memory limit')
        booleanParam(name: 'ALLOW_PROD_DEPLOY', defaultValue: false, description: 'Allow production deployment')
        text(name: 'CONFIG_JSON', defaultValue: '{}', description: 'Configuration JSON')
    }

    environment {
        PARAM_SCHEMA = "schemas/deploy-service.schema.json"
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/vimit12/Jenkins_params_framework.git', branch: 'master'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('Generate Schema') {
            steps {
                sh 'python3 scripts/generate_schema.py --jenkinsfile Jenkinsfile --output ${PARAM_SCHEMA}'
            }
        }

        stage('Write Params JSON') {
            steps {
                sh '''
                    cat > input.json << 'EOF'
{
  "APP_NAME": "${params.APP_NAME}",
  "IMAGE_TAG": "${params.IMAGE_TAG}",
  "ENV": "${params.ENV}",
  "RUN_TESTS": "${params.RUN_TESTS}",
  "REPLICAS": "${params.REPLICAS}",
  "CPU_LIMIT": "${params.CPU_LIMIT}",
  "MEMORY_LIMIT": "${params.MEMORY_LIMIT}",
  "ALLOW_PROD_DEPLOY": "${params.ALLOW_PROD_DEPLOY}",
  "CONFIG_JSON": "${params.CONFIG_JSON}"
}
EOF
                '''
            }
        }

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

        stage('Build & Deploy') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo "✅ All parameters validated successfully!"
                echo "Deploying ${params.APP_NAME}:${params.IMAGE_TAG} to ${params.ENV}"
                // Your deployment logic here
            }
        }
    }
}
```

Complete `schema_rules.yaml` Example

```yaml
# scripts/schema_rules.yaml

rules:
  APP_NAME:
    type: string
    minLength: 2
    maxLength: 50
    pattern: "^[a-z0-9](-?[a-z0-9])*$"
    description: "Application name (lowercase alphanumeric with hyphens)"

  IMAGE_TAG:
    type: string
    pattern: "^[a-zA-Z0-9._-]+$"
    minLength: 1
    maxLength: 128
    description: "Docker image tag"

  ENV:
    type: string
    enum: ["dev", "qa", "staging", "prod"]
    description: "Target environment"

  RUN_TESTS:
    type: boolean
    x-coerce: true
    description: "Run unit tests before deploy"

  REPLICAS:
    type: integer
    minimum: 1
    maximum: 20
    x-coerce: true
    description: "Number of replicas"

  CPU_LIMIT:
    type: string
    pattern: "^[0-9]+(m)?$"
    description: "CPU limit (e.g., 500m)"

  MEMORY_LIMIT:
    type: string
    pattern: "^[0-9]+(Mi|Gi)$"
    description: "Memory limit (e.g., 512Mi or 2Gi)"

  ALLOW_PROD_DEPLOY:
    type: boolean
    x-coerce: true
    description: "Gate for production deployment"

  CONFIG_JSON:
    type: object
    x-coerce: true
    properties:
      replicas:
        type: integer
        minimum: 1
      debug:
        type: boolean
      features:
        type: array
        items:
          type: string
    description: "Configuration JSON object"

required_fields:
  - APP_NAME
  - IMAGE_TAG
  - ENV

conditional_required:
  - condition: "ENV == 'prod'"
    requires: ["ALLOW_PROD_DEPLOY"]

mutually_exclusive:
  - ["RUN_TESTS", "SKIP_TESTS"]

error_messages:
  APP_NAME:
    pattern: "App name must contain only lowercase letters, numbers, and hyphens"
    minLength: "App name must be at least 2 characters"
  
  REPLICAS:
    minimum: "At least 1 replica is required"
    maximum: "Maximum 20 replicas allowed"

  ENV:
    enum: "Invalid environment. Must be one of: dev, qa, staging, prod"

custom_validators:
  - "jenkins_param_validator.validators:validate_deployment_rules"

options:
  strict_mode: true
  auto_coerce_numbers: false
  trim_strings: true
```

## **Shared Library / Reuse In Other Pipelines**

### Option 1: Direct Script Checkout
Clone or checkout this repository in your pipeline and call the Python script directly.

```groovy
pipeline {
  agent any
  stages {
    stage('Checkout Framework') {
      steps {
        git url: 'https://github.com/vimit12/Jenkins_params_framework.git', branch: 'master'
      }
    }

    stage('Install Dependencies') {
      steps {
        sh 'pip3 install -r requirements.txt'
      }
    }

    stage('Validate Parameters') {
      steps {
        sh '''
          python3 scripts/validate_params.py \
            --input input.json \
            --schema schemas/deploy-service.schema.json \
            --strict
        '''
      }
    }
  }
}
```

### Option 2: Jenkins Shared Library (Recommended for Reuse)

Configure this repository as a Jenkins Global Pipeline Library so all your teams can reuse it across multiple pipelines.

#### Step 1: Configure Jenkins Global Pipeline Library

1. In Jenkins, go to **Manage Jenkins → Configure System → Global Pipeline Libraries**
2. Click **Add**
3. Set:
   - **Name:** `param-validator` (this is the identifier you'll use in `@Library`)
   - **Default Version:** `master` (or your preferred branch/tag)
   - **Retrieval method:** Choose Git, then:
     - **Project Repository:** `https://github.com/vimit12/Jenkins_params_framework.git`
   - **Load implicitly:** (optional) Check if you want it auto-loaded for all jobs
   - **Allow default version to be overridden:** (optional) Check to allow per-pipeline versions

4. Click **Save**

#### Step 2: Use in Your Jenkinsfile

Once configured, use `@Library('param-validator') _` in any Jenkinsfile:

```groovy
@Library('param-validator') _

pipeline {
  agent any

  parameters {
    string(name: 'APP_NAME', defaultValue: 'myapp')
    string(name: 'IMAGE_TAG', defaultValue: 'v1.0.0')
    choice(name: 'ENV', choices: ['dev', 'qa', 'prod'])
    string(name: 'REPLICAS', defaultValue: '2')
  }

  stages {
    stage('Write Parameters JSON') {
      steps {
        script {
          def paramsJson = """
          {
            "APP_NAME": "${params.APP_NAME}",
            "IMAGE_TAG": "${params.IMAGE_TAG}",
            "ENV": "${params.ENV}",
            "REPLICAS": "${params.REPLICAS}"
          }
          """
          writeFile file: 'input.json', text: paramsJson
        }
      }
    }

    stage('Write Validation Schema') {
      steps {
        writeFile file: 'schema.json', text: '''
        {
          "type": "object",
          "properties": {
            "APP_NAME": { "type": "string" },
            "IMAGE_TAG": { "type": "string" },
            "ENV": { "type": "string", "enum": ["dev", "qa", "prod"] },
            "REPLICAS": { "type": "integer", "minimum": 1, "x-coerce": true }
          },
          "required": ["APP_NAME", "IMAGE_TAG", "ENV"],
          "additionalProperties": false
        }
        '''
      }
    }

    stage('Validate Parameters') {
      steps {
        // The wrapper automatically:
        // 1. Extracts bundled Python scripts from the shared library (if not present in workspace)
        // 2. Creates a Python virtualenv and installs dependencies
        // 3. Runs the validation
        validateParams(
          input: 'input.json',
          schema: 'schema.json',
          strict: true,
          ensureEnv: true  // optional: set false if you manage Python yourself
        )
      }
    }

    stage('Deploy') {
      when {
        expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
      }
      steps {
        echo "✅ Parameters valid! Proceeding with deployment..."
        // Your deployment logic here
      }
    }
  }
}
```

#### How the Shared Library Wrapper Works

The `vars/validateParams.groovy` wrapper (loaded by Jenkins when you use `@Library('param-validator') _`) performs the following:

1. **Extracts Resources** — If `scripts/validate_params.py` is not in the workspace, it extracts the bundled Python package from the shared library using `libraryResource()`.
2. **Prepares Environment** — Creates a Python virtualenv (`.venv`) and installs dependencies from `requirements.txt`.
3. **Runs Validation** — Executes `python3 scripts/validate_params.py` with your input and schema.
4. **Reports Results** — Displays validation errors in a rich formatted table on failure, or success message on pass.

**Configuration Options:**

```groovy
validateParams(
  input: 'input.json',                    // Path to input parameters JSON (required)
  schema: 'schema.json',                  // Path to schema JSON (required)
  strict: true,                           // Reject unknown parameters (default: true)
  noCoerce: false,                        // Disable type coercion (default: false)
  ensureEnv: true                         // Create venv and install deps (default: true)
)
```

#### Benefits of Using Shared Library

- ✅ **No Checkout Required** — Scripts are extracted from the library, no need to clone the repo
- ✅ **Isolated Environment** — Each pipeline gets a clean `.venv` with dependencies
- ✅ **Automatic Resource Extraction** — Packaged resources bundled with the shared library
- ✅ **Easy Updates** — Update the library version in Jenkins to get new features across all jobs
- ✅ **Reusable** — One configuration, used by many pipelines and teams

### Architecture: Shared Library Resources

The shared library includes a `resources/` folder with all necessary Python files:

```
vars/
  └── validateParams.groovy         # Entry point (Groovy wrapper)
resources/
  ├── scripts/
  │   └── validate_params.py        # Bundled validator script
  ├── requirements.txt              # Bundled dependencies
  └── jenkins_param_validator/      # Bundled Python package
      ├── __init__.py
      ├── engine.py
      ├── coercion.py
      ├── plugins.py
      └── validators.py
```

When `validateParams` is called:
1. It checks if `scripts/validate_params.py` exists locally
2. If not, it extracts from `resources/` using Groovy's `libraryResource()` function
3. Extracted files are written to the workspace
4. Python packages are installed in a virtualenv
5. Validation runs in that isolated environment
Notes:
- The wrapper executes the `scripts/validate_params.py` script from the workspace. Ensure the repo is checked out or that the shared library includes the script.
- Keep Python dependencies available on the Jenkins agent (use a virtualenv or install via `pip3 install -r requirements.txt` in an earlier stage).

### Using the library as `@Library('param-validator') _`

To consume this repository with the exact identifier `param-validator`, configure Jenkins Global Pipeline Libraries:

- Go to **Manage Jenkins → Configure System → Global Pipeline Libraries**
- Add a new library with:
  - **Name:** `param-validator`
  - **Default Version:** the branch or tag you want (e.g., `master`)
  - **Retrieval method / SCM:** point to this Git repository URL

Important: Jenkins Shared Libraries expect a `vars/` directory at the repository root. This repository provides `vars/validateParams.groovy`, so once configured you can reference it directly with `@Library('param-validator') _` in your Jenkinsfiles.

Example Jenkinsfile using `@Library('param-validator')`:

```groovy
@Library('param-validator') _

pipeline {
  agent any

  parameters {
    string(name: 'APP_NAME', defaultValue: 'myapp')
    string(name: 'IMAGE_TAG', defaultValue: 'v1.0.0')
    choice(name: 'ENV', choices: ['dev', 'qa', 'prod'])
    string(name: 'REPLICAS', defaultValue: '2')
  }

  stages {
    stage('Write Parameters JSON') {
      steps {
        script {
          def paramsJson = """
          {
            "APP_NAME": "${params.APP_NAME}",
            "IMAGE_TAG": "${params.IMAGE_TAG}",
            "ENV": "${params.ENV}",
            "REPLICAS": "${params.REPLICAS}"
          }
          """
          writeFile file: 'input.json', text: paramsJson
        }
      }
    }

    stage('Write Validation Schema') {
      steps {
        writeFile file: 'schema.json', text: '''
        {
          "type": "object",
          "properties": {
            "APP_NAME": { "type": "string" },
            "IMAGE_TAG": { "type": "string" },
            "ENV": { "type": "string", "enum": ["dev", "qa", "prod"] },
            "REPLICAS": { "type": "integer", "minimum": 1, "x-coerce": true }
          },
          "required": ["APP_NAME", "IMAGE_TAG", "ENV"],
          "additionalProperties": false
        }
        '''
      }
    }

    stage('Validate Parameters') {
      steps {
        validateParams(
          input: 'input.json',
          schema: 'schema.json',
          strict: true
        )
      }
    }

    stage('Deploy') {
      steps {
        echo "✅ All parameters validated! Deploying..."
      }
    }
  }
}
```

**Important Notes:**
- The wrapper automatically extracts bundled resources and prepares a Python virtualenv.
- No need to checkout this repo or manually install dependencies—the wrapper handles it.
- If validation fails, the pipeline stops and displays errors in a formatted table.
- If validation succeeds, the pipeline continues to the next stage.

```

### 📖 API Reference

`validate_params.py` - CLI Tool
```bash
python3 scripts/validate_params.py [options]
```

#### Options:
```
--input INPUT                 Path to input.json (required)
--schema SCHEMA              Path to schema.json (required)
--no-coerce                  Disable type coercion
--strict                     Reject unknown parameters
--help                       Show help message
```

#### Examples:

```bash
# Basic validation
python3 scripts/validate_params.py --input input.json --schema schema.json

# With strict mode (reject unknown params)
python3 scripts/validate_params.py --input input.json --schema schema.json --strict

# Without type coercion
python3 scripts/validate_params.py --input input.json --schema schema.json --no-coerce
```

`generate_schema.py` - Schema Generator

```bash
Options:
--jenkinsfile PATH           Path to Jenkinsfile (default: Jenkinsfile)
--rules PATH                 Path to schema_rules.yaml (default: scripts/schema_rules.yaml)
--output PATH                Output schema path (default: schemas/deploy-service.schema.json)
--output-stdout              Print schema to stdout instead of file
--help                       Show help message
```

### Examples:

```bash
# Generate with defaults
python3 scripts/generate_schema.py

# Generate with custom rules
python3 scripts/generate_schema.py --rules custom-rules.yaml --output custom-schema.json

# Print to stdout
python3 scripts/generate_schema.py --output-stdout | jq .
```

```python
from jenkins_param_validator.engine import validate_params, ValidationError

try:
    result = validate_params(
        input_file='input.json',
        schema_file='schema.json',
        coerce=True,      # Enable type coercion
        strict=False      # Reject unknown parameters
    )
    print(f"✅ Valid: {result}")
except ValidationError as e:
    print(f"❌ Invalid: {e}")
except Exception as e:
    print(f"💥 Error: {e}")
```

### 🔧 Priority Rules

When Jenkinsfile parameters and `schema_rules.yaml` differ, the framework follows this priority:

#### Priority Order
1. **schema_rules.yaml (Highest)** — Explicit custom rules override everything  
2. **Jenkinsfile** — Parameter definitions used if not in rules  
3. **Auto-generated defaults (Lowest)** — Applied if not defined elsewhere  

### Example with Conflict Resolution

```groovy
// Jenkinsfile
parameters {
    string(name: 'REPLICAS', defaultValue: '2')  // Type: string
}
```

```yaml
# schema_rules.yaml
rules:
  REPLICAS:
    type: integer          # Override: change to integer
    minimum: 1
    maximum: 20
    x-coerce: true         # Auto-convert "2" → 2
```

Result:

Final type: integer (from schema_rules.yaml)  
Coercion: Enabled (from schema_rules.yaml)  
Input: `{"REPLICAS": "2"} ` 
After validation: `{"REPLICAS": 2}` ✅  

No Conflict Case

### 🎓 Complete Workflow
Day 1: Setup

```bash
# 1. Clone repository
git clone https://github.com/vimit12/Jenkins_params_framework.git
cd Jenkins_params_framework

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Create your Jenkinsfile with parameters
# (edit Jenkinsfile)

# 4. Create schema_rules.yaml with custom rules
# (create scripts/schema_rules.yaml)

# 5. Test schema generation locally
python3 scripts/generate_schema.py --output-stdout
```

Day 2: In Jenkins

```groovy
pipeline {
    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('Generate Schema') {
            steps {
                sh 'python3 scripts/generate_schema.py --jenkinsfile Jenkinsfile --output schemas/deploy-service.schema.json'
            }
        }

        stage('Write Params JSON') {
            steps {
                sh '''cat > input.json << 'EOF'
{...parameters...}
EOF'''
            }
        }

        stage('Validate Parameters') {
            steps {
                sh 'python3 scripts/validate_params.py --input input.json --schema schemas/deploy-service.schema.json --strict'
            }
        }

        stage('Deploy') {
            steps {
                echo "Parameters validated! Proceeding..."
            }
        }
    }
}
```

### 🔐 Security Considerations

1. **Credentials Handling**
   - Never log credentials or sensitive parameter values
   - Use Jenkins credentials store for passwords and API keys
   - Validate credentials IDs but don't expose actual values

2. **Parameter Validation**
   - Always validate input patterns strictly
   - Use regex patterns to reject suspicious values
   - Implement email/URL validation for external inputs

3. **Strict Mode**
   - Always enable `--strict` mode in production
   - Prevents injection of unexpected parameters
   - Ensures only declared parameters are accepted

4. **Access Control**
   - Restrict who can trigger builds with parameter validation
   - Audit parameter changes in Jenkins audit logs

### 🔄 Exit Codes

The validation script returns specific exit codes for automation:

```
0  - Validation successful
1  - Validation failed (invalid parameters)
2  - File not found (input or schema)
3  - Configuration error (malformed YAML)
4  - Type coercion failure
5  - Internal error
```

**Usage in Jenkinsfile:**
```groovy
stage('Validate Parameters') {
    steps {
        sh '''
            python3 scripts/validate_params.py \
              --input input.json \
              --schema schemas/deploy-service.schema.json \
              --strict
            
            # Exit code 0 = success, non-zero = failure
            if [ $? -ne 0 ]; then
                echo "❌ Validation failed"
                exit 1
            fi
        '''
    }
}
```

### 🧪 Testing

#### Running Tests Locally

```bash
# Install test dependencies
pip3 install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=jenkins_param_validator

# Run specific test file
pytest tests/test_validators.py -v
```

#### Testing Validation Locally

```bash
# Test schema generation
python3 scripts/generate_schema.py --output-stdout | jq .

# Test parameter validation
python3 scripts/validate_params.py \
  --input tests/fixtures/valid_input.json \
  --schema schemas/deploy-service.schema.json \
  --strict

# Test without coercion
python3 scripts/validate_params.py \
  --input tests/fixtures/input.json \
  --schema schemas/deploy-service.schema.json \
  --no-coerce
```

#### Example Test Cases

```bash
# Valid parameters
echo '{"APP_NAME": "my-app", "ENV": "dev", "IMAGE_TAG": "v1.0"}' > input.json
python3 scripts/validate_params.py --input input.json --schema schemas/deploy-service.schema.json
# Expected: ✅ Valid

# Invalid: Missing required field
echo '{"ENV": "dev", "IMAGE_TAG": "v1.0"}' > input.json
python3 scripts/validate_params.py --input input.json --schema schemas/deploy-service.schema.json
# Expected: ❌ APP_NAME is required

# Invalid: Out of range
echo '{"APP_NAME": "my-app", "ENV": "dev", "IMAGE_TAG": "v1.0", "REPLICAS": "100"}' > input.json
python3 scripts/validate_params.py --input input.json --schema schemas/deploy-service.schema.json
# Expected: ❌ 100 exceeds maximum of 20
```

### 🚨 Troubleshooting

**Issue:** `ModuleNotFoundError: No module named 'jsonschema'`  
**Solution:** Install requirements

```bash
pip3 install -r requirements.txt
```

**Issue:** `No parameters block found in Jenkinsfile`
**Solution:** Ensure your Jenkinsfile has a parameters block:

```groovy
pipeline {
    parameters {
        string(name: 'APP_NAME', defaultValue: 'my-app')
    }
}

```

**Issue:** `Validation passes locally but fails in Jenkins`
**Solution:**  Ensure Jenkins uses the same Python version and dependencies:

```groovy
stage('Install Dependencies') {
    steps {
        sh 'pip3 install -r requirements.txt'
    }
}
```

**Issue:** Schema rules not being applied
**Solution:** Verify `schema_rules.yaml` path and syntax:

```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('scripts/schema_rules.yaml'))"

# Generate with explicit rules path
python3 scripts/generate_schema.py --rules scripts/schema_rules.yaml --output-stdout
```

**Issue:** Coercion not working
**Solution:** Ensure x-coerce: true is set in `schema_rules.yaml`:

```yaml
rules:
  REPLICAS:
    type: integer
    x-coerce: true  # Must be true
```

**Issue:** Type coercion failure error
**Error:** `ValueError: Coercion failed for 'REPLICAS': Cannot coerce '...' to integer`

**Solution:** Check input value is convertible:

```json
// Invalid: Non-numeric string
{"REPLICAS": "abc"}  // ❌

// Valid
{"REPLICAS": "2"}    // ✅
```

### 💡 Best Practices

1. **Always use `schema_rules.yaml`** - Define explicit constraints for clarity  
2. **Keep Jenkinsfile simple** - Use schema_rules for complex validation  
3. **Enable strict mode** - Catch unknown parameters early in production  
4. **Test locally first** - Run validation before committing to repository  
5. **Document custom validators** - Explain business logic in code comments  
6. **Version your schemas** - Track schema changes with code using git  
7. **Use meaningful error messages** - Help developers understand validation failures  
8. **Validate early** - Place validation as first stage in pipeline  
9. **Log validation results** - Keep audit trail of parameter validation  
10. **Keep schemas DRY** - Reuse common patterns and rules  
11. **Test edge cases** - Include boundary values in test cases  
12. **Use type coercion wisely** - Enable only for Jenkins string parameters

### 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository  
2. Create a feature branch  
3. Make your changes  
4. Test thoroughly  
5. Submit a pull request


## License

Vimit