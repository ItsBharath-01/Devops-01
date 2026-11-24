pipeline {
    agent any

    // Automated trigger on SCM polling every 5 minutes and compatible with GitHub Webhooks
    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        APP_NAME = 'customer-service-complaint-management-system'
        BUILD_VERSION = "${BUILD_NUMBER}"
        ARTIFACT_NAME = "customer-service-${BUILD_NUMBER}.tar.gz"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo '=== Stage 1: Checking out source code from Git repository ==='
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '=== Stage 2: Setting up virtual environment and installing dependencies ==='
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv venv || python -m venv venv
                            . venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    } else {
                        bat '''
                            python -m venv venv
                            call venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Automated Pytest Suite (CI Enhancement)') {
            steps {
                echo '=== Stage 3: Running automated unit tests and generating JUnit test report ==='
                script {
                    if (isUnix()) {
                        sh '''
                            . venv/bin/activate
                            mkdir -p test-results
                           export PYTHONPATH="$WORKSPACE"
python -m pytest tests/test_app.py --junitxml=test-results/results.xml -v
                        '''
                    } else {
                        bat '''
                            call venv\\Scripts\\activate.bat
                            if not exist test-results mkdir test-results
export PYTHONPATH="$WORKSPACE"
python -m pytest tests/test_app.py --junitxml=test-results/results.xml -v                        '''
                    }
                }
            }
            post {
                always {
                    // Record test results for Jenkins UI dashboard and trend reports
                    junit testResults: 'test-results/results.xml', allowEmptyResults: true
                }
            }
        }

        stage('Package Application') {
            steps {
                echo '=== Stage 4: Packaging application into tar.gz artifact ==='
                script {
                    if (isUnix()) {
                        sh """
                            mkdir -p dist
                            tar --exclude='./venv' \
                                --exclude='./.git' \
                                --exclude='./__pycache__' \
                                --exclude='./tests/__pycache__' \
                                --exclude='./.pytest_cache' \
                                --exclude='./test-results' \
                                --exclude='./dist' \
                                -czvf dist/${ARTIFACT_NAME} \
                                app.py run.py requirements.txt tests/
                        """
                    } else {
                        bat """
                            if not exist dist mkdir dist
                            tar --exclude="venv" --exclude=".git" --exclude="__pycache__" --exclude=".pytest_cache" --exclude="test-results" --exclude="dist" -czvf dist/%ARTIFACT_NAME% app.py run.py requirements.txt tests
                        """
                    }
                }
            }
        }

        stage('Archive Artifacts') {
            steps {
                echo '=== Stage 5: Archiving packaged artifact for deployment ==='
                archiveArtifacts artifacts: 'dist/*.tar.gz', fingerprint: true
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded! Application packaged and archived: dist/${ARTIFACT_NAME}"
        }
        failure {
            echo 'Pipeline failed! Please check console output and test results.'
        }
    }
}
