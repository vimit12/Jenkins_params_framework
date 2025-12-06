// Top-level wrapper that makes this repository usable as a Jenkins Shared Library
// when referenced with: @Library('param-validator') _
// This file delegates to the script in the workspace or the bundled implementation.

def call(Map config = [:]) {
    // Delegate to the workspace script we included under jenkins_shared_lib/vars
    // If this repository is used as a Shared Library, files under 'vars/' are automatically
    // available. We keep logic minimal here to run the bundled Python validator.

    def inputFile = config.get('input', 'input.json')
    def schemaFile = config.get('schema', env.PARAM_SCHEMA ?: 'schemas/deploy-service.schema.json')
    def strictFlag = config.get('strict', true) ? '--strict' : ''
    def noCoerceFlag = config.get('noCoerce', false) ? '--no-coerce' : ''

    // If the Python script isn't present in the workspace, attempt to extract packaged resources
    if (!fileExists('scripts/validate_params.py')) {
        echo "scripts/validate_params.py not found — extracting bundled resources from shared library"
        sh 'mkdir -p scripts jenkins_param_validator'
        try {
            writeFile file: 'scripts/validate_params.py', text: libraryResource('scripts/validate_params.py')
            writeFile file: 'jenkins_param_validator/__init__.py', text: libraryResource('jenkins_param_validator/__init__.py')
            writeFile file: 'jenkins_param_validator/engine.py', text: libraryResource('jenkins_param_validator/engine.py')
            writeFile file: 'jenkins_param_validator/coercion.py', text: libraryResource('jenkins_param_validator/coercion.py')
            writeFile file: 'jenkins_param_validator/plugins.py', text: libraryResource('jenkins_param_validator/plugins.py')
            writeFile file: 'jenkins_param_validator/validators.py', text: libraryResource('jenkins_param_validator/validators.py')
            writeFile file: 'requirements.txt', text: libraryResource('requirements.txt')
            sh 'chmod +x scripts/validate_params.py || true'
        } catch (Exception e) {
            echo "ERROR: failed to extract resources: ${e}"
            error "Shared library resources missing"
        }
    }

    def ensureEnv = config.get('ensureEnv', true)

    if (ensureEnv) {
        sh label: 'Prepare python venv and install deps', script: """
            if [ ! -d .venv ]; then
                python3 -m venv .venv
                . .venv/bin/activate
                python3 -m pip install --upgrade pip
                pip install -r requirements.txt
            fi
            . .venv/bin/activate
            .venv/bin/python3 scripts/validate_params.py --input ${inputFile} --schema ${schemaFile} ${noCoerceFlag} ${strictFlag}
        """
    } else {
        sh label: 'Run parameter validation', script: """
            python3 scripts/validate_params.py --input ${inputFile} --schema ${schemaFile} ${noCoerceFlag} ${strictFlag}
        """
    }
}
