#!/usr/bin/env python3

import sys

from src.plotter import Plotter

# The script expects paths to a file with precomputed values, an output
# directory, a string indicating whether we want to compare between MoPs
# or election periods, and ids of one or more MoPs. It generates plots for
# these particular MoPs.
#
# The indication string can have one of two values:
# speaker
# term

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 4:
        plotter = Plotter(args[0], args[1], args[2], args[3:])
        plotter.plot()
    else:
        print("Incorrect number of args")

