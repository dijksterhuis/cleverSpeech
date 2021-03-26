#!/usr/bin/env bash

set -e

SAMPLES_URL=https://cleverspeech-data.s3.eu-west-2.amazonaws.com/samples.tar.gz
SILENCE_URL=https://cleverspeech-data.s3.eu-west-2.amazonaws.com/silence.tar.gz

if [[ -f samples.tar.gz ]]
then
    echo "samples.tar.gz archive exists so skipping download"
else
    echo "Getting samples archive."
    curl -o ./samples.tar.gz ${SAMPLES_URL} \
        && echo "Got samples archive."
fi

# make samples directory and dump files based on ID.

echo "Extracting samples archive."
mkdir -p ./samples/all ./samples/10 ./samples/100 ./samples/1000
tar -xzf ./samples.tar.gz \
    && mv -f ./samples/sample-*.wav ./samples/all \
    && rm -f ./samples.tar.gz \
    && echo "Extraction successful."

# create some additional data sets for running tests on the code
echo "copying 10 files" \
    && mkdir -p ./samples/10 \
    && cp -f ./samples/all/sample-00000?.wav ./samples/10

echo "copying 100 files" \
    && mkdir -p ./samples/100 \
    && cp -f ./samples/all/sample-0000??.wav ./samples/100

echo "copying 1000 files" \
    && mkdir -p ./samples/1000 \
    && cp -f ./samples/all/sample-000???.wav ./samples/1000


if [[ -f silence.tar.gz ]]
then
    echo "silence.tar.gz archive exists so skipping download"
else
    echo "Getting silence archive."
    curl -o ./silence.tar.gz ${SAMPLES_URL} \
        && echo "Got silence archive."
fi

echo "Extracting silence archive."
tar -xzf ./silence.tar.gz \
 && echo "Extraction successful."

echo "====>: Data prep script completed. <===="

