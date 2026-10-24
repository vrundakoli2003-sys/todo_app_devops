pipeline {
    agent { label 'todo-agent' }

    options {
        timestamps()
    }

    environment {
        IMAGE_NAME = 'vrundakoli05/todo-app'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Python Tests') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install -r requirements.txt
                    .venv/bin/python -m pytest -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t "$IMAGE_NAME:$BUILD_NUMBER" .
                    docker image ls "$IMAGE_NAME"
                '''
            }
        }

        stage('Docker Hub Push') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x
                        echo "$DOCKER_TOKEN" | docker login \
                            --username "$DOCKER_USER" \
                            --password-stdin
                        docker push "$IMAGE_NAME:$BUILD_NUMBER"
                        docker logout
                    '''
                }
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'k8s-deploy-ssh',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    sh '''
                        set -eu

                        ssh -i "$SSH_KEY" \
                            -o IdentitiesOnly=yes \
                            -o BatchMode=yes \
                            "$SSH_USER@172.31.5.22" \
                            "kubectl --kubeconfig=/home/k8s-deployer/.kube/config \
                            -n todo-production set image deployment/todo-app \
                            todo-app=$IMAGE_NAME:$BUILD_NUMBER"

                        ssh -i "$SSH_KEY" \
                            -o IdentitiesOnly=yes \
                            -o BatchMode=yes \
                            "$SSH_USER@172.31.5.22" \
                            "kubectl --kubeconfig=/home/k8s-deployer/.kube/config \
                            -n todo-production rollout status \
                            deployment/todo-app --timeout=180s"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check console output.'
        }
    }
}
