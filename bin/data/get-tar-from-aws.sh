#!/usr/bin/env bash

set -e

ARCHIVE_FILE_NAME=mcv1-sentences.tar.gz
SAMPLES_URL=https://cleverspeech-data.s3.eu-west-2.amazonaws.com/${ARCHIVE_FILE_NAME}

if [[ -f ${ARCHIVE_FILE_NAME} ]]
then
    echo "samples.tar.gz archive exists so skipping download"
else
    echo "Getting samples archive."
    curl -o ./${ARCHIVE_FILE_NAME} ${SAMPLES_URL} \
        && echo "Got samples archive."
fi

# make samples directory and dump files based on ID.

echo "Extracting samples archive."
tar -xzf ./${ARCHIVE_FILE_NAME} \
    && echo "Extraction successful."

echo "====>: ./samples/ prep script completed. <===="
