#!/usr/bin/env python3

import os
import sys
import json
import librosa
import soundfile
from random import randint

import numpy as np

BIT_DEPTH = 2 ** 15 - 1
MAX_EXAMPLES = 1000
MAX_LENGTH_EXAMPLES = 120000
MIN_LENGTH_EXAMPLES = MAX_LENGTH_EXAMPLES // 2


def main(outdir):

    for example_id in range(MAX_EXAMPLES):
        length = randint(MIN_LENGTH_EXAMPLES, MAX_LENGTH_EXAMPLES)

        silence = np.zeros(length, dtype=np.int16)
        base_file_name = "silence_{i}".format(i=example_id)
        base_file_path = os.path.abspath(
            os.path.join(outdir, base_file_name)
        )

        wav_file_name = base_file_path + ".wav"
        json_file_name = base_file_path + ".json"

        soundfile.write(
            wav_file_name,
            silence,
            16000,
            subtype="PCM_16",
            format="WAV"
        )

        json_data = [
            {
                "correct_transcription": "",
                "n_samples": length
            }
        ]

        with open(json_file_name, "w+") as f:
            json.dump(json_data, f)


if __name__ == '__main__':
    outdir = sys.argv[1]
    main(outdir)

