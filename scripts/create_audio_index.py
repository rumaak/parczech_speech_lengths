#!/usr/bin/env python3

import sys
import os
import pickle

import pandas as pd

# The script expects paths to an audio file directory. The script creates
# an index with election_period, meeting, sitting, and agenda as keys and
# an audio file name as value.

def create_audio_index(audio_dir):
    index = set()
    for audio in audio_files(audio_dir):
        data_df = pd.read_csv(audio)
        data_df.apply(lambda row: update_index(index, audio, row), axis=1)

    columns = [
        "election_period",
        "meeting",
        "sitting",
        "agenda",
        "filename"
    ]
    index_df = pd.DataFrame(index, columns=columns)

    path = os.path.join(audio_dir, "audio_index.csv")
    index_df.to_csv(path, index=False)

def audio_files(audio_dir):
    for dirpath,dirnames,filenames in os.walk(audio_dir):
        for filename in filenames:
            index_filename = "audio_index.csv"
            if filename != index_filename:
                audio = os.path.join(dirpath, filename)
                yield audio

def update_index(index, audio, row):
    index.add((
        row["election_period"],
        row["meeting"],
        row["sitting"],
        row["agenda"],
        audio
    ))

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 1:
        create_audio_index(args[0])
    else:
        print("Incorrect number of args")

