#!/usr/bin/env python3

import sys
import os
from datetime import datetime, date, time

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# The script expects path to the audio files, output directory and a time
# interval, over over which the data should be aggregated (two separate
# arguments).
# 
# Example of proper datetime (ISO 8601):
# 2021-08-13T03:34:17
#
# Statistics of an audio are used only if both audio start and end belong
# to the said interval (makes more sense as audio files overlap)

class Aggregator:
    def __init__(self, input_dir, output_dir, start, end):
        self.input_dir = os.path.relpath(input_dir)
        self.output_dir = os.path.relpath(output_dir)
        self.start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        self.end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")

        self.total_length = dict()

    def tables_plots(self):
        self.speech_length_statistics()

        # TODO add plotting other statistics

    def aggregate(self):
        for audio in self.correct_audios():
            data_df = pd.read_csv(audio)
            data_df.apply(self.compute_total_length, axis=1)

            # TODO add computing other statistics

    def speech_length_statistics(self):
        for role in self.total_length:
            # tables
            statistics_df = pd.DataFrame()
            for speaker in self.total_length[role]["word"]:
                statistics_df = statistics_df.append({
                    "speaker": speaker,
                    "word": self.total_length[role]["word"][speaker],
                    "sentence": self.total_length[role]["sentence"][speaker],
                    "paragraph": self.total_length[role]["paragraph"][speaker],
                    "utterance": self.total_length[role]["utterance"][speaker]
                }, ignore_index=True)

            filename = "total_length-" + role + ".txt"
            path = os.path.join(self.output_dir, filename)
            statistics_df.to_csv(path, index=False)

            # plots
            plot_df = pd.DataFrame()
            for stat in self.total_length[role]:
                for speaker in self.total_length[role][stat]:
                    val = self.total_length[role][stat][speaker]
                    plot_df = plot_df.append({
                        "speaker": speaker,
                        "stat": stat,
                        "length": val
                    }, ignore_index=True)

            sns.set_theme()
            sns.set_context("paper")
            sns_plot = sns.catplot(
                x="speaker",
                y="length",
                hue="stat",
                kind="bar",
                data=plot_df
            )
            sns_plot.set_xticklabels(rotation=90)

            filename = "total_length-" + role + ".png"
            path = os.path.join(self.output_dir, filename)
            sns_plot.savefig(path)

    def compute_total_length(self, row):
        speaker, role = row["speaker"], row["role"]
        self.check_speaker_role(speaker, role)

        self.total_length[role]["word"][speaker] += row["word"]
        self.total_length[role]["sentence"][speaker] += row["sentence"]
        self.total_length[role]["paragraph"][speaker] += row["paragraph"]
        self.total_length[role]["utterance"][speaker] += row["utterance"]

    def check_speaker_role(self, speaker, role):
        if not (role in self.total_length):
            self.total_length[role] = {
                "word": dict(),
                "sentence": dict(),
                "paragraph": dict(),
                "utterance": dict()
            }

        # it is enough to check just one field
        if not (speaker in self.total_length[role]["word"]):
            self.total_length[role]["word"][speaker] = 0
            self.total_length[role]["sentence"][speaker] = 0
            self.total_length[role]["paragraph"][speaker] = 0
            self.total_length[role]["utterance"][speaker] = 0

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

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 4:
        agg = Aggregator(args[0], args[1], args[2], args[3])
        agg.aggregate()
        agg.tables_plots()
    else:
        print("Incorrect number of args")

