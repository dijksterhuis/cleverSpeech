#!/usr/bin/env bash

set -e

REFSIGS_URL=https://cleverspeech-data.s3.eu-west-2.amazonaws.com/reference-signals.tar.gz

if [[ -f reference-signals.tar.gz ]]
then
    echo "reference-signals.tar.gz archive exists so skipping download"
else
    echo "Getting reference-signals archive."
    curl -o ./reference-signals.tar.gz ${REFSIGS_URL} \
        && echo "Got reference-signals archive."
fi

echo "Extracting reference signals archive."
tar -xzf ./reference-signals.tar.gz \
 && echo "Extraction successful."

echo "====>: ./reference-signals/ prep script completed. <===="

