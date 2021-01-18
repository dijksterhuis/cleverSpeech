#!/usr/bin/env bash

echo "Moving .wav files from ${1} to ${2} ..."

find ${1} -type f -name "*.wav" -print -exec mv -f {} ${2} \;
