#!/usr/bin/env python3

import sys
import os
from datetime import datetime, date, time
from pathlib import Path
from copy import deepcopy

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# The script expects paths to an audio file directory and an output directory.
# The script precomputes the statistics over election periods and saves
# them to the output directory.
#
# Note that as opposed to the audio files, the total speaking times (per word,
# sentence, paragraph, utterance) are measured in hours, not milliseconds.

class TermAggregator:
    def __init__(self, input_dir, output_dir):
        self.input_dir = os.path.relpath(input_dir)
        self.output_dir = os.path.relpath(output_dir)

        self.total_length = dict()
        self.relative_diff = dict()
        self.words = dict()

    def aggregate(self):
        # accumulate the data from audio files
        for audio in self.correct_audios():
            data_df = pd.read_csv(audio)
            data_df.apply(self.compute_total_length, axis=1)
            data_df.apply(self.compute_relative_difference, axis=1)
            data_df.apply(self.compute_word_statistics, axis=1)

        # create a file with accumulated values
        statistics_df = pd.DataFrame()
        for period in self.total_length:
            length_period = self.total_length[period]
            for speaker in length_period:
                length_speaker = length_period[speaker]
                for role in length_speaker:
                    length = length_speaker[role]
                    diff = self.relative_diff[period][speaker][role]
                    words = self.words[period][speaker][role]

                    up = diff["utterance-paragraph"] / length["utterance"]
                    ps = diff["paragraph-sentence"] / length["paragraph"]
                    sw = diff["sentence-word"] / length["sentence"]

                    count = words["word_count"]
                    anchor = words["no_anchor"]
                    minutes = self.to_minutes(length["utterance"])

                    statistics_df = statistics_df.append({
                        "election_period": period,
                        "speaker": speaker,
                        "role": role,
                        "length_word": self.to_hours(length["word"]),
                        "length_sentence": self.to_hours(length["sentence"]),
                        "length_paragraph": self.to_hours(length["paragraph"]),
                        "length_utterance": self.to_hours(length["utterance"]),
                        "utterance-paragraph": up,
                        "paragraph-sentence": ps,
                        "sentence-word": sw,
                        "unanchored": anchor / count,
                        "words_per_minute": count / minutes
                    }, ignore_index=True)

        # make sure the directory exists
        path_to_dir = os.path.join(self.output_dir, "precomputed")
        Path(path_to_dir).mkdir(parents=True, exist_ok=True)

        path = os.path.join(path_to_dir, "all.txt")
        statistics_df.to_csv(path, index=False)

    def to_minutes(self, length):
        seconds = length / 1000
        minutes = seconds / 60
        return minutes

    def to_hours(self, length):
        seconds = length / 1000
        minutes = seconds / 60
        hours = minutes / 60
        return hours

    def compute_word_statistics(self, row):
        speaker, role = row["speaker"], row["role"]
        period = row["election_period"]

        default_values = {
            "word_count": 0,
            "no_anchor": 0
        }
        self.check_field_exists(
            self.words,
            default_values,
            speaker,
            role,
            period
        )

        words = self.words[period][speaker][role]
        
        words["word_count"] += row["word_count"]
        words["no_anchor"] += row["no_anchor"]

    def compute_relative_difference(self, row):
        speaker, role = row["speaker"], row["role"]
        period = row["election_period"]

        default_values = {
            "utterance-paragraph": 0,
            "paragraph-sentence": 0,
            "sentence-word": 0
        }
        self.check_field_exists(
            self.relative_diff,
            default_values,
            speaker,
            role,
            period
        )

        relative_diff = self.relative_diff[period][speaker][role]

        relative_diff["utterance-paragraph"] += row["utterance"] - row["paragraph"]
        relative_diff["paragraph-sentence"] += row["paragraph"] - row["sentence"]
        relative_diff["sentence-word"] += row["sentence"] - row["word"]

    def compute_total_length(self, row):
        speaker, role = row["speaker"], row["role"] 
        period = row["election_period"]

        default_values = {
            "word": 0,
            "sentence": 0,
            "paragraph": 0,
            "utterance": 0
        }
        self.check_field_exists(
            self.total_length,
            default_values,
            speaker,
            role,
            period
        )

        length = self.total_length[period][speaker][role]

        length["word"] += row["word"]
        length["sentence"] += row["sentence"]
        length["paragraph"] += row["paragraph"]
        length["utterance"] += row["utterance"]

    def check_field_exists(self, field, values, speaker, role, period):
        """Ensure there is a field in the field dict corresponding to this speaker, role and period."""
        if not (period in field):
            field[period] = dict()
        field_period = field[period]

        if not (speaker in field_period):
            field_period[speaker] = dict()
        field_speaker = field_period[speaker]

        if not (role in field_speaker):
            field_speaker[role] = values.copy()

    def correct_audios(self):
        for dirpath,dirnames,filenames in os.walk(self.input_dir):
            for filename in filenames:
                audio = os.path.join(dirpath, filename)
                yield audio

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        agg = TermAggregator(args[0], args[1])
        agg.aggregate()
    else:
        print("Incorrect number of args")
