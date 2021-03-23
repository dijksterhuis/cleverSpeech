pipeline {
    agent any
    environment {
        IMAGE_NAME = "dijksterhuis/cleverspeech"
        BUILD_TAG = "build"
        BRANCH = "master"
        TAG = "latest"
    }

    stages {

        stage('Clean up before we start.') {
            steps {
                sh "docker image prune -f"
                sh "docker container prune -f"
                sh "docker builder prune -f"
            }
        }

        stage('Checkout vcs.') {
            steps {
                git branch: "${BRANCH}", credentialsId: 'git-mr', url: 'https://github.com/dijksterhuis/cleverSpeech.git'
            }
        }

        stage("Build release images.") {
            steps {
                script {

                    sh """
                        DOCKER_BUILDKIT=1 docker build \
                        -t ${IMAGE_NAME}:${TAG} \
                        -f ./docker/Dockerfile.latest \
                        --force-rm \
                        --no-cache \
                        .

                    """
                }
            }
        }

        stage("Push images.") {
            steps {
                script {
                    withDockerRegistry([ credentialsId: "dhub-mr", url: "" ]) {
                        sh "docker push ${IMAGE_NAME}:${TAG}"
                    }
                }
            }
        }
    }
    post  {
        always {
            sh "docker image prune -f"
            sh "docker container prune -f"
            sh "docker builder prune -f"
            sh "docker image rm ${IMAGE_NAME}:${BUILD_TAG}"
            sh "docker image rm ${IMAGE_NAME}:${TAG}"
        }
    }
}