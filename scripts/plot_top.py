#!/usr/bin/env python3

import sys

import pandas as pd

from src.plotter import Plotter

def plot_top(file_in, output_dir, number_top=5):
    data_df = pd.read_csv(file_in)

    roles = data_df.role.unique()
    for role in roles:
        role_df = data_df.loc[data_df["role"] == role]

        plot_total_length(role_df, number_top, file_in, output_dir)
        plot_relative_diff(role_df, number_top, file_in, output_dir)
        plot_unanchored(role_df, number_top, file_in, output_dir)
        plot_wpm(role_df, number_top, file_in, output_dir)

# TODO the functions are very similar; however, they differ in the Plotter
#      method used for plotting, which isn't that simple to pass as
#      parameter
def plot_total_length(role_df, number_top, file_in, output_dir):
    role_df = role_df.sort_values("length_utterance", ascending=False)

    n_select = min(number_top, len(role_df))
    top = role_df.iloc[:n_select, :]
    top_names = list(top.speaker)

    plotter = Plotter(file_in, output_dir, "speaker", top_names)
    plotter.plot_single(
        plotter.plot_total_length,
        sort_func=lambda plot_df: plot_df.sort_values(
            by=["length"],
            ascending=False
        ),
        labels_tight=True
    )

def plot_relative_diff(role_df, number_top, file_in, output_dir):
    role_df = role_df.sort_values("sentence-word", ascending=False)

    n_select = min(number_top, len(role_df))
    top = role_df.iloc[:n_select, :]
    top_names = list(top.speaker)

    plotter = Plotter(file_in, output_dir, "speaker", top_names)
    plotter.plot_single(
        plotter.plot_relative_diff,
        sort_func=sort_relative_diff,
        labels_tight=True
    )

def plot_unanchored(role_df, number_top, file_in, output_dir):
    role_df = role_df.sort_values("unanchored", ascending=False)

    n_select = min(number_top, len(role_df))
    top = role_df.iloc[:n_select, :]
    top_names = list(top.speaker)

    plotter = Plotter(file_in, output_dir, "speaker", top_names)
    plotter.plot_single(
        plotter.plot_unanchored,
        sort_func=lambda plot_df: plot_df.sort_values(
            by=["unanchored"],
            ascending=False
        ),
        labels_tight=True
    )

def plot_wpm(role_df, number_top, file_in, output_dir):
    role_df = role_df.sort_values("words_per_minute", ascending=False)

    n_select = min(number_top, len(role_df))
    top = role_df.iloc[:n_select, :]
    top_names = list(top.speaker)

    plotter = Plotter(file_in, output_dir, "speaker", top_names)
    plotter.plot_single(
        plotter.plot_wpm,
        sort_func=lambda plot_df: plot_df.sort_values(
            by=["words_per_minute"],
            ascending=False
        ),
        labels_tight=True
    )

def relative_diff_sorter(column):
    reorder = [
        "Utterance vs word",
        "Paragraph vs sentence",
        "Sentence vs word"
    ]

    cat = pd.Categorical(column, categories=reorder, ordered=True)
    return pd.Series(cat)

def sort_relative_diff(plot_df):
    plot_df = plot_df.sort_values(by=["difference"], ascending=False)
    plot_df = plot_df.sort_values(
        by=["statistic"],
        key=relative_diff_sorter,
        ascending=False
    )
    return plot_df

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        plot_top(args[0], args[1])
    else:
        print("Incorrect number of args")

