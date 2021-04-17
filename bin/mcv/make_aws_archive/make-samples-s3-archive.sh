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
python3 ./bin/mcv/make_aws_archive/preprocess_samples.py ./samples/all/ ${TRANSCRIPTION_FILE}

# create some additional data sets for running tests on the code
echo "copying 10 files" \
    && mkdir -p ./samples/10 \
    && cp -fv ./samples/all/sample-00000?.* ./samples/10

echo "copying 100 files" \
    && mkdir -p ./samples/100 \
    && cp -fv ./samples/all/sample-0000??.* ./samples/100

echo "copying 1000 files" \
    && mkdir -p ./samples/1000 \
    && cp -fv ./samples/all/sample-000???.* ./samples/1000

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
