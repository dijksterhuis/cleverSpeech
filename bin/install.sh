#!/usr/bin/env bash

echo "++ | Double-checking that git submodules are installed correctly..."
# TODO
echo "-- | Done."

echo "++ | Adding cleverSpeech to your PYTHONPATH..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "-- | Done."

echo "++ | Adding models to your PYTHONPATH..."
for model_dir in ./models/*/src/
do
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/${model_dir}"
done
echo "-- | Done."

echo "++ | Installing cleverSpeech python dependencies..."
python3 -m pip install --upgrade --requirement ./reqs.txt
echo "-- | Done."

echo "++ | Installing victim model python dependencies..."
python3 -m pip install --upgrade --r ./models/DeepSpeech/requirements.txt
echo "-- | Done."

echo "++ | Getting DeepSpeech files..."
./bin/deepspeech/get_model_files.sh
echo "-- | Done."

echo "++ | Getting Common Voice files..."
./bin/deepspeech/get_model_files.sh
echo "-- | Done."

echo "-------------------------------------------------"
echo "You should be ready to run one of the experiments from the ./experiments directory:"
find ./experiments | grep attacks.py