#!/usr/bin/env python3

import os
import sys
import json
import time
import soundfile
import progressbar

import numpy as np
import multiprocessing as mp

BIT_DEPTH = 2 ** 15


def l_map(f, x):
    return list(map(f, x))


def load_wav(fp):
    dtype = "int16"
    audio, sample_rate = soundfile.read(fp, dtype=dtype)
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
    return [load_wav(f) for f in fps]


def load_transcriptions(csv_file_path):

    # headers = wav_filename,wav_filesize,transcript

    with open(csv_file_path, 'r') as f:
        rows = f.readlines()[1:]

    def get_sample_basename_key(split_row):
        return split_row[0].replace(".wav", '')

    def get_sample_transcription(split_row):
        return split_row[2].rstrip("\n")

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
        lambda fp: os.path.abspath(os.path.join(wav_dir, fp)),
        os.listdir(wav_dir)
    )

    abs_wav_file_paths = [x for x in abs_paths if not os.path.isdir(x) and ".wav" in x]

    print("\nHave these wav files (first 10)")
    for fp in abs_wav_file_paths[0:10]:
        print(fp)

    print("\nHave these wav files (last 10)")
    for fp in abs_wav_file_paths[-10:]:
        print(fp)

    print("\nLoading wav files...")
    with mp.Pool(mp.cpu_count()) as pool:
        wavs = pool.map(load_wav, abs_wav_file_paths)

    # wavs = load_wavs(abs_wav_file_paths, "int16")

    print("... Loaded wav files. Processing now.")

    bar = progressbar.progressbar(zip(abs_paths, wavs))

    for file_data in bar:

        path, wav = file_data

        path_no_ext = path.rstrip(".wav")
        basename_no_ext = os.path.basename(path_no_ext)
        metadata_json_path = path_no_ext + ".json"

        try:
            true_trans = transcription_mapping[basename_no_ext]

        except KeyError:

            s = "\nFile not found in transcriptions file: {}".format(
                basename_no_ext
            )
            s += "\nProbably invalid (only silence or not long enough)."
            s += "\nDeleting {}".format(basename_no_ext)
            print(s)
            os.remove(
                os.path.abspath(
                    os.path.join(wav_dir, path)
                )
            )
            print("... Deleted {}\n".format(basename_no_ext))
            continue

        else:
            n_samples = wav.size

            json_data = [
                {
                    "correct_transcription": true_trans,
                    "n_samples": int(n_samples),
                }
            ]

            with open(metadata_json_path, "w+") as f:

                # save disk space in json by not using *any* delimiter
                # whitespace
                json.dump(json_data, f, separators=(',', ':'))

            soundfile.write(path, wav.astype(np.int16), 16000, subtype="PCM_16", format="WAV")


if __name__ == '__main__':
    indir, transcript_file_path = sys.argv[1:]
    main(indir, transcript_file_path)

