#!/usr/bin/env python3

import sys
import os
import os.path
import math
from datetime import datetime, timedelta, date, time
from pathlib import Path
from glob import glob

import pandas as pd

# Several metrics of speech lengths are used, namely:
# - sum of word lengths over all words of given speaker
# - difference between first and last anchor of a sentence
# - difference between first and last anchor of a paragraph
# - difference between first and last anchor of an utterance
# - difference between first and last anchor of an uninterrupted speech

# TODO should we also include audio start / audio end if it can be inferred
#      from the name of the file?

class Parser:
    def __init__(self, file_in, dir_out):
        self.file_in = file_in
        self.dir_out = dir_out

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

        self.previous_audio = None
        self.audio_start = None
        self.audio_end = None
        self.audio_first_anchor = None
        self.audio_last_anchor = None

    def parse(self):
        data_df = pd.read_csv(self.file_in, sep="\t")

        # extract data from each row
        data_df.apply(self.parse_row, axis=1)

        # write statistics to a file
        self.save_audio()

    def create_statistics_df(self):
        statistics_df = pd.DataFrame(columns=[
            "speaker",
            "role",
            "audio_start",
            "audio_end",
            # TODO keep?
            # "first_anchor",
            # "last_anchor",
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
                    "audio_start": self.audio_start.strftime("%Y-%m-%dT%H:%M:%S"),
                    "audio_end": self.audio_end.strftime("%Y-%m-%dT%H:%M:%S"),
                    # TODO keep?
                    # "first_anchor": self.audio_first_anchor,
                    # "last_anchor": self.audio_last_anchor,
                    "word": role_stats["word"],
                    "sentence": role_stats["sentence"],
                    "paragraph": role_stats["paragraph"],
                    "utterance": role_stats["utterance"],
                    "continuous": role_stats["continuous"]
                }, ignore_index=True)

        return statistics_df

    def finish(self, speaker, role):
        self.finish_continuous(speaker, role)
        self.finish_segment("sentence", speaker, role)
        self.finish_segment("paragraph", speaker, role)
        self.finish_segment("utterance", speaker, role)

    def finish_continuous(self, speaker, role):
        speaker_l = self.last_continuous["speaker"]
        role_l = self.last_continuous["role"]
        beg_l = self.last_continuous["beg"]
        end_l = self.last_continuous["end"]

        if speaker_l is not None:
            if beg_l is not None:
                length = (end_l - beg_l).total_seconds()*1000
                self.statistics[speaker_l][role_l]["continuous"] += length

        self.last_continuous["speaker"] = speaker
        self.last_continuous["role"] = role
        self.last_continuous["beg"] = None
        self.last_continuous["end"] = None

    def finish_segment(self, seg_name, speaker, role):
        speaker_l = self.last_segment[seg_name]["speaker"]
        role_l = self.last_segment[seg_name]["role"]
        beg_l = self.last_segment[seg_name]["beg"]
        end_l = self.last_segment[seg_name]["end"]

        if speaker_l is not None:
            if beg_l is not None:
                length = (end_l - beg_l).total_seconds()*1000
                self.statistics[speaker_l][role_l][seg_name] += length

        self.last_segment[seg_name]["speaker"] = speaker
        self.last_segment[seg_name]["role"] = role
        self.last_segment[seg_name]["beg"] = None
        self.last_segment[seg_name]["end"] = None
        
    def parse_row(self, row):
        self.check_audio(row["audio_url"])
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

        # TODO absolute timestamps are unnecessary after we switched from
        # counting over single TEI file to counting over single audio file

        # use absolute timestamps
        start = self.to_absolute(row["start"], row["absolute"])
        end = self.to_absolute(row["end"], row["absolute"])

        self.update_word(start, end, row["speaker"], row["role"])
        self.update_segment(start, end, row["speaker"], row["role"], sc, sl, "sentence")
        self.update_segment(start, end, row["speaker"], row["role"], pc, pl, "paragraph")
        self.update_segment(start, end, row["speaker"], row["role"], uc, ul, "utterance")
        self.update_continuous(start, end, row["speaker"], row["role"])

        self.last = row["id"]

        # for words missing audio_url, assume previous audio_url
        if type(row["audio_url"]) != float: 
            self.previous_audio = row["audio_url"]
            self.audio_start_end(row["audio_url"])
            self.update_audio_anchors(start, end)

    def audio_start_end(self, audio_url):
        datetime_string = audio_url.split("/")[-1]

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

        self.audio_start = datetime.combine(d, time_start)
        self.audio_end = datetime.combine(d, time_end)

    def update_audio_anchors(self, start, end):
        if self.audio_first_anchor is None: 
            if start is not None:
                self.audio_first_anchor = start.strftime("%Y-%m-%dT%H:%M:%S")
            elif end is not None:
                self.audio_first_anchor = end.strftime("%Y-%m-%dT%H:%M:%S")

        if end is not None:
            self.audio_last_anchor = end.strftime("%Y-%m-%dT%H:%M:%S")
        elif start is not None:
            self.audio_last_anchor = start.strftime("%Y-%m-%dT%H:%M:%S")

    def check_audio(self, audio_url):
        # different audio
        if (self.previous_audio != audio_url) and (type(audio_url) != float):
            self.save_audio()

    def save_audio(self):
        if self.previous_audio is not None:
            # finish counting
            self.finish_continuous(
                self.last_continuous["speaker"],
                self.last_continuous["role"]
            )
            self.finish_segment("sentence",
                self.last_segment["sentence"]["speaker"],
                self.last_segment["sentence"]["role"]
            )
            self.finish_segment("paragraph",
                self.last_segment["paragraph"]["speaker"],
                self.last_segment["paragraph"]["role"]
            )
            self.finish_segment("utterance",
                self.last_segment["utterance"]["speaker"],
                self.last_segment["utterance"]["role"]
            )

            # audio already exists -> update statistics
            path = self.construct_path()
            if os.path.exists(path):
                self.update_from_existing(path)

            # create dataframe from computed values, save
            statistics_df = self.create_statistics_df()
            statistics_df.to_csv(path, index=False)

            # reset statistics
            self.statistics = dict()

    def construct_path(self):
        year = self.audio_start.strftime("%Y")
        month = self.audio_start.strftime("%m")
        day = self.audio_start.strftime("%d")

        hour_start = self.audio_start.strftime("%H")
        minute_start = self.audio_start.strftime("%M")

        hour_end = self.audio_end.strftime("%H")
        minute_end = self.audio_end.strftime("%M")

        name_first = year + month + day
        name_last = hour_start + minute_start + hour_end + minute_end

        path_to_dir = os.path.join(
            self.dir_out,
            year,
            month,
            day
        )
        
        Path(path_to_dir).mkdir(parents=True, exist_ok=True)
        return os.path.join(path_to_dir, name_first + name_last + ".txt")

    def update_from_existing(self, path):
        existing_df = pd.read_csv(path)
        existing_df.apply(self.update_from_row, axis=1)

    def update_from_row(self, row):
        speaker = row["speaker"]
        role = row["role"]

        # ensure given speaker + role exist
        self.check_speaker_role(speaker, role)

        # get current values
        word = self.statistics[speaker][role]["word"]
        sentence = self.statistics[speaker][role]["sentence"]
        paragraph = self.statistics[speaker][role]["paragraph"]
        utterance = self.statistics[speaker][role]["utterance"]
        continuous = self.statistics[speaker][role]["continuous"]

        # update with values from file
        self.statistics[speaker][role]["word"] = word + row["word"]
        self.statistics[speaker][role]["sentence"] = word + row["sentence"]
        self.statistics[speaker][role]["paragraph"] = word + row["paragraph"]
        self.statistics[speaker][role]["utterance"] = word + row["utterance"]
        self.statistics[speaker][role]["continuous"] = word + row["continuous"]

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
            self.finish_segment(seg_name, speaker, role)

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
            self.finish_continuous(speaker, role)

    def to_absolute(self, interval, absolute):
        # check if either value is not nan
        if (not math.isnan(interval)) and type(absolute) != float:
            dt = datetime.strptime(absolute, "%Y-%m-%dT%H:%M:%S")
            return dt + timedelta(milliseconds=interval)
        else:
            return None

if __name__ == "__main__":
    # The script expects path to the input file as well as a path to a
    # directory where statistics for each audio should be stored
    args = sys.argv[1:]
    if len(args) == 2:
        # Windows-compatible pattern matching
        filelist = glob(args[0]) 
        for filename in filelist:
            parser = Parser(filename, args[1])
            parser.parse()
    else:
        print("Incorrect number of args")

