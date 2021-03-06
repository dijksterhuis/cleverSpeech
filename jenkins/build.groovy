pipeline {

    /* run on a gpu machine because the build machine (rhea) has low root disk space */
    agent { label 'cpu' }

    environment {
        BASE_IMAGE = "tensorflow/tensorflow:1.13.1-gpu-py3"
        IMAGE_NAME = "dijksterhuis/cleverspeech"
        GITHUB_BRANCH = "master"
        BUILD_TAG = "latest"
        OUTPUT_IMAGE = "${IMAGE_NAME}:${BUILD_TAG}"
    }
    options {
        timestamps()
        disableResume()
        disableConcurrentBuilds()
    }
    triggers {
        pollSCM('@weekly')
    }
    stages {

        stage('Clean up before we start.') {
            steps {
                lock("docker cleanup") {
                    sh "docker container prune -f"
                    sh "docker image prune -f"
                    sh "docker builder prune -f"
                }
            }
        }

        stage('Checkout vcs.') {
            steps {
                git branch: "${GITHUB_BRANCH}", credentialsId: 'git-mr', url: 'https://github.com/dijksterhuis/cleverSpeech.git'
            }
        }

        stage("Pull tensorflow image.") {
            steps {
                script {
                    withDockerRegistry([ credentialsId: "dhub-mr", url: "" ]) {
                        sh "docker pull ${BASE_IMAGE}"
                    }
                }
            }
        }

        stage("Build base image.") {
            steps {
                script {

                    sh """
                        DOCKER_BUILDKIT=1 docker build \
                        -t ${OUTPUT_IMAGE} \
                        -f ./docker/Dockerfile.build \
                        --pull \
                        --force-rm \
                        --no-cache \
                        .

                    docker tag \
                        ${IMAGE_NAME}:${BUILD_TAG} \
                        ${IMAGE_NAME}:${GIT_COMMIT}

                    """
                }
            }
        }

        stage("Push images.") {
            steps {
                script {
                    withDockerRegistry([ credentialsId: "dhub-mr", url: "" ]) {
                        sh "echo 'pushing latest' && docker push ${IMAGE_NAME}:${BUILD_TAG}"
                        sh "echo 'pushin git commit hash' && docker push ${IMAGE_NAME}:${GIT_COMMIT}"
                    }
                }
            }
        }
    }
    post  {
        always {
            lock("docker cleanup") {
                sh "docker container prune -f"
                sh "docker image prune -f"
                sh "docker builder prune -f"
                sh "docker image rm ${OUTPUT_IMAGE}"
            }
        }
    }
}