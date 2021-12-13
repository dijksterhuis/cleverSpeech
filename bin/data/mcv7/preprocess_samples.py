#!/usr/bin/env python3

import os
import sys
import json
import boto3
import shutil
import tarfile
import soundfile

import numpy as np
import multiprocessing as mp

from cleverspeech.utils.Utils import Logger
from progressbar import ProgressBar

BIT_DEPTH = 2 ** 15


def l_map(f, x):
    return list(map(f, x))


def get_wav_file_size(fp):
    dtype = "int16"
    audio, sample_rate = soundfile.read(fp, dtype=dtype)
    try:
        assert min(audio) >= -BIT_DEPTH and max(audio) <= BIT_DEPTH - 1
    except AssertionError as e:
        err = "Problem with source file resolution:\n"
        err += "min(audio)={}\n".format(min(audio))
        err += "max(audio)={}\n".format(max(audio))
        err += "input must be valid 16 bit audio: -2**15 <= x <= 2**15 -1\n"
        Logger.critical(err)
        raise AssertionError
    return audio


def load_wavs(fps, dtype="int16"):
    return [get_wav_file_size(f) for f in fps]


def load_transcriptions(csv_file_path):

    # headers = wav_filename,wav_filesize,transcript

    with open(csv_file_path, 'r') as f:
        rows = f.readlines()[1:]

    def get_sample_basename_key(split_row):
        return split_row[0].replace(".wav", '')

    def get_sample_transcription(split_row):
        return split_row[2]

    rows = [row.rstrip("\n").split(',') for row in rows]

    sample_trans_map = {
        get_sample_basename_key(r): get_sample_transcription(r) for r in rows
    }

    return sample_trans_map


def make_directory_structure(major_id, minor_id):
    samples_dir = os.path.join(os.path.join("./samples", major_id), minor_id)
    os.makedirs(samples_dir, exist_ok=True)
    return samples_dir


def move_files(args):
    initial_path, end_path = args
    shutil.copy(initial_path, end_path)


def get_json_metadata(args) -> list:
    transcription, wav = args
    n_samples = wav.size

    return [
        {
            "correct_transcription": transcription,
            "n_samples": int(n_samples),
        }
    ]


def dump_json(args):
    path, json_data = args
    metadata_json_path = path.rstrip(".wav") + ".json"
    with open(metadata_json_path, "w+") as f:
        # save disk space in json by not using *any* delimiter
        # whitespace
        json.dump(json_data, f, separators=(',', ':'))
    return metadata_json_path


def dump_wav_file(args):
    path, wav = args
    soundfile.write(
        path, wav.astype(np.int16), 16000, subtype="PCM_16", format="WAV"
    )


def process(wav_dir, trans_file_path, samples_dir):

    Logger.info("Loading transcriptions....")

    transcription_mapping = load_transcriptions(trans_file_path)

    initial_transcription_file_path = os.path.join(
        wav_dir, os.path.basename(trans_file_path)
    )
    samples_transcription_file_path = os.path.join(
        samples_dir, os.path.basename(trans_file_path)
    )

    Logger.info("... Loaded transcriptions.")
    Logger.info("Moving transcriptions csv file...")

    move_files(
        (initial_transcription_file_path, samples_transcription_file_path)
    )

    Logger.info("... Moved transcriptions csv file.")
    Logger.info("Loading wav file paths...")

    def absolute_file_path(directory, x):
        return os.path.abspath(os.path.join(directory, x))

    def safety_check(directory, x):
        return not os.path.isdir(absolute_file_path(directory, x)) and ".wav" in x

    wav_file_paths = [
        x for x in os.listdir(wav_dir) if safety_check(wav_dir, x)
    ]

    initial_abs_file_paths = l_map(
        lambda file_path: absolute_file_path(wav_dir, file_path), wav_file_paths
    )
    new_wav_dir = os.path.join(samples_dir, "all")
    os.makedirs(new_wav_dir, exist_ok=True)
    samples_abs_file_paths = l_map(
        lambda file_path: absolute_file_path(new_wav_dir, file_path), wav_file_paths
    )

    Logger.info("Have these wav files (first 10)")
    for fp in initial_abs_file_paths[0:10]:
        print(fp)

    Logger.info("Have these wav files (last 10)")
    for fp in initial_abs_file_paths[-10:]:
        print(fp)

    Logger.info("Moving wav files to {} directory...".format(samples_dir))
    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(
            move_files,
            zip(initial_abs_file_paths, samples_abs_file_paths)
        )
    Logger.info("... wav file move complete")
    Logger.info("Moving transcription file to {} directory...".format(samples_dir))

    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(
            move_files,
            zip(initial_abs_file_paths, samples_abs_file_paths)
        )
    Logger.info("... wav file move complete")
    Logger.info("Loading wav files...")

    with mp.Pool(mp.cpu_count()) as pool:
        wav_sizes = pool.map(get_wav_file_size, samples_abs_file_paths)

    Logger.info("... Loaded wav files. Processing now.")
    Logger.info("Checking for invalid samples...")

    invalid_counter, valid_counter = 0, 0
    transcription_paths = list(transcription_mapping.keys())
    cleaned_paths, transcriptions = [], []
    for path in samples_abs_file_paths:
        basename_no_ext = os.path.basename(path).rstrip(".wav")
        if basename_no_ext not in transcription_paths:
            invalid_counter += 1
            Logger.warn("File not found in transcriptions file: {}".format(path))
            Logger.warn("Probably invalid (only silence or not long enough) ==> Deleting.")
            os.remove(path)
            Logger.warn("... Deleted {}\n".format(path))
        else:
            valid_counter += 1
            cleaned_paths.append(path)
            transcriptions.append(transcription_mapping[basename_no_ext])

    Logger.info("Found {} invalid examples and deleted them".format(invalid_counter))
    Logger.info("Processing remaining {} valid files...".format(valid_counter))

    with mp.Pool(mp.cpu_count()) as pool:
        json_data = pool.map(get_json_metadata, zip(transcriptions, wav_sizes))
    Logger.info("Generated json metadata.")

    with mp.Pool(mp.cpu_count()) as pool:
        json_paths = pool.map(dump_json, zip(cleaned_paths, json_data))
    Logger.info("Wrote {} json metadata files.".format(len(json_paths)))

    return samples_transcription_file_path, cleaned_paths, json_paths


def create_tar_archive(major, minor, fps):

    tar_fname = "{}-{}.tar.gz".format(major, minor)

    def convert(x):
        x = x.split("samples")[-1].lstrip(".").lstrip("/")
        return os.path.join("./samples", x)

    fps = l_map(convert, fps)

    with ProgressBar(max_value=len(fps) + 1) as tar_bar:
        with tarfile.open(tar_fname, "w:gz") as tar:
            for fp in fps:
                tar_bar.update(1)
                tar.add(fp)

    return tar_fname


def upload_to_s3(tar_fname):

    total_size = os.path.getsize(tar_fname)

    s3 = boto3.client('s3')

    with ProgressBar(max_value=total_size) as s3_bar:

        def _upload_progress(chunk):
            s3_bar.update(s3_bar.value + chunk)

        s3.upload_file(
            Bucket="cleverspeech-data",
            Key=tar_fname.lstrip("./"),
            Filename=tar_fname,
            Callback=_upload_progress,
        )


def main(in_dir, major, minor):
    transcription_file_path = os.path.join(in_dir, "test.csv")

    samples_dir = make_directory_structure(major, minor)

    out_transcription_file_path, out_wav_file_paths, out_json_paths = process(
        in_dir, transcription_file_path, samples_dir
    )
    all_file_paths = out_wav_file_paths + out_json_paths + [out_transcription_file_path]

    Logger.info("Processing complete. Creating archive from {} files...".format(
        len(all_file_paths))
    )
    tar_file_name = create_tar_archive(
        major, minor, all_file_paths
    )
    Logger.info("... Created archive. ")
    Logger.info("Uploading to S3...")
    upload_to_s3(tar_file_name)
    Logger.info("... Uploaded. Script complete. Have a great day!")


if __name__ == '__main__':
    main(*sys.argv[1:])






