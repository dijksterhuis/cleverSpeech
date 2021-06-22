#!/usr/bin/env bash

export MCV_CORPUS_DIR=${1}

if [[ -z ${MCV_CORPUS_DIR} ]]
then
  echo "I need the path to the cv_corpus_v1/ directory as an argument please!"
  exit
fi

mkdir -p ./reference-signals/sines/sine \
    ./reference-signals/sines/additive \
    ./reference-signals/sines/am \
    ./reference-signals/sines/fm \
    ./reference-signals/noise/uniform

echo "Creating basic sine files."
python3 ./bin/data/make_aws_archive/reference-signals/make_sine_tones.py ./reference-signals/sines/sine

echo "Creating additive sine files."
python3 ./bin/data/make_aws_archive/reference-signals/make_additive_sine_tones.py ./reference-signals/sines/additive

echo "Creating am sine files."
python3 ./bin/data/make_aws_archive/reference-signals/make_am_sine_tones.py ./reference-signals/sines/am

echo "Creating fm sine files."
python3 ./bin/data/make_aws_archive/reference-signals/make_fm_sine_tones.py ./reference-signals/sines/fm

echo "Creating uniform noise files."
python3 ./bin/data/make_aws_archive/reference-signals/make_uniform_noise.py ./reference-signals/noise/uniform

echo "Getting targets file"
cp -fv ${MCV_CORPUS_DIR}/cv-valid-test.csv ./reference-signals/

# create archive for S3
echo "Archiving."
tar cz -f ./reference-signals.tar.gz ./reference-signals/ \
    && rm -rf ./reference-signals/

# upload to s3
echo "Uploading."
aws s3 cp ./reference-signals.tar.gz s3://cleverspeech-data/reference-signals.tar.gz
echo "Done!"
