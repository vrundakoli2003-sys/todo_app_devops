pipeline {
    agent {
        label 'todo-agent'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'vrundakoli05/todo-app'
        K8S_HOST = '172.31.5.22'
        K8S_NAMESPACE = 'todo-production'
        K8S_DEPLOYMENT = 'todo-app'
        K8S_CONTAINER = 'todo-app'
        KUBECONFIG_PATH = '/home/k8s-deployer/.kube/config'
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
                    set -eu

                    python3 -m venv .venv

                    .venv/bin/python -m pip install \
                        -r requirements.txt

                    .venv/bin/python -m pytest -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    set -eu

                    docker build \
                        -t "$IMAGE_NAME:$BUILD_NUMBER" .

                    docker image inspect \
                        "$IMAGE_NAME:$BUILD_NUMBER"
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
                        set -eu
                        set +x

                        echo "$DOCKER_TOKEN" | \
                            docker login \
                            --username "$DOCKER_USER" \
                            --password-stdin

                        docker push \
                            "$IMAGE_NAME:$BUILD_NUMBER"

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

                        SSH_OPTIONS="-o BatchMode=yes -o IdentitiesOnly=yes"

                        echo "Checking SSH connection..."

                        ssh -i "$SSH_KEY" $SSH_OPTIONS \
                            "$SSH_USER@$K8S_HOST" \
                            "whoami"

                        echo "Updating Kubernetes image..."

                        ssh -i "$SSH_KEY" $SSH_OPTIONS \
                            "$SSH_USER@$K8S_HOST" \
                            "kubectl --kubeconfig=$KUBECONFIG_PATH \
                            -n $K8S_NAMESPACE \
                            set image deployment/$K8S_DEPLOYMENT \
                            $K8S_CONTAINER=$IMAGE_NAME:$BUILD_NUMBER"

                        echo "Waiting for Kubernetes rollout..."

                        ssh -i "$SSH_KEY" $SSH_OPTIONS \
                            "$SSH_USER@$K8S_HOST" \
                            "kubectl --kubeconfig=$KUBECONFIG_PATH \
                            -n $K8S_NAMESPACE \
                            rollout status deployment/$K8S_DEPLOYMENT \
                            --timeout=180s"

                        echo "Checking deployed image..."

                        ssh -i "$SSH_KEY" $SSH_OPTIONS \
                            "$SSH_USER@$K8S_HOST" \
                            "kubectl --kubeconfig=$KUBECONFIG_PATH \
                            -n $K8S_NAMESPACE \
                            get deployment $K8S_DEPLOYMENT \
                            -o wide"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD PIPELINE COMPLETED SUCCESSFULLY!'
            echo "Docker image: ${IMAGE_NAME}:${BUILD_NUMBER}"
        }

        failure {
            echo 'CI/CD PIPELINE FAILED!'
            echo 'Check the failed stage in Jenkins Console Output.'
        }

        always {
            echo "Build number: ${BUILD_NUMBER}"
        }
    }
}
