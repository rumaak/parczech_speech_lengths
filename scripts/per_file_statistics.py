#!/usr/bin/env python3

import sys
import os
import math
from datetime import datetime, timedelta

import pandas as pd

# Several metrics of speech lengths are used, namely:
# - sum of word lengths over all words of given speaker
# - difference between first and last anchor of a sentence
# - difference between first and last anchor of a paragraph
# - difference between first and last anchor of an utterance
# - difference between first and last anchor of an uninterrupted speech

class Parser:
    def __init__(self, file_in, file_out):
        self.file_in = file_in
        self.file_out = file_out

        # TODO in future maybe replace directly by dataframe
        self.statistics = dict()

        self.last_continuous = {
            "speaker": None,
            "role": None,
            "beg": None,
            "end": None
        }

        self.last_segment = {
            "sentence": {
                "speaker": None,
                "role": None,
                "beg": None,
                "end": None
            },
            "paragraph": {
                "speaker": None,
                "role": None,
                "beg": None,
                "end": None
            },
            "utterance": {
                "speaker": None,
                "role": None,
                "beg": None,
                "end": None
            }
        }

        self.last = None

    def parse(self):
        data_df = pd.read_csv(self.file_in, sep="\t")

        # extract data from each row
        data_df.apply(self.parse_row, axis=1)
        self.finish()

        # create dataframe from computed values
        statistics_df = self.create_statistics_df()

        # write statistics to a file
        statistics_df.to_csv(self.file_out, index=False)

    def create_statistics_df(self):
        statistics_df = pd.DataFrame(columns=[
            "speaker",
            "role",
            "word",
            "sentence",
            "paragraph",
            "utterance",
            "continuous"
        ])

        for name in self.statistics:
            person_stats = self.statistics[name]
            for role in person_stats:
                role_stats = person_stats[role]
                statistics_df = statistics_df.append({
                    "speaker": name,
                    "role": role,
                    "word": role_stats["word"],
                    "sentence": role_stats["sentence"],
                    "paragraph": role_stats["paragraph"],
                    "utterance": role_stats["utterance"],
                    "continuous": role_stats["continuous"]
                }, ignore_index=True)

        return statistics_df

    def finish(self):
        # finish continuous
        speaker_l = self.last_continuous["speaker"]
        role_l = self.last_continuous["role"]
        beg_l = self.last_continuous["beg"]
        end_l = self.last_continuous["end"]

        if speaker_l is not None:
            if beg_l is not None:
                length = (end_l - beg_l).total_seconds()*1000
                self.statistics[speaker_l][role_l]["continuous"] += length

        # finish sentence, paragraph, utterance
        self.finish_segment("sentence")
        self.finish_segment("paragraph")
        self.finish_segment("utterance")

    def finish_segment(self, seg_name):
        # finish continuous
        speaker_l = self.last_segment[seg_name]["speaker"]
        role_l = self.last_segment[seg_name]["role"]
        beg_l = self.last_segment[seg_name]["beg"]
        end_l = self.last_segment[seg_name]["end"]

        if speaker_l is not None:
            if beg_l is not None:
                length = (end_l - beg_l).total_seconds()*1000
                self.statistics[speaker_l][role_l][seg_name] += length
        
    def parse_row(self, row):
        self.check_speaker_role(row["speaker"], row["role"])

        # current utterance, paragraph, sentence
        id_parts = row["id"].split(".")
        uc = ".".join(id_parts[:2])
        pc = ".".join(id_parts[:3])
        sc = ".".join(id_parts[:4])

        # last utterance, paragraph, sentence
        sl,pl,ul = None, None, None
        if self.last is not None:
            id_parts = self.last.split(".")
            ul = ".".join(id_parts[:2])
            pl = ".".join(id_parts[:3])
            sl = ".".join(id_parts[:4])

        start = self.to_absolute(row["start"], row["absolute"])
        end = self.to_absolute(row["end"], row["absolute"])

        self.update_word(start, end, row["speaker"], row["role"])
        self.update_segment(start, end, row["speaker"], row["role"], sc, sl, "sentence")
        self.update_segment(start, end, row["speaker"], row["role"], pc, pl, "paragraph")
        self.update_segment(start, end, row["speaker"], row["role"], uc, ul, "utterance")
        self.update_continuous(start, end, row["speaker"], row["role"])

        self.last = row["id"]

    def check_speaker_role(self, speaker, role):
        if not (speaker in self.statistics):
            self.statistics[speaker] = {
                role: {
                    "word": 0,
                    "sentence": 0,
                    "paragraph": 0,
                    "utterance": 0,
                    "continuous": 0
                }
            }
        elif not (role in self.statistics[speaker]):
            self.statistics[speaker][role] = {
                "word": 0,
                "sentence": 0,
                "paragraph": 0,
                "utterance": 0,
                "continuous": 0
            }

    def update_word(self, start, end, speaker, role):
        if (start is not None) and (end is not None):
            word_length = (end - start).total_seconds()*1000
            self.statistics[speaker][role]["word"] += word_length

    def update_segment(self, start, end, speaker, role, sc, sl, seg_name):
        speaker_l = self.last_segment[seg_name]["speaker"]
        role_l = self.last_segment[seg_name]["role"]
        beg_l = self.last_segment[seg_name]["beg"]
        end_l = self.last_segment[seg_name]["end"]

        # same segment -> update start / end anchor
        if sc == sl:
            # missing beginning anchor
            if beg_l is None:
                if start is not None:
                    self.last_segment[seg_name]["beg"] = start
                elif end is not None:
                    self.last_segment[seg_name]["beg"] = end

            # update ending anchor
            if end is not None:
                self.last_segment[seg_name]["end"] = end
            elif start is not None:
                self.last_segment[seg_name]["end"] = start

        # different segment - finish last one, initialize values for new one
        else:
            if speaker_l is not None:
                if beg_l is not None:
                    length = (end_l - beg_l).total_seconds()*1000
                    self.statistics[speaker_l][role_l][seg_name] += length

            self.last_segment[seg_name]["speaker"] = speaker
            self.last_segment[seg_name]["role"] = role
            self.last_segment[seg_name]["beg"] = None
            self.last_segment[seg_name]["end"] = None

    def update_continuous(self, start, end, speaker, role):
        speaker_l = self.last_continuous["speaker"]
        role_l = self.last_continuous["role"]
        beg_l = self.last_continuous["beg"]
        end_l = self.last_continuous["end"]

        # same speaker -> update start / end anchor
        if speaker == speaker_l and role == role_l:
            # missing beginning anchor
            if beg_l is None:
                if start is not None:
                    self.last_continuous["beg"] = start
                elif end is not None:
                    self.last_continuous["beg"] = end

            # update ending anchor
            if end is not None:
                self.last_continuous["end"] = end
            elif start is not None:
                self.last_continuous["end"] = start

        # different speaker - finish last one, initialize values for new one
        else:
            if speaker_l is not None:
                if beg_l is not None:
                    length = (end_l - beg_l).total_seconds()*1000
                    self.statistics[speaker_l][role_l]["continuous"] += length

            self.last_continuous["speaker"] = speaker
            self.last_continuous["role"] = role
            self.last_continuous["beg"] = None
            self.last_continuous["end"] = None

    def to_absolute(self, interval, absolute):
        # check if either value is not nan
        if (not math.isnan(interval)) and type(absolute) != float:
            dt = datetime.strptime(absolute, "%Y-%m-%dT%H:%M:%S")
            return dt + timedelta(milliseconds=interval)
        else:
            return None

if __name__ == "__main__":
    # The script expects paths to input and output file as arguments
    args = sys.argv[1:]
    if len(args) == 2:
        parser = Parser(args[0], args[1])
        parser.parse()
    else:
        print("Incorrect number of args")

