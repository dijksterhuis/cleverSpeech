#!/usr/bin/env bash

export DS_VERSION="0.9.3"
DS_RELEASE_URL="https://github.com/mozilla/DeepSpeech/releases/download/v${DS_VERSION}"
BASE_PATH=$(pwd)

DS_BASE_DIR="${BASE_PATH}/cleverspeech/models/__DeepSpeech_v0_9_3"
DS_SRC_DIR="${DS_BASE_DIR}/src"
DS_DATA_DIR="${DS_BASE_DIR}/data"


if [[ $(basename ${BASE_PATH}) != "cleverSpeech" ]]
then
    echo "Script must be run from the root of the cleverSpeech directory."
    echo "Like so: ./bin/deepspeech/get-v093-model-files.sh"
    echo "You are currently in $(pwd)"
    echo "Quitting. "
    exit
fi


DS_CHECKPOINT_DIR="deepspeech-${DS_VERSION}-checkpoint"
DS_CHECKPOINT_FILE="${DS_CHECKPOINT_DIR}.tar.gz"
DS_SCORER_FILE="deepspeech-${DS_VERSION}-models.scorer"

DS_CHECKPOINT_URL="${DS_RELEASE_URL}/${DS_CHECKPOINT_FILE}"
DS_MODEL_DATA_URL="${DS_RELEASE_URL}/${DS_SCORER_FILE}"

mkdir -p ${DS_DATA_DIR} ${DS_DATA_DIR}/models

echo "Getting scorer file."
wget --no-verbose ${DS_MODEL_DATA_URL}

echo "Moving scorer and alphabet files."
mv -v ./${DS_SCORER_FILE} ${DS_DATA_DIR}/models
cp -fv ${DS_SRC_DIR}/data/alphabet.txt ${DS_DATA_DIR}/models/

echo "Getting checkpoint file."
wget --no-verbose ${DS_CHECKPOINT_URL}

echo "Extracting checkpoint."
tar xvfz ./${DS_CHECKPOINT_FILE}
mv -v ./${DS_CHECKPOINT_DIR}/ ${DS_DATA_DIR}/

echo "Removing archive."
rm -f ./${DS_CHECKPOINT_FILE}
