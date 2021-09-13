#!/usr/bin/env python3

import sys
import os
import pickle

import pandas as pd

# The script expects paths to an audio file directory. The script creates
# an index file with keys (speaker, role, term, meeting, sitting, agenda)
# and audio files as values. The output file is a pickled dict; it is
# thus not human-readable.

def create_audio_index(audio_dir):
    index = dict()

    for audio in audio_files(audio_dir):
        data_df = pd.read_csv(audio)
        data_df.apply(lambda row: update_index(index, audio, row), axis=1)

    path = os.path.join(audio_dir, "audio_index.pkl")
    with open(path, 'wb') as f:
        pickle.dump(index, f, pickle.HIGHEST_PROTOCOL)

def update_index(index, audio, row):
    key = (
        row["speaker"],
        row["role"],
        row["election_period"],
        row["meeting"],
        row["sitting"],
        row["agenda"]
    )

    if not (key in index):
        index[key] = []

    index[key].append(audio)

def audio_files(audio_dir):
    for dirpath,dirnames,filenames in os.walk(audio_dir):
        for filename in filenames:
            index_filename = "audio_index.pkl"
            if filename != index_filename:
                audio = os.path.join(dirpath, filename)
                yield audio

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 1:
        create_audio_index(args[0])
    else:
        print("Incorrect number of args")

