#!/usr/bin/env bash

export MCV_CORPUS_DIR=${1}

if [[ -z ${MCV_CORPUS_DIR} ]]
then
  echo "I need the path to the cv_corpus_v1/ directory as an argument please!"
  exit
fi

mkdir -p ./reference-signals/sines/sine/all \
    ./reference-signals/sines/additive/all \
    ./reference-signals/sines/am/all \
    ./reference-signals/sines/fm/all \
    ./reference-signals/noise/uniform/all

echo "Creating basic sine files."
python3 ./bin/data/make_aws_archive/reference-signals/make_sine_tones.py ./reference-signals/sines/sine/all

echo "Creating additive sine files."
python3 ./bin/data/make_aws_archive/reference-signals/make_additive_sine_tones.py ./reference-signals/sines/additive/all

echo "Creating am sine files."
python3 ./bin/data/make_aws_archive/reference-signals/make_am_sine_tones.py ./reference-signals/sines/am/all

echo "Creating fm sine files."
python3 ./bin/data/make_aws_archive/reference-signals/make_fm_sine_tones.py ./reference-signals/sines/fm/all

echo "Creating uniform noise files."
python3 ./bin/data/make_aws_archive/reference-signals/make_uniform_noise.py ./reference-signals/noise/uniform/all

echo "Copying targets files"
cp -fv ${MCV_CORPUS_DIR}/cv-valid-test.csv ./reference-signals/sines/sine
cp -fv ${MCV_CORPUS_DIR}/cv-valid-test.csv ./reference-signals/sines/additive
cp -fv ${MCV_CORPUS_DIR}/cv-valid-test.csv ./reference-signals/sines/am
cp -fv ${MCV_CORPUS_DIR}/cv-valid-test.csv ./reference-signals/sines/fm
cp -fv ${MCV_CORPUS_DIR}/cv-valid-test.csv ./reference-signals/sines/sine
cp -fv ${MCV_CORPUS_DIR}/cv-valid-test.csv ./reference-signals/noise/uniform



# create archive for S3
echo "Archiving."
tar cz -f ./reference-signals.tar.gz ./reference-signals/ \
    && rm -rf ./reference-signals/

# upload to s3
echo "Uploading."
aws s3 cp ./reference-signals.tar.gz s3://cleverspeech-data/reference-signals.tar.gz
echo "Done!"
