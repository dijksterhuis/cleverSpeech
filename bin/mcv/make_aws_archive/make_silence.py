#!/usr/bin/env python3

import os
import sys
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
        basename = "silence_{i}.wav".format(i=example_id)
        file_path = os.path.abspath(
            os.path.join(outdir, basename)
        )
        soundfile.write(
            file_path,
            silence,
            16000,
            subtype="PCM_16",
            format="WAV"
        )


if __name__ == '__main__':
    outdir = sys.argv[1]
    main(outdir)

