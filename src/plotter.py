import os
from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, file_in, output_dir, compare_by, mops):
        assert compare_by in ["speaker", "term"]

        self.file_in = file_in
        self.output_dir = output_dir
        self.mops = mops

        if compare_by == "speaker":
            self.x = "speaker"
            self.x_label = "Speaker"
        else:
            self.x = "election_period"
            self.x_label = "Election period"

    def plot(self):
        self.plot_single(self.plot_total_length)
        self.plot_single(self.plot_relative_diff)
        self.plot_single(self.plot_unanchored)
        self.plot_single(self.plot_wpm)

    def plot_single(self, plot_func, sort_func=None, labels_tight=False):
        if sort_func is None:
            sort_func = self.sort_default

        data_df = pd.read_csv(self.file_in)
        speaker_df = data_df.loc[data_df["speaker"].isin(self.mops)]

        # Plots are in general divided by role
        roles = speaker_df.role.unique()
        for role in roles:
            role_df = speaker_df.loc[speaker_df["role"] == role]

            # make sure directory exists
            path_to_dir = os.path.join(self.output_dir, role)
            Path(path_to_dir).mkdir(parents=True, exist_ok=True)

            # plot
            plot_func(role_df, path_to_dir, sort_func, labels_tight)

    def plot_total_length(self, role_df, path_to_dir, sort_func, labels_tight):
        length_stats = [
            "length_word",
            "length_sentence",
            "length_paragraph",
            "length_utterance"
        ]

        stats_labels = {
            "length_word": "Words",
            "length_sentence": "Sentences",
            "length_paragraph": "Paragraphs",
            "length_utterance": "Utterances"
        }

        plot_df = pd.DataFrame()
        for stat in length_stats:
            stat_df = role_df.loc[:,["speaker","election_period",stat]]
            stat_df["statistic"] = stats_labels[stat]
            stat_df.rename(columns={stat: "length"}, inplace=True)
            plot_df = pd.concat([plot_df, stat_df])
        plot_df = sort_func(plot_df)
        plot_df.rename(columns={"statistic": "Measured across"}, inplace=True)


        sns.set_theme()
        sns_plot = sns.catplot(
            x=self.x,
            y="length",
            hue="Measured across",
            kind="bar",
            data=plot_df
        )
        sns_plot.set_axis_labels(x_var=self.x_label, y_var="Speaking time [h]")
        self.set_xticks_tight(sns_plot, labels_tight)

        path = os.path.join(path_to_dir, "total_length.png")
        sns_plot.savefig(path)

    def plot_relative_diff(self, role_df, path_to_dir, sort_func, labels_tight):
        diff_stats = [
            "utterance-paragraph",
            "paragraph-sentence",
            "sentence-word"
        ]

        stats_labels = {
            "utterance-paragraph": "Utterance vs paragraph",
            "paragraph-sentence": "Paragraph vs sentence",
            "sentence-word": "Sentence vs word"
        }

        plot_df = pd.DataFrame()
        for stat in diff_stats:
            stat_df = role_df.loc[:,["speaker","election_period",stat]]
            stat_df["statistic"] = stats_labels[stat]
            stat_df.rename(columns={stat: "difference"}, inplace=True)
            plot_df = pd.concat([plot_df, stat_df])
        plot_df = sort_func(plot_df)
        plot_df.rename(columns={"statistic": "Comparing"}, inplace=True)

        sns.set_theme()
        sns_plot = sns.catplot(
            x=self.x,
            y="difference",
            hue="Comparing",
            kind="bar",
            data=plot_df
        )
        sns_plot.set_axis_labels(x_var=self.x_label, y_var="Relative difference")
        self.set_xticks_tight(sns_plot, labels_tight)

        path = os.path.join(path_to_dir, "relative_diff.png")
        sns_plot.savefig(path)

    def plot_unanchored(self, role_df, path_to_dir, sort_func, labels_tight):
        plot_df = sort_func(role_df)

        sns.set_theme()
        sns_plot = sns.catplot(
            x=self.x,
            y="unanchored",
            kind="bar",
            data=plot_df
        )
        sns_plot.set_axis_labels(x_var=self.x_label, y_var="Percentage of unanchored words")
        self.set_xticks_tight(sns_plot, labels_tight)

        path = os.path.join(path_to_dir, "unanchored.png")
        sns_plot.savefig(path)

    def plot_wpm(self, role_df, path_to_dir, sort_func, labels_tight):
        plot_df = sort_func(role_df)

        sns.set_theme()
        sns_plot = sns.catplot(
            x=self.x,
            y="words_per_minute",
            kind="bar",
            data=plot_df
        )
        sns_plot.set_axis_labels(x_var=self.x_label, y_var="Words per minute")
        self.set_xticks_tight(sns_plot, labels_tight)

        path = os.path.join(path_to_dir, "wpm.png")
        sns_plot.savefig(path)

    def set_xticks_tight(self, plot, labels_tight):
        if labels_tight:
            # exploiting the underlying library isn't the best practice
            # but there really isn't other option
            for axes in plot.axes.flat:
                axes.set_xticklabels(
                    axes.get_xticklabels(),
                    rotation=35,
                    horizontalalignment='right'
                )


    def sort_default(self, plot_df):
        plot_df = plot_df.sort_values(by=[self.x], ascending=True)
        return plot_df

