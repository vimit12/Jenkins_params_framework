pipeline {
    agent any

    parameters {
        string(name: 'APP_NAME', defaultValue: 'my-api', description: 'App name')
        string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Image tag')
        choice(name: 'ENV', choices: ['dev', 'qa', 'staging', 'prod'], description: 'Environment')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run tests before deploy')
        string(name: 'REPLICAS', defaultValue: '2', description: 'Number of replicas')
        string(name: 'CPU_LIMIT', defaultValue: '500m', description: 'CPU limit')
        string(name: 'MEMORY_LIMIT', defaultValue: '512Mi', description: 'Memory limit')
        booleanParam(name: 'ALLOW_PROD_DEPLOY', defaultValue: false, description: 'Allow prod deploy')
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

        stage('Write Params JSON') {
            steps {
                sh """
                    cat > input.json << 'EOF'
{
  "APP_NAME": "${params.APP_NAME}",
  "IMAGE_TAG": "${params.IMAGE_TAG}",
  "ENV": "${params.ENV}",
  "RUN_TESTS": "${params.RUN_TESTS}",
  "REPLICAS": "${params.REPLICAS}",
  "CPU_LIMIT": "${params.CPU_LIMIT}",
  "MEMORY_LIMIT": "${params.MEMORY_LIMIT}",
  "ALLOW_PROD_DEPLOY": "${params.ALLOW_PROD_DEPLOY}"
}
EOF
                """
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
            steps {
                echo "All params valid. Proceeding with build & deploy..."
                // your usual logic here
            }
        }
    }
}