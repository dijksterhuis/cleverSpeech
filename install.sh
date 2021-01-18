#!/usr/bin/env bash

echo "++ | Double-checking that git submodules are installed correctly..."
# TODO
echo "-- | Done."

echo "++ | Setting cleverSpeech environment variables for your shell..."
export DEEPSPEECH_CHECKPOINT_DIR=/home/dijksterhuis/0-dox/1-dev/3-attacks/old/cwAudioAttack012018/deepspeech-0.4.1-checkpoint
export DEEPSPEECH_MODEL_DIR=/home/dijksterhuis/0-dox/1-dev/2-models/DeepSpeechData
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/models/DeepSpeech/"
echo "-- | Done."

echo "++ | Installing cleverSpeech python dependencies..."
python3 -m pip install --upgrade --requirement ./reqs.txt
echo "-- | Done."

echo "++ | Installing victim model python dependencies..."
python3 -m pip install --upgrade --r ./models/DeepSpeech/requirements.txt
echo "-- | Done."

echo "-------------------------------------------------"
echo "You should be ready to run one of the experiments from the ./experiments directory."
