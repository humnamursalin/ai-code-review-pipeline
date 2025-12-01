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

        stage('Install Cypress System Dependencies') {
            steps {
                sh '''#!/bin/bash
                    # Check and install Cypress system dependencies for Linux
                    # Try to detect Ubuntu/Debian version
                    if [ -f /etc/os-release ]; then
                        . /etc/os-release
                        OS=$ID
                        VERSION=$VERSION_ID
                    else
                        OS="unknown"
                    fi
                    
                    echo "Detected OS: $OS, Version: $VERSION"
                    
                    # Check if dependencies are already installed
                    MISSING_DEPS=""
                    for dep in libgtk-3-0 libgbm-dev libnotify-dev libnss3 libxss1 libasound2 libxtst6 xauth xvfb; do
                        if ! dpkg -l | grep -q "^ii  $dep"; then
                            MISSING_DEPS="$MISSING_DEPS $dep"
                        fi
                    done
                    
                    if [ -n "$MISSING_DEPS" ]; then
                        echo "Missing Cypress dependencies:$MISSING_DEPS"
                        echo "Attempting to install..."
                        # Try to install without sudo first (in case user has permissions)
                        apt-get update -qq 2>/dev/null && apt-get install -y $MISSING_DEPS 2>/dev/null || {
                            echo "=========================================="
                            echo "ERROR: Could not install Cypress dependencies."
                            echo "=========================================="
                            echo "Cypress requires the following system packages:"
                            echo "  libgtk-3-0 libgbm-dev libnotify-dev libnss3 libxss1 libasound2 libxtst6 xauth xvfb"
                            echo ""
                            echo "Please install them on the Jenkins agent:"
                            echo "  sudo apt-get update"
                            echo "  sudo apt-get install -y libgtk-3-0 libgbm-dev libnotify-dev libnss3 libxss1 libasound2 libxtst6 xauth xvfb"
                            echo "=========================================="
                            exit 1
                        }
                    else
                        echo "All Cypress system dependencies are installed."
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
                    
                    # Run Cypress tests in Electron headless mode (no Xvfb required)
                    echo "Running Cypress in Electron headless mode..."
                    npx cypress run --headless --browser electron
                    
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
