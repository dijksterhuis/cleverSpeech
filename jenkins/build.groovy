pipeline {

    /* run on a gpu machine because the build machine (rhea) has low root disk space */
    agent { label 'gpu' }

    environment {
        BASE_IMAGE = "tensorflow/tensorflow:1.13.1-gpu-py3"
        IMAGE_NAME = "dijksterhuis/cleverspeech"
        GITHUB_BRANCH = "master"
        BUILD_TAG = "build"
        OUTPUT_IMAGE = "${IMAGE_NAME}:${BUILD_TAG}"
    }

    stages {

        stage('Clean up before we start.') {
            steps {
                sh "docker container prune -f"
                sh "docker image prune -f"
                sh "docker builder prune -f"
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
                        sh "docker push ${OUTPUT_IMAGE}"
                    }
                }
            }
        }
    }
    post  {
        always {
            sh "docker container prune -f"
            sh "docker image prune -f"
            sh "docker builder prune -f"
            sh "docker image rm ${OUTPUT_IMAGE}"
        }
    }
}