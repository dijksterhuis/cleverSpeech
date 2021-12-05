#!/usr/bin/env bash

set -e

SAMPLES_URL=https://cleverspeech-data.s3.eu-west-2.amazonaws.com/singlewords.tar.gz

if [[ -f singlewords.tar.gz ]]
then
    echo "samples.tar.gz archive exists so skipping download"
else
    echo "Getting samples archive."
    curl -o ./singlewords.tar.gz ${SAMPLES_URL} \
        && echo "Got samples archive."
fi

# make samples directory and dump files based on ID.

echo "Extracting samples archive."
tar -xzf ./singlewords.tar.gz \
    && echo "Extraction successful."

echo "====>: ./samples/ prep script completed. <===="
