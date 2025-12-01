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

        stage('E2E Tests with Cypress') {
            steps {
                sh '''
                    . venv/bin/activate
                    npm install
                    # Start Flask app in background
                    python app/simple_app.py &
                    FLASK_PID=$!
                    # Wait for the app to be ready
                    sleep 3
                    # Run Cypress tests
                    npx cypress run || EXIT_CODE=$?
                    # Stop Flask app
                    kill $FLASK_PID || true
                    exit ${EXIT_CODE:-0}
                '''
            }
        }

        stage('Slack Notification') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 -c "from ai_review.utils import send_slack_message; send_slack_message('✅ Pipeline Success — E2E Tests Completed')"
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
                # Clean up any running Flask processes
                pkill -f "python.*simple_app.py" || true
            '''
        }
    }
}
