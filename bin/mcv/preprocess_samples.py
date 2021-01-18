#!/usr/bin/env python3

import os
import sys
import librosa
import soundfile

import numpy as np

BIT_DEPTH = 2 ** 15 - 1


def l_map(f, x):
    return list(map(f, x))


def load_wav(fp, dtype):
    audio, sample_rate = soundfile.read(fp, dtype=dtype)
    audio = audio.astype(np.float32)
    try:
        assert min(audio) >= -2**15 and max(audio) <= 2**15 - 1
    except AssertionError as e:
        err = "Problem with source file resolution:\n"
        err += "min(audio)={}\n".format(min(audio))
        err += "max(audio)={}\n".format(max(audio))
        err += "input must be valid 16 bit audio: -2**15 <= x <= 2**15 -1\n"
        print(err)
        raise AssertionError
    return audio


def load_wavs(fps, dtype="int16"):
    return [load_wav(f, dtype) for f in fps]


def amplitude_normalisation(x):
    if np.max(x) < 0:
        # if max is somehow negative (possibly some weird phase issue) then
        # don't divide by the negative sign so we don't flip the phase
        norm = - np.max(x)
    elif np.max(x) > 0:
        # max is positive and greater than zero, all good.
        norm = np.max(x)
    else:
        # there's one annoying empty example in the mcv test data set
        # (it should not be counted as "valid"!).
        print("Zero array! Normalising with max == 1...")
        print("This is usually sample 001156.wav from cv-valid-test/")
        norm = 1

    return x * BIT_DEPTH * 0.5 / norm


def main(indir):

    print(
        """
        Note that this script will OVERWRITE your test files with
        normalised and trimmed versions.\n
        If you have unintentionally modified your data by running this script 
        without inspecting it first, then you should pay more attention to 
        random scripts you downloaded from the internets.
        """
    )

    abs_paths = l_map(
        lambda fp: os.path.abspath(os.path.join(indir, fp)),
        os.listdir(indir)
    )

    wavs = load_wavs(abs_paths, "int16")
    wavs = l_map(
        lambda x: amplitude_normalisation(x),
        wavs
    )
    wavs = l_map(
        lambda x: librosa.effects.trim(x, ref=np.mean, top_db=20)[0],
        wavs
    )
    wavs = l_map(
        lambda x: x.astype(np.int16),
        wavs
    )

    print("Pre-processing done... Writing over existing files.")

    for path, wav in zip(abs_paths, wavs):
        soundfile.write(path, wav, 16000, subtype="PCM_16", format="WAV")


if __name__ == '__main__':
    indir = sys.argv[1]
    main(indir)

