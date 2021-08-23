#!/usr/bin/env python3

import sys
import os
from datetime import datetime, date, time
from pathlib import Path
from copy import deepcopy

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# The script expects paths to an audio file directory, an output directory
# and a time interval (two additional arguments, start and end). The script
# computes the statistics over the specified interval.
# 
# Example of proper datetime (ISO 8601):
# 2021-08-13T03:34:17
#
# Statistics of an audio are used only if both audio start and end belong
# to the said interval (makes more sense as audio files overlap)

# TODO ms aren't probably very good way to measure the lenghts of speeches

class IntervalAggregator:
    def __init__(self, input_dir, output_dir, start, end):
        self.start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        self.end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")

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
                        "length_word": length["word"],
                        "length_sentence": length["sentence"],
                        "length_paragraph": length["paragraph"],
                        "length_utterance": length["utterance"],
                        "utterance-paragraph": up,
                        "paragraph-sentence": ps,
                        "sentence-word": sw,
                        "unanchored": anchor / count,
                        "words_per_minute": count / minutes
                    }, ignore_index=True)

        # make sure the directory exists
        path_to_dir = self.resolve_output_dir()
        Path(path_to_dir).mkdir(parents=True, exist_ok=True)

        path = os.path.join(path_to_dir, "all.txt")
        statistics_df.to_csv(path, index=False)

    def to_minutes(self, length):
        seconds = length / 1000
        minutes = seconds / 60
        return minutes

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

    # TODO this looks bad, don't know how to make prettier yet simple
    def correct_audios(self):
        # Years
        for year_dir in os.listdir(self.input_dir):
            if self.check_year(year_dir):
                year_path = os.path.join(self.input_dir, year_dir)

                # Months
                for month_dir in os.listdir(year_path):
                    if self.check_month(year_dir, month_dir):
                        month_path = os.path.join(year_path, month_dir)

                        # Days
                        for day_dir in os.listdir(month_path):
                            if self.check_day(year_dir, month_dir, day_dir):
                                day_path = os.path.join(month_path, day_dir)

                                # Audio files
                                for audio in os.listdir(day_path):
                                    if self.check_audio(audio):
                                        yield os.path.join(day_path, audio)

    # TODO this time of time striping is used in both script, consider
    #      creating a shared helper module
    def check_audio(self, audio):
        datetime_string = audio.split(".")[0]

        year = int(datetime_string[:4])
        month = int(datetime_string[4:6])
        day = int(datetime_string[6:8])

        hour_start = int(datetime_string[8:10])
        minute_start = int(datetime_string[10:12])

        hour_end = int(datetime_string[12:14])
        minute_end = int(datetime_string[14:16])

        d = date(year, month, day)

        time_start = time(hour_start, minute_start)
        time_end = time(hour_end, minute_end)

        start = datetime.combine(d, time_start)
        end = datetime.combine(d, time_end)

        if (self.start <= start) and (end <= self.end):
            return True
        
        return False

    def check_day(self, year, month, day):
        # Day
        after_start = self.start.day <= int(day)
        before_end = int(day) <= self.end.day

        # Month
        if self.start.month < int(month): 
            after_start = True

        if int(month) < self.end.month: 
            before_end = True

        # Year
        if self.start.year < int(year): 
            after_start = True

        if int(year) < self.end.year: 
            before_end = True

        return after_start and before_end

    def check_month(self, year, month):
        # Month
        after_start = self.start.month <= int(month)
        before_end = int(month) <= self.end.month

        # Year
        if self.start.year < int(year): 
            after_start = True

        if int(year) < self.end.year: 
            before_end = True

        return after_start and before_end

    def check_year(self, year):
        # Year
        after_start = self.start.year <= int(year)
        before_end = int(year) <= self.end.year
        return after_start and before_end

    def resolve_output_dir(self):
        start = self.start.strftime("%Y%m%d%H%M")
        end = self.end.strftime("%Y%m%d%H%M")

        path_to_dir = os.path.join(
            self.output_dir,
            start + "-" + end
        )

        return path_to_dir

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 4:
        agg = IntervalAggregator(args[0], args[1], args[2], args[3])
        agg.aggregate()
    else:
        print("Incorrect number of args")
