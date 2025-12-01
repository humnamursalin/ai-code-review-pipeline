pipeline {
    agent any

    environment {
        SLACK_WEBHOOK_URL = credentials('slack-webhook')
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/humnamursalin/ai-code-review-pipeline.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv --without-pip venv
                    . venv/bin/activate
                    curl -sS https://bootstrap.pypa.io/get-pip.py | python3
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest -q
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ai-demo-app:latest .'
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                    docker stop ai-app || true
                    docker rm ai-app || true
                    docker run -d --name ai-app -p 5000:5000 ai-demo-app:latest
                '''
            }
        }

        stage('E2E Tests with Cypress') {
            steps {
                sh '''
                    npm install
                    # Wait for the app to be ready
                    sleep 5
                    npx cypress run
                '''
            }
        }

        stage('Slack Notification') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 -c "from ai_review.utils import send_slack_message; send_slack_message('✅ Pipeline Success — E2E Tests + Deployment Completed')"
                '''
            }
        }
    }

    post {
        failure {
            sh '''
                . venv/bin/activate
                python3 -c "from ai_review.utils import send_slack_message; send_slack_message('❌ Pipeline Failed. Check Jenkins logs.')"
            '''
        }
        always {
            sh '''
                docker stop ai-app || true
                docker rm ai-app || true
            '''
        }
    }
}
