#!/usr/bin/env bash

set -e

MCV_CORPUS_DIR=${1}

if [[ -z ${MCV_CORPUS_DIR} ]]
then
  echo "I need the path to the cv_corpus_v1/ directory as an argument please!"
  exit
fi

WAV_DIR=${MCV_CORPUS_DIR}
TRANSCRIPTION_FILE=${MCV_CORPUS_DIR}/test.csv

mkdir -p ./samples/mcv7/sentences/all/

# use find as *.wav globs can cause problems
echo "Getting audio files."
find ${WAV_DIR} -type f -name "*.wav" -exec cp -vf {} ./samples/mcv7/sentences/all/ \; \

echo "Getting targets file"
cp -fv ${TRANSCRIPTION_FILE} ./samples/mcv7/sentences/test.csv

echo "Pre-processing audio (normalise, trim) and generating json example files."
python3 ./bin/data/mcv7/preprocess_samples.py ./samples/mcv7/sentences/all/ ./samples/mcv7/sentences/test.csv

# create archive for S3
echo "Archiving."
tar cz -f ./sentences.tar.gz ./samples/mcv7/sentences \
 && rm -rfv ./samples/mcv7/sentences
# upload to s3
echo "Uploading."
aws s3 cp ./sentences.tar.gz s3://cleverspeech-data/mcv7/sentences.tar.gz \
 && echo "Done!"

echo "Cleaning up."
rm -rfv ./sentences.tar.gz \
 && echo "Done!"
