#!/usr/bin/env bash

set -e

SILENCE_URL=https://cleverspeech-data.s3.eu-west-2.amazonaws.com/silence.tar.gz

if [[ -f silence.tar.gz ]]
then
    echo "silence.tar.gz archive exists so skipping download"
else
    echo "Getting silence archive."
    curl -o ./silence.tar.gz ${SILENCE_URL} \
        && echo "Got silence archive."
fi

echo "Extracting silence archive."
tar -xzf ./silence.tar.gz \
 && echo "Extraction successful."

echo "====>: Data prep script completed. <===="

