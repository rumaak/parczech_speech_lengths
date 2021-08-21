#!/usr/bin/env python3

import sys
import os
from datetime import datetime, date, time
from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



# TODO THIS SCRIPT SHOULDN'T BE USED AS OF RIGHT NOW



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
        self.output_dir = self.resolve_output_dir(output_dir)

        self.total_length = dict()
        self.relative_diff = dict()
        self.words = dict()

    def resolve_output_dir(self, output_dir):
        start = self.start.strftime("%Y%m%d%H%M")
        end = self.end.strftime("%Y%m%d%H%M")

        path_to_dir = os.path.join(
            output_dir,
            start + "-" + end
        )

        return path_to_dir

    def tables_plots(self):
        self.speech_length_statistics()
        self.relative_diff_statistics()
        self.word_statistics()

        # TODO add plotting other statistics

    def aggregate(self):
        for audio in self.correct_audios():
            data_df = pd.read_csv(audio)
            data_df.apply(self.compute_total_length, axis=1)
            data_df.apply(self.compute_relative_difference, axis=1)
            data_df.apply(self.compute_word_statistics, axis=1)

            # TODO add computing other statistics

    def word_statistics(self):
        for role in self.words:
            # make sure directory exists
            path_to_dir = os.path.join(self.output_dir, "words")
            Path(path_to_dir).mkdir(parents=True, exist_ok=True)

            # tables
            statistics_df = pd.DataFrame()
            for speaker in self.words[role]["word_count"]:
                count = self.words[role]["word_count"][speaker]
                anchor = self.words[role]["no_anchor"][speaker]
                length = self.total_length[role]["utterance"][speaker]

                statistics_df = statistics_df.append({
                    "speaker": speaker,
                    "unanchored": anchor / count,
                    "words_per_minute": count / self.to_minutes(length)
                }, ignore_index=True)

            path = os.path.join(path_to_dir, role + ".txt")
            statistics_df.to_csv(path, index=False)

            # plots
            plot1_df = pd.DataFrame()
            plot2_df = pd.DataFrame()
            for speaker in self.words[role]["word_count"]:
                count = self.words[role]["word_count"][speaker]
                anchor = self.words[role]["no_anchor"][speaker]
                length = self.total_length[role]["utterance"][speaker]

                plot1_df = plot1_df.append({
                    "speaker": speaker,
                    "unanchored": anchor / count
                }, ignore_index=True)

                plot2_df = plot2_df.append({
                    "speaker": speaker,
                    "words_per_minute": count / self.to_minutes(length)
                }, ignore_index=True)

            plot1_df = plot1_df.sort_values(by=["unanchored"], ascending=False)
            plot2_df = plot2_df.sort_values(by=["words_per_minute"], ascending=False)

            # unanchored plot
            sns.set_theme()
            sns.set_context("paper")
            sns_plot = sns.catplot(
                x="speaker",
                y="unanchored",
                kind="bar",
                data=plot1_df
            )
            sns_plot.set_xticklabels(rotation=90)

            path = os.path.join(path_to_dir, role + "-unanchored" + ".png")
            sns_plot.savefig(path)
            plt.clf()

            # words_per_minute plot
            sns.set_theme()
            sns.set_context("paper")
            sns_plot = sns.catplot(
                x="speaker",
                y="words_per_minute",
                kind="bar",
                data=plot2_df
            )
            sns_plot.set_xticklabels(rotation=90)

            path = os.path.join(path_to_dir, role + "-wpm" + ".png")
            sns_plot.savefig(path)

    def to_minutes(self, length):
        seconds = length / 1000
        minutes = seconds / 60
        return minutes

    def relative_diff_statistics(self):
        for role in self.total_length:
            # make sure directory exists
            path_to_dir = os.path.join(self.output_dir, "relative_diff")
            Path(path_to_dir).mkdir(parents=True, exist_ok=True)

            # tables
            statistics_df = pd.DataFrame()
            for speaker in self.relative_diff[role]["sentence-word"]:
                sw = self.calculate_rel_diff(speaker, role, "sentence-word", "sentence")
                ps = self.calculate_rel_diff(speaker, role, "paragraph-sentence", "paragraph")
                up = self.calculate_rel_diff(speaker, role, "utterance-paragraph", "utterance")

                statistics_df = statistics_df.append({
                    "speaker": speaker,
                    "sentence-word": sw,
                    "paragraph-sentence": ps,
                    "utterance-paragraph": up
                }, ignore_index=True)

            path = os.path.join(path_to_dir, role + ".txt")
            statistics_df.to_csv(path, index=False)

            # plots
            plot_df = pd.DataFrame()
            for stat in self.relative_diff[role]:
                for speaker in self.relative_diff[role][stat]:
                    val = self.calculate_rel_diff(
                        speaker, 
                        role, 
                        stat, 
                        self.decide_stat_total(stat)
                    )
                    plot_df = plot_df.append({
                        "speaker": speaker,
                        "stat": stat,
                        "difference": val
                    }, ignore_index=True)
            plot_df = plot_df.sort_values(by=["difference"], ascending=False)

            sns.set_theme()
            sns.set_context("paper")
            sns_plot = sns.catplot(
                x="speaker",
                y="difference",
                hue="stat",
                kind="bar",
                data=plot_df
            )
            sns_plot.set_xticklabels(rotation=90)

            path = os.path.join(path_to_dir, role + ".png")
            sns_plot.savefig(path)

    def decide_stat_total(self, stat):
        return stat.split("-")[0]

    def calculate_rel_diff(self, speaker, role, stat, stat_total):
        total_diff = self.relative_diff[role][stat][speaker]
        total_length = self.total_length[role][stat_total][speaker]
        rel_diff =  total_diff / total_length
        return rel_diff

    def speech_length_statistics(self):
        for role in self.total_length:
            # make sure directory exists
            path_to_dir = os.path.join(self.output_dir, "total_length")
            Path(path_to_dir).mkdir(parents=True, exist_ok=True)

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

            path = os.path.join(path_to_dir, role + ".txt")
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
            plot_df = plot_df.sort_values(by=["length"], ascending=False)

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

            path = os.path.join(path_to_dir, role + ".png")
            sns_plot.savefig(path)

    def compute_word_statistics(self, row):
        speaker, role = row["speaker"], row["role"]
        self.check_speaker_role_word(speaker, role)
        
        self.words[role]["word_count"][speaker] += row["word_count"]
        self.words[role]["no_anchor"][speaker] += row["no_anchor"]

    def compute_relative_difference(self, row):
        speaker, role = row["speaker"], row["role"]
        self.check_speaker_role_diff(speaker, role)

        up = self.relative_diff[role]["utterance-paragraph"]
        ps = self.relative_diff[role]["paragraph-sentence"]
        sw = self.relative_diff[role]["sentence-word"]

        up[speaker] += row["utterance"] - row["paragraph"]
        ps[speaker] += row["paragraph"] - row["sentence"]
        sw[speaker] += row["sentence"] - row["word"]

    def compute_total_length(self, row):
        speaker, role = row["speaker"], row["role"]
        self.check_speaker_role_length(speaker, role)

        self.total_length[role]["word"][speaker] += row["word"]
        self.total_length[role]["sentence"][speaker] += row["sentence"]
        self.total_length[role]["paragraph"][speaker] += row["paragraph"]
        self.total_length[role]["utterance"][speaker] += row["utterance"]

    def check_speaker_role_word(self, speaker, role):
        if not (role in self.words):
            self.words[role] = {
                "word_count": dict(),
                "no_anchor": dict()
            }

        # it is enough to check just one field
        if not (speaker in self.words[role]["word_count"]):
            self.words[role]["word_count"][speaker] = 0
            self.words[role]["no_anchor"][speaker] = 0

    def check_speaker_role_diff(self, speaker, role):
        if not (role in self.relative_diff):
            self.relative_diff[role] = {
                "utterance-paragraph": dict(),
                "paragraph-sentence": dict(),
                "sentence-word": dict()
            }

        # it is enough to check just one field
        if not (speaker in self.relative_diff[role]["sentence-word"]):
            self.relative_diff[role]["utterance-paragraph"][speaker] = 0
            self.relative_diff[role]["paragraph-sentence"][speaker] = 0
            self.relative_diff[role]["sentence-word"][speaker] = 0

    def check_speaker_role_length(self, speaker, role):
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
    # Compute over specified interval
    if len(args) == 4:
        agg = IntervalAggregator(args[0], args[1], args[2], args[3])
        agg.aggregate()
        agg.tables_plots()
    else:
        print("Incorrect number of args")
