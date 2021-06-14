#!/usr/bin/env bash

#~/0-dox/0-data/mozilla-cv/cv_corpus_v1/

echo "Clearing all .mp3 files from ${1} to save some space..."

MOZILLA_COMMON_VOICE_PATH="${1}"

find ${MOZILLA_COMMON_VOICE_PATH}/*/ -type f -name "*.mp3" -print -exec rm -f {} \;
