#!/usr/bin/env python3

import os
import sys
import json
import time
import librosa
import soundfile
import progressbar

import numpy as np

BIT_DEPTH = 2 ** 15


def l_map(f, x):
    return list(map(f, x))


def load_wav(fp, dtype):
    audio, sample_rate = soundfile.read(fp, dtype=dtype)
    audio = audio.astype(np.float32)
    try:
        assert min(audio) >= -BIT_DEPTH and max(audio) <= BIT_DEPTH - 1
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


def load_transcriptions(csv_file_path):

    with open(csv_file_path, 'r') as f:
        rows = f.readlines()[1:]

    def get_sample_basename_key(split_row):
        return split_row[0].replace("cv-valid-test/", '').replace(".mp3", '')

    def get_sample_transcription(split_row):
        return split_row[1]

    rows = [row.split(',') for row in rows]

    sample_trans_map = {
        get_sample_basename_key(r): get_sample_transcription(r) for r in rows
    }

    return sample_trans_map


def main(wav_dir, trans_file_path):

    print(
        """
        Note that this script will OVERWRITE your test files with
        normalised and trimmed versions.\n
        If you have unintentionally modified your data by running this script 
        without inspecting it first, then you should pay more attention to 
        random scripts you downloaded from the internets.
        """
    )
    for i in range(10, -1, -1):
        s = "You have {} seconds until changes are made.".format(i)
        print(s)
        time.sleep(1)

    transcription_mapping = load_transcriptions(trans_file_path)

    abs_paths = l_map(
        lambda fp: os.path.abspath(os.path.join(indir, fp)),
        os.listdir(wav_dir)
    )

    abs_wav_file_paths = [x for x in abs_paths if not os.path.isdir(x) and ".wav" in x]

    wavs = load_wavs(abs_wav_file_paths, "int16")

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

    print("\n\nPre-processing done... Writing over existing files.")

    bar = progressbar.progressbar(zip(abs_paths, wavs))

    for file_data in bar:

        path, wav = file_data

        path_no_ext = path.rstrip(".wav")
        basename_no_ext = os.path.basename(path_no_ext)

        metadata_json_path = path_no_ext + ".json"

        true_trans = transcription_mapping[basename_no_ext]
        n_samples = wav.size

        json_data = [
            {
                "correct_transcription": true_trans,
                "n_samples": int(n_samples),
            }
        ]

        with open(metadata_json_path, "w+") as f:

            # save disk space in json by not using *any* delimiter whitespace
            json.dump(json_data, f, separators=(',', ':'))

        soundfile.write(path, wav, 16000, subtype="PCM_16", format="WAV")


if __name__ == '__main__':
    indir, transcript_file_path = sys.argv[1:]
    main(indir, transcript_file_path)

