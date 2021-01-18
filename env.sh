#!/usr/bin/env bash

export DEEPSPEECH_SRC_DIR=/home/dijksterhuis/0-dox/1-dev/2-models/DeepSpeechAdversaries
export DEEPSPEECH_CHECKPOINT_DIR=/home/dijksterhuis/0-dox/1-dev/3-attacks/old/cwAudioAttack012018/deepspeech-0.4.1-checkpoint
export DEEPSPEECH_MODEL_DIR=/home/dijksterhuis/0-dox/1-dev/2-models/DeepSpeechData
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/models/DeepSpeech/"