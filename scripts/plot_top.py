#!/usr/bin/env python3

import sys

import pandas as pd

from src.plotter import Plotter

# NOTES:
# - currently under development

# TODO:
# - all statistics -> split to individual functions
# - tweak plots
#   - names overlap
#   - sort from highest to lowest

def plot_top(file_in, output_dir, number_top=5):
    data_df = pd.read_csv(file_in)

    roles = data_df.role.unique()
    for role in roles:
        role_df = data_df.loc[data_df["role"] == role]
        role_df = role_df.sort_values("length_utterance", ascending=False)

        n_select = min(number_top, len(role_df))
        top = role_df.iloc[:n_select, :]
        top_names = list(top.speaker)

        plotter = Plotter(file_in, output_dir, "speaker", top_names)
        plotter.plot_single(plotter.plot_total_length)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        plot_top(args[0], args[1])
    else:
        print("Incorrect number of args")

