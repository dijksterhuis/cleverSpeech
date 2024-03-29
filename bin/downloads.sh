#!/usr/bin/env bash

if [[ $(basename $(pwd)) != "cleverSpeech" ]]
then
    echo "Script must be run from the root of the cleverSpeech directory."
    echo "Like so: ./bin/install.sh"
    echo "You are currently in $(pwd)"
    echo "Quitting. "
    exit
fi

echo "++ | Getting DeepSpeech files..."
./bin/deepspeech/get-v093-model-files.sh
echo "-- | Done."

echo "++ | Getting pre-processed Common Voice files from AWS..."
./bin/data/get-mcv1-sentences-test.sh
./bin/data/get-mcv7-sentences-test.sh
./bin/data/get-mcv1-singlewords-test.sh
echo "-- | Done."
