pipeline {
    agent any

    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
        SLACK_WEBHOOK_URL = credentials('slack-webhook')
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/YOUR_USERNAME/ai-code-review-pipeline.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python3 -m pip install --upgrade pip'
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('AI Code Review') {
            steps {
                sh 'python3 ai_review/code_review.py'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest -q'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ai-demo-app:latest .'
            }
        }

        stage('Deploy Container') {
            steps {
                sh 'docker stop ai-app || true'
                sh 'docker rm ai-app || true'
                sh 'docker run -d --name ai-app -p 5000:5000 ai-demo-app:latest'
            }
        }

        stage('Slack Notification') {
            steps {
                sh 'python3 -c "from ai_review.utils import send_slack_message; send_slack_message(\\"Pipeline Success — AI Review + Deployment Completed\\")"'
            }
        }
    }

    post {
        failure {
            sh 'python3 -c "from ai_review.utils import send_slack_message; send_slack_message(\\"❌ Pipeline Failed. Check Jenkins logs.\\")"'
        }
    }
}
