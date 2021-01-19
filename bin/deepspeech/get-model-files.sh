#!/usr/bin/env bash

export DS_VERSION="0.4.1"
DS_RELEASE_URL="https://github.com/mozilla/DeepSpeech/releases/download/v${DS_VERSION}"
BASE_PATH=$(pwd)
OUTPUT_PATH="${BASE_PATH}/models/DeepSpeech/data/"


if [[ $(basename ${BASE_PATH}) != "cleverSpeech" ]]
then
    echo "Script must be run from the root of the cleverSpeech directory."
    echo "Like so: ./bin/deepspeech/get-model-files.sh"
    echo "You are currently in $(pwd)"
    echo "Quitting. "
    exit
fi


DS_CHECKPOINT_FILE="deepspeech-${DS_VERSION}-checkpoint.tar.gz"
DS_MODEL_FILE="deepspeech-${DS_VERSION}-models.tar.gz"
DS_CHECKPOINT_URL="${DS_RELEASE_URL}/${DS_CHECKPOINT_FILE}"
DS_MODEL_DATA_URL="${DS_RELEASE_URL}/${DS_MODEL_FILE}"

echo "Getting checkpoint file."
mkdir -p ${OUTPUT_PATH}
wget ${DS_CHECKPOINT_URL} -O ${OUTPUT_PATH}/${DS_CHECKPOINT_FILE}
echo "Getting model data file."
wget ${DS_MODEL_DATA_URL} -O ${OUTPUT_PATH}/${DS_MODEL_FILE}

echo "Extracting files."
cd ${OUTPUT_PATH}
tar xvfz ./${DS_CHECKPOINT_FILE}
tar xvfz ./${DS_MODEL_FILE}

echo "Removing archives."
rm -f ./${DS_CHECKPOINT_FILE}
rm -f ./${DS_MODEL_FILE}


cd ${BASE_PATH}