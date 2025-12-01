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

        stage('Install xvfb') {
            steps {
                sh '''#!/bin/bash
                    # Check if xvfb is already installed
                    if command -v xvfb-run &> /dev/null || command -v Xvfb &> /dev/null; then
                        echo "xvfb is already installed."
                    else
                        echo "xvfb not found. Attempting to install..."
                        # Try to install without sudo first (in case user has permissions)
                        apt-get update -qq 2>/dev/null && apt-get install -y xvfb 2>/dev/null || {
                            echo "=========================================="
                            echo "ERROR: Could not install xvfb."
                            echo "=========================================="
                            echo "Please install xvfb on the Jenkins agent:"
                            echo "  sudo apt-get update"
                            echo "  sudo apt-get install -y xvfb"
                            echo "=========================================="
                            exit 1
                        }
                        echo "xvfb installed successfully."
                    fi
                '''
            }
        }

        stage('Install Node.js and Cypress') {
            steps {
                sh '''#!/bin/bash
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
                    
                    # Run Cypress tests with xvfb-run
                    if command -v xvfb-run &> /dev/null; then
                        echo "Running Cypress with xvfb-run..."
                        xvfb-run -a npx cypress run --headless --browser electron
                    else
                        echo "ERROR: xvfb-run not found. Please install xvfb."
                        exit 1
                    fi
                    
                    # Stop Flask app
                    kill $FLASK_PID || true
                '''
            }
        }

        stage('Slack Notification') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 -c "from ai_review.utils import send_slack_message; send_slack_message('✅ Pipeline Success — Tests Completed')"
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
