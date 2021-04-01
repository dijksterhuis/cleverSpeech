#!/usr/bin/env bash

export MCV_CORPUS_DIR=${1}

if [[ -z ${MCV_CORPUS_DIR} ]]
then
  echo "I need the path to the cv_corpus_v1/ directory as an argument please!"
  exit
fi

mkdir -p ./silence/all

echo "Create silence files."
python3 ./bin/mcv/make_aws_archive/make_silence.py ./silence/all

echo "Getting targets file"
cp -fv ${MCV_CORPUS_DIR}/cv-valid-test.csv ./silence/

# create archive for S3
echo "Archiving."
tar cz -f ./silence.tar.gz ./silence/ \
    && rm -rf ./silence/

# upload to s3
echo "Uploading."
aws s3 cp ./silence.tar.gz s3://cleverspeech-data/silence.tar.gz
echo "Done!"
