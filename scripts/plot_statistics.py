#!/usr/bin/env python3

import sys
import os
from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# The script expects paths to a file with precomputed values, an output
# directory, a string indicating whether we want to compare between MoPs
# or election periods, and ids of one or more MoPs. It generates plots for
# these particular MoPs.
#
# The indication string can have one of two values:
# speaker
# term

class Plotter:
    def __init__(self, file_in, output_dir, compare_by, mops):
        assert compare_by in ["speaker", "term"]

        self.file_in = file_in
        self.output_dir = output_dir
        self.mops = mops

        if compare_by == "speaker":
            self.x = "speaker"
        else:
            self.x = "election_period"

        if len(mops) == 1:
            self.dir_name = mops[0]
        else:
            self.dir_name = "multiple"


    def plot(self):
        data_df = pd.read_csv(self.file_in)
        speaker_df = data_df.loc[data_df["speaker"].isin(self.mops)]

        # Plots are in general divided by role
        roles = speaker_df.role.unique()
        for role in roles:
            role_df = speaker_df.loc[speaker_df["role"] == role]

            # make sure directory exists
            path_to_dir = os.path.join(self.output_dir, self.dir_name, role)
            Path(path_to_dir).mkdir(parents=True, exist_ok=True)

            # plots
            self.plot_total_length(role_df, path_to_dir)
            self.plot_relative_diff(role_df, path_to_dir)
            self.plot_unanchored(role_df, path_to_dir)
            self.plot_wpm(role_df, path_to_dir)

    def plot_total_length(self, role_df, path_to_dir):
        length_stats = [
            "length_word",
            "length_sentence",
            "length_paragraph",
            "length_utterance",
        ]

        plot_df = pd.DataFrame()
        for stat in length_stats:
            stat_df = role_df.loc[:,["speaker","election_period",stat]]
            stat_df["statistic"] = stat
            stat_df.rename(columns={stat: "length"}, inplace=True)
            plot_df = pd.concat([plot_df, stat_df])
        plot_df = plot_df.sort_values(by=[self.x], ascending=True)

        sns.set_theme()
        sns_plot = sns.catplot(
            x=self.x,
            y="length",
            hue="statistic",
            kind="bar",
            data=plot_df
        )

        path = os.path.join(path_to_dir, "total_length.png")
        sns_plot.savefig(path)

    def plot_relative_diff(self, role_df, path_to_dir):
        diff_stats = [
            "utterance-paragraph",
            "paragraph-sentence",
            "sentence-word"
        ]

        plot_df = pd.DataFrame()
        for stat in diff_stats:
            stat_df = role_df.loc[:,["speaker","election_period",stat]]
            stat_df["statistic"] = stat
            stat_df.rename(columns={stat: "difference"}, inplace=True)
            plot_df = pd.concat([plot_df, stat_df])
        plot_df = plot_df.sort_values(by=[self.x], ascending=True)

        sns.set_theme()
        sns_plot = sns.catplot(
            x=self.x,
            y="difference",
            hue="statistic",
            kind="bar",
            data=plot_df
        )

        path = os.path.join(path_to_dir, "relative_diff.png")
        sns_plot.savefig(path)

    def plot_unanchored(self, role_df, path_to_dir):
        plot_df = role_df.sort_values(by=[self.x], ascending=True)

        sns.set_theme()
        sns_plot = sns.catplot(
            x=self.x,
            y="unanchored",
            kind="bar",
            data=plot_df
        )

        path = os.path.join(path_to_dir, "unanchored.png")
        sns_plot.savefig(path)

    def plot_wpm(self, role_df, path_to_dir):
        plot_df = role_df.sort_values(by=[self.x], ascending=True)

        sns.set_theme()
        sns_plot = sns.catplot(
            x=self.x,
            y="words_per_minute",
            kind="bar",
            data=plot_df
        )

        path = os.path.join(path_to_dir, "wpm.png")
        sns_plot.savefig(path)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 4:
        plotter = Plotter(args[0], args[1], args[2], args[3:])
        plotter.plot()
    else:
        print("Incorrect number of args")

