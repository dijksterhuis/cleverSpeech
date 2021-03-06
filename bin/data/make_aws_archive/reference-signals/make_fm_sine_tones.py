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
MIN_FREQ = 100
MAX_FREQ = 4000
SAMPLE_RATE = 16000
MAX_AMP = 0.5
MIN_AMP = 0.0
MAX_SINES_WAVES = 1


def main(outdir):

    n_examples = range(MAX_EXAMPLES)
    bar = ProgressBar()

    for example_id in bar(n_examples):

        length = randint(MIN_LENGTH_EXAMPLES, MAX_LENGTH_EXAMPLES)

        # n_sines = randint(1, MAX_SINES_WAVES-1)

        t = np.arange(0, length) / SAMPLE_RATE
        amp = np.random.uniform(MIN_AMP, MAX_AMP, 1)

        k = 5

        freqs = []

        carrier_freq = randint(MIN_FREQ, MAX_FREQ)
        carrier_angular_freq = 2 * np.pi * t * carrier_freq

        mod_freq = randint(1, 4000)
        modulator = k * np.sin(2 * np.pi * t * mod_freq)

        main_sine_wave = np.sin(carrier_angular_freq + modulator)
        sine_wave = amp * main_sine_wave

        n_samples_fade = 1000

        fade_in_linear_ramp = np.linspace(0, 1, n_samples_fade)
        fade_out_linear_ramp = np.linspace(1, 0, n_samples_fade)

        sine_fade_in = fade_in_linear_ramp * sine_wave[0:n_samples_fade]
        sine_fade_out = fade_out_linear_ramp * sine_wave[-(n_samples_fade + 1):-1]
        untouched_sine_wave = sine_wave[n_samples_fade:-(n_samples_fade + 1)]

        sine_wave = np.concatenate(
            [sine_fade_in, untouched_sine_wave, sine_fade_out]
        )

        base_file_name = "fm_sine_{i}".format(i=example_id)
        base_file_path = os.path.abspath(
            os.path.join(outdir, base_file_name)
        )

        wav_file_name = base_file_path + ".wav"
        json_file_name = base_file_path + ".json"

        soundfile.write(
            wav_file_name,
            sine_wave,
            16000,
            subtype="PCM_16",
            format="WAV"
        )

        json_data = [
            {
                "correct_transcription": "",
                "n_samples": length,
                # "n_sines": n_sines,
                "frequencies": freqs,
                "amplitude": float(amp),
            }
        ]

        with open(json_file_name, "w+") as f:
            json.dump(json_data, f)


if __name__ == '__main__':
    outdir = sys.argv[1]
    main(outdir)

