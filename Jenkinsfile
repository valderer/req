pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        TEST_COMPANY_ID = '2'
        TEST_TIMEOUT = '15'
    }

    stages {
        stage('Checkout') {
            steps {
                retry(3) {
                    checkout scm
                }
            }
        }

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
                        mkdir -p reports
                        .venv-ci/bin/python -m pytest -v \\
                            --junitxml=reports/junit.xml
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('allure-results')) {
                    allure([
                        includeProperties: false,
                        jdk: '',
                        results: [[path: 'allure-results']]
                    ])
                } else {
                    echo '没有找到 allure-results，跳过 Allure 报告发布'
                }
                junit(
                    allowEmptyResults: true,
                    testResults: 'reports/junit.xml'
                )
            }
        }

        success {
            script {
                withCredentials([
                    string(
                        credentialsId: 'feishu-webhook',
                        variable: 'FEISHU_WEBHOOK'
                    )
                ]) {
                    sh '''
                        FEISHU_STATUS=success \\
                        python3 scripts/send_feishu.py
                    '''
                }
            }
        }

        failure {
            script {
                withCredentials([
                    string(
                        credentialsId: 'feishu-webhook',
                        variable: 'FEISHU_WEBHOOK'
                    )
                ]) {
                    sh '''
                        FEISHU_STATUS=failure \\
                        python3 scripts/send_feishu.py
                    '''
                }
            }
        }
    }
}
