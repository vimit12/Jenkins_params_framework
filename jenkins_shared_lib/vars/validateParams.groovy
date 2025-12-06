// Jenkins shared library wrapper to run the Python validator from workspace
// Usage from a Jenkinsfile when this repo is added as a Shared Library or checked out in the workspace:
// validateParams(input: 'input.json', schema: 'schemas/deploy-service.schema.json', strict: true)

def call(Map config = [:]) {
    def inputFile = config.get('input', 'input.json')
    def schemaFile = config.get('schema', env.PARAM_SCHEMA ?: 'schemas/deploy-service.schema.json')
    def strictFlag = config.get('strict', true) ? '--strict' : ''
    def noCoerceFlag = config.get('noCoerce', false) ? '--no-coerce' : ''

    // Execute the bundled validation script inside the workspace
    sh label: 'Run parameter validation', script: """
        if [ -f scripts/validate_params.py ]; then
            python3 scripts/validate_params.py --input ${inputFile} --schema ${schemaFile} ${noCoerceFlag} ${strictFlag}
        else
            echo 'ERROR: scripts/validate_params.py not found in workspace.'
            exit 2
        fi
    """
}
