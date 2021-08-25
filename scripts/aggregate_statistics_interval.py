#!/usr/bin/env python3

import sys
from src.aggregator import IntervalAggregator

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

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 4:
        agg = IntervalAggregator(args[0], args[1], args[2], args[3])
        agg.aggregate()
    else:
        print("Incorrect number of args")
