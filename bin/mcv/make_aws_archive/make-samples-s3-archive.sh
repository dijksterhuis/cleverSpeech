#!/usr/bin/env bash

MCV_CORPUS_DIR=${1}

if [[ -z ${MCV_CORPUS_DIR} ]]
then
  echo "I need the path to the cv_corpus_v1/ directory as an argument please!"
  exit
fi

mkdir ./samples/

# use find as *.wav globs can cause problems
echo "Getting audio files."
find ${MCV_CORPUS_DIR}/cv-valid-test/ -type f -name "*.wav" -exec cp -vf {} ./samples/ \; \

echo "Pre-processing files (normalise + trim)."
python3 ./bin/mcv/preprocess_samples.py ./samples/

echo "Getting targets file"
cp -fv ${MCV_CORPUS_DIR}/cv-valid-test.csv ./samples/

# create archive for S3
echo "Archiving."
tar cz -f ./samples.tar.gz ./samples/ \
    && rm -rf ./samples/

# upload to s3
echo "Uploading."
aws s3 cp ./samples.tar.gz s3://cleverspeech-data/samples.tar.gz
echo "Done!"