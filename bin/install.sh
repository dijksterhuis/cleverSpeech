#!/usr/bin/env bash

if [[ $(basename $(pwd)) != "cleverSpeech" ]]
then
    echo "Script must be run from the root of the cleverSpeech directory."
    echo "Like so: ./bin/install.sh"
    echo "You are currently in $(pwd)"
    echo "Quitting. "
    exit
fi

echo "++ | Installing cleverSpeech python dependencies..."
python3 -m pip install --upgrade --requirement ./reqs.txt
echo "-- | Done."

echo "++ | Installing victim model python dependencies..."
python3 -m pip install --upgrade --r ./models/DeepSpeech/src/requirements.txt
echo "-- | Done."

echo "++ | Getting DeepSpeech files..."
./bin/deepspeech/get_model_files.sh
echo "-- | Done."

echo "++ | Getting pre-processed Common Voice files from AWS..."
./bin/mcv/create-samples-dir.sh
echo "-- | Done."

echo "-------------------------------------------------"
echo "You should be ready to run one of the experiments from the ./experiments directory:"
find ./experiments | grep attacks.py

echo "... Once you run this command: source ./bin/attacks/env.sh"