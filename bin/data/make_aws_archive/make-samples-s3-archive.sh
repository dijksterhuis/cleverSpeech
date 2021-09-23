#!/usr/bin/env bash

MCV_CORPUS_DIR=${1}

if [[ -z ${MCV_CORPUS_DIR} ]]
then
  echo "I need the path to the cv_corpus_v1/ directory as an argument please!"
  exit
fi

WAV_DIR=${MCV_CORPUS_DIR}/cv-valid-test/
TRANSCRIPTION_FILE=${MCV_CORPUS_DIR}/cv-valid-test.csv

mkdir -p ./samples/all/

# use find as *.wav globs can cause problems
echo "Getting audio files."
find ${WAV_DIR} -type f -name "*.wav" -exec cp -vf {} ./samples/all \; \

echo "Getting targets file"
cp -fv ${TRANSCRIPTION_FILE} ./samples/

echo "Pre-processing audio (normalise, trim) and generating json example files."
python3 ./bin/data/make_aws_archive/preprocess_samples.py ./samples/all ${TRANSCRIPTION_FILE}

# create archive for S3
echo "Archiving."
tar cz -f ./samples.tar.gz ./samples/ \
    && rm -rfv ./samples/

# upload to s3
echo "Uploading."
aws s3 cp ./samples.tar.gz s3://cleverspeech-data/samples.tar.gz \
    && echo "Done!"

echo "Cleaning up."
rm -rfv ./samples.tar.gz \
    && echo "Done!"
