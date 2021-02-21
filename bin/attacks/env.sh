#!/usr/bin/env bash

echo "Add cleverSpeech to your PYTHONPATH..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Add models to your PYTHONPATH..."
for model_dir in ./models/*/src/
do
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/${model_dir}"
done
