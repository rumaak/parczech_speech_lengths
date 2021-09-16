#!/usr/bin/env python3

import sys
import argparse
from datetime import datetime

from src.aggregator import CustomAggregator

# TODO change description

# The script expects paths to an audio file directory, an output directory
# and a time interval (two additional arguments, start and end). The script
# computes the statistics over the specified interval.
# 
# Example of proper datetime (ISO 8601):
# 2021-08-13T03:34:17
#
# Statistics of an audio are used only if both audio start and end belong
# to the said interval (makes more sense as audio files overlap)
#
# Note that as opposed to the audio files, the total speaking times (per word,
# sentence, paragraph, utterance) are measured in hours, not milliseconds.

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="path to audio file directory")
    parser.add_argument("output_dir", help="path to output directory")

    parser.add_argument("--start", type=datetime.fromisoformat, help="start of time interval")
    parser.add_argument("--end", type=datetime.fromisoformat, help="end of time interval")

    mutex = parser.add_mutually_exclusive_group()
    mutex.add_argument("--term", help="term")
    mutex.add_argument("--meeting", help="meeting")
    mutex.add_argument("--sitting", help="sitting")
    mutex.add_argument("--agenda", help="agenda")

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    aggregator = CustomAggregator(**vars(args)) 
    aggregator.aggregate()

