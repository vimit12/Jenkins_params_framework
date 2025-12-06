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

    sh label: 'Run parameter validation', script: """
        if [ -f scripts/validate_params.py ]; then
            python3 scripts/validate_params.py --input ${inputFile} --schema ${schemaFile} ${noCoerceFlag} ${strictFlag}
        else
            echo 'ERROR: scripts/validate_params.py not found in workspace.'
            exit 2
        fi
    """
}
