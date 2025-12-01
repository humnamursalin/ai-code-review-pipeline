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

        stage('Install Node.js and Cypress') {
            steps {
                sh '''#!/bin/bash
                    # Check for Xvfb (required for Cypress headless mode on Linux)
                    if ! command -v xvfb-run &> /dev/null && ! command -v Xvfb &> /dev/null; then
                        echo "WARNING: Xvfb not found. Cypress requires Xvfb to run headless on Linux."
                        echo "Please install Xvfb on the Jenkins agent: apt-get install xvfb"
                        echo "Continuing with installation, but E2E tests may fail..."
                    fi
                    # Install nvm (Node Version Manager) - doesn't require sudo
                    export NVM_DIR="$HOME/.nvm"
                    [ -s "$NVM_DIR/nvm.sh" ] || curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
                    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
                    # Install and use Node.js LTS
                    nvm install --lts
                    nvm use --lts
                    # Verify installation
                    node --version
                    npm --version
                    # Install Cypress dependencies
                    npm install
                '''
            }
        }

        stage('E2E Tests with Cypress') {
            steps {
                sh '''#!/bin/bash
                    . venv/bin/activate
                    # Load nvm
                    export NVM_DIR="$HOME/.nvm"
                    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
                    nvm use --lts
                    # Start Flask app in background
                    python app/simple_app.py &
                    FLASK_PID=$!
                    # Wait for the app to be ready
                    sleep 3
                    # Run Cypress tests with xvfb-run if available
                    if command -v xvfb-run &> /dev/null; then
                        echo "Running Cypress with xvfb-run..."
                        xvfb-run -a npx cypress run || EXIT_CODE=$?
                    elif command -v Xvfb &> /dev/null; then
                        echo "Starting Xvfb manually..."
                        export DISPLAY=:99
                        Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
                        XVFB_PID=$!
                        sleep 2
                        npx cypress run || EXIT_CODE=$?
                        kill $XVFB_PID 2>/dev/null || true
                    else
                        echo "ERROR: Xvfb is required but not found. Please install it on the Jenkins agent."
                        echo "Install with: sudo apt-get install xvfb"
                        EXIT_CODE=1
                    fi
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
