#!/usr/bin/env python3

import os
import sys
import json
import soundfile
from random import randint
from progressbar import ProgressBar
import numpy as np

BIT_DEPTH = 2 ** 15 - 1
MAX_EXAMPLES = 1000
MAX_LENGTH_EXAMPLES = 90000
MIN_LENGTH_EXAMPLES = MAX_LENGTH_EXAMPLES // 3
MAX_AMP = 0.5
MIN_AMP = 1e-5


def main(outdir):

    n_examples = range(MAX_EXAMPLES)
    bar = ProgressBar()

    for example_id in bar(n_examples):

        length = randint(MIN_LENGTH_EXAMPLES, MAX_LENGTH_EXAMPLES)

        noise = np.random.uniform(MIN_AMP, MAX_AMP, length)
        noise = (BIT_DEPTH * noise).astype(np.int16)

        base_file_name = "noise_{i}".format(i=example_id)
        base_file_path = os.path.abspath(
            os.path.join(outdir, base_file_name)
        )

        wav_file_name = base_file_path + ".wav"
        json_file_name = base_file_path + ".json"

        soundfile.write(
            wav_file_name,
            noise,
            16000,
            subtype="PCM_16",
            format="WAV"
        )

        json_data = [
            {
                "correct_transcription": "",
                "n_samples": length,
            }
        ]

        with open(json_file_name, "w+") as f:
            json.dump(json_data, f)


if __name__ == '__main__':
    outdir = sys.argv[1]
    main(outdir)

