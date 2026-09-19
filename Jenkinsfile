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

        success {
            withCredentials([
                string(
                    credentialsId: 'feishu-webhook',
                    variable: 'FEISHU_WEBHOOK'
                )
            ]) {
                sh '''
                    curl -fsS -X POST "$FEISHU_WEBHOOK" \\
                        -H "Content-Type: application/json" \\
                        -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"Jenkins 自动化测试成功\\n项目：$JOB_NAME\\n构建：#$BUILD_NUMBER\\n详情：$BUILD_URL\"}}" \\
                        || echo "飞书成功通知发送失败，但不影响构建结果"
                '''
            }
        }

        failure {
            withCredentials([
                string(
                    credentialsId: 'feishu-webhook',
                    variable: 'FEISHU_WEBHOOK'
                )
            ]) {
                sh '''
                    curl -fsS -X POST "$FEISHU_WEBHOOK" \\
                        -H "Content-Type: application/json" \\
                        -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"Jenkins 自动化测试失败\\n项目：$JOB_NAME\\n构建：#$BUILD_NUMBER\\n详情：$BUILD_URL\"}}" \\
                        || echo "飞书失败通知发送失败"
                '''
            }
        }
    }
}
