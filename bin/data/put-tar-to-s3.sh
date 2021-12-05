#!/usr/bin/env bash

set -e

echo """
  This script is for minimal organisation on original mozilla common voice test
  data sets and pushes source data to my own S3 repository. It is not intended
  for use by others.
  """

EXISTING_DATA_DIR=${1}
# e.g. mcv7
DATASET_MAJOR_ID=${2}
# eg. sentences
DATASET_MINOR_ID=${3}

WAV_DIR=${EXISTING_DATA_DIR}
if [[ "${DATASET_MAJOR_ID}" == "mcv7" ]]
then
  TRANSCRIPTION_FILE=${EXISTING_DATA_DIR}/../test.csv
elif [[ "${DATASET_MAJOR_ID}" == "mcv1" ]]
then
  TRANSCRIPTION_FILE=${EXISTING_DATA_DIR}/../cv-valid-test.csv
fi
NEW_TRANSCRIPTION_DIR=./samples/${DATASET_MAJOR_ID}/${DATASET_MINOR_ID}/
NEW_WAV_DIR=${NEW_TRANSCRIPTION_DIR}/all/
ARCHIVE_NAME=${DATASET_MAJOR_ID}-${DATASET_MINOR_ID}.tar.gz

mkdir -p ${NEW_WAV_DIR}

# use find as *.wav globs can cause problems
echo "Getting audio files."
find ${WAV_DIR} -type f -name "*.wav" -exec cp -vf {} ${NEW_WAV_DIR} \; \

echo "Getting targets file"
cp -fv ${TRANSCRIPTION_FILE} ${NEW_TRANSCRIPTION_DIR}/test.csv

echo "Pre-processing audio (normalise, trim) and generating json example files."
python3 ./bin/data/${DATASET_MAJOR_ID}/preprocess_samples.py \
  ${NEW_WAV_DIR} ${NEW_TRANSCRIPTION_DIR}/test.csv

# create archive for S3
echo "Archiving."
tar cz -f ./${ARCHIVE_NAME} ${NEW_TRANSCRIPTION_DIR} \
 && rm -rfv ${NEW_TRANSCRIPTION_DIR}
# upload to s3
echo "Uploading."
aws s3 cp ./${ARCHIVE_NAME} s3://cleverspeech-data/${ARCHIVE_NAME} \
 && echo "Done!"

echo "Cleaning up."
rm -rfv ./${ARCHIVE_NAME} \
 && echo "Done!"
