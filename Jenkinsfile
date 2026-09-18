pipeline {
    agent any

    environment {
        TEST_COMPANY_ID = '2'
        TEST_TIMEOUT = '15'
    }

    stages {
        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv-ci
                    .venv-ci/bin/python -m pip install --upgrade pip
                    .venv-ci/bin/python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run tests') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'req-test-account',
                        usernameVariable: 'TEST_USERNAME',
                        passwordVariable: 'TEST_PASSWORD'
                    ),
                    string(
                        credentialsId: 'req-base-url',
                        variable: 'BASE_URL'
                    )
                ]) {
                    sh '''
                        .venv-ci/bin/python -m pytest -v
                    '''
                }
            }
        }
    }

    post {
        always {
            allure([
                includeProperties: false,
                jdk: '',
                results: [[path: 'allure-results']]
            ])
        }
    }
}