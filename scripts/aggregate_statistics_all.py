#!/usr/bin/env python3

import sys
from src.aggregator import TermAggregator

# The script expects paths to an audio file directory and an output directory.
# The script precomputes the statistics over election periods and saves
# them to the output directory.
#
# Note that as opposed to the audio files, the total speaking times (per word,
# sentence, paragraph, utterance) are measured in hours, not milliseconds.

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        agg = TermAggregator(args[0], args[1])
        agg.aggregate()
    else:
        print("Incorrect number of args")
