#!/usr/bin/env bash

export DS_VERSION="0.9.3"
DS_RELEASE_URL="https://github.com/mozilla/DeepSpeech/releases/download/v${DS_VERSION}"
BASE_PATH=$(pwd)
OUTPUT_PATH="${BASE_PATH}/cleverspeech/models/DeepSpeech_v0_9_3/src/data/"


if [[ $(basename ${BASE_PATH}) != "cleverSpeech" ]]
then
    echo "Script must be run from the root of the cleverSpeech directory."
    echo "Like so: ./bin/deepspeech/get-v093-model-files.sh"
    echo "You are currently in $(pwd)"
    echo "Quitting. "
    exit
fi


DS_CHECKPOINT_FILE="deepspeech-${DS_VERSION}-checkpoint.tar.gz"
DS_SCORER_FILE="deepspeech-${DS_VERSION}-models.scorer"

DS_CHECKPOINT_URL="${DS_RELEASE_URL}/${DS_CHECKPOINT_FILE}"
DS_MODEL_DATA_URL="${DS_RELEASE_URL}/${DS_SCORER_FILE}"

echo "Getting checkpoint file."
mkdir -p ${OUTPUT_PATH} && cd ${OUTPUT_PATH}
wget --no-verbose ${DS_CHECKPOINT_URL}
echo "Getting scorer file."
wget --no-verbose ${DS_MODEL_DATA_URL}

echo "Extracting."
cd ${OUTPUT_PATH}
tar xvfz ./${DS_CHECKPOINT_FILE}
mkdir ./models && mv -v ./${DS_SCORER_FILE} ./models/
cp -fv ./cleverspeech/models/DeepSpeech_v0_9_3/src/data/alphabet.txt ./models/

echo "Removing archives."
rm -f ./${DS_CHECKPOINT_FILE}

cd ${BASE_PATH}