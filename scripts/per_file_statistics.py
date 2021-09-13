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

class Parser:
    def __init__(self, file_in, dir_out):
        self.file_in = file_in
        self.dir_out = dir_out

        self.statistics = dict()

        self.last_continuous = {
            "beg": None,
            "end": None
        }

        self.last_segment = {
            "sentence": {
                "beg": None,
                "end": None
            },
            "paragraph": {
                "beg": None,
                "end": None
            },
            "utterance": {
                "beg": None,
                "end": None
            }
        }

        self.last_speaker = None
        self.last_role = None

        self.last = None

        self.previous_audio = None
        self.audio_start = None
        self.audio_end = None

        self.last_term = None
        self.last_meeting = None
        self.last_sitting = None
        self.last_agenda = None

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
            "election_period",
            "meeting",
            "sitting",
            "agenda",
            "word",
            "sentence",
            "paragraph",
            "utterance",
            "continuous",
            "word_count",
            "no_anchor"
        ])

        for key in self.statistics:
            speaker, role, election_period, meeting, sitting, agenda = key
            stats = self.statistics[key]
            statistics_df = statistics_df.append({
                "speaker": speaker,
                "role": role,
                "election_period": election_period,
                "meeting": meeting,
                "sitting": sitting,
                "agenda": agenda,
                "word": stats["word"],
                "sentence": stats["sentence"],
                "paragraph": stats["paragraph"],
                "utterance": stats["utterance"],
                "continuous": stats["continuous"],
                "word_count": stats["word_count"],
                "no_anchor": stats["no_anchor"]
            }, ignore_index=True)

        return statistics_df

    def finish(self):
        self.finish_continuous()
        self.finish_segment("sentence")
        self.finish_segment("paragraph")
        self.finish_segment("utterance")

    def finish_continuous(self):
        key = self.key_last()
        beg = self.last_continuous["beg"]
        end = self.last_continuous["end"]

        if not (None in key):
            if beg is not None:
                length = (end - beg).total_seconds()*1000
                self.statistics[key]["continuous"] += length

        self.last_continuous["beg"] = None
        self.last_continuous["end"] = None

    def finish_segment(self, seg_name):
        key = self.key_last()
        beg = self.last_segment[seg_name]["beg"]
        end = self.last_segment[seg_name]["end"]

        if not (None in key):
            if beg is not None:
                length = (end - beg).total_seconds()*1000
                self.statistics[key][seg_name] += length

        self.last_segment[seg_name]["beg"] = None
        self.last_segment[seg_name]["end"] = None
        
    def parse_row(self, row):
        key = self.key_from_row(row)
        self.check_audio(row["audio_url"])
        self.check_statistics(key)

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

        # update word statistics
        self.update_word(start, end, key)
        self.update_word_count(key)
        self.update_missing_anchors(start, end, key)

        # update first and last anchors of segments
        self.update_segment(start, end, sc, sl, "sentence")
        self.update_segment(start, end, pc, pl, "paragraph")
        self.update_segment(start, end, uc, ul, "utterance")
        self.update_continuous(start, end, row["speaker"], row["role"])

        self.last = row["id"]

        # for words missing audio_url, assume previous audio_url
        if type(row["audio_url"]) != float: 
            self.previous_audio = row["audio_url"]
            self.audio_start_end(row["audio_url"])

        # remember election period, meeting, sitting, and agenda
        self.last_term = key[2]
        self.last_meeting = key[3]
        self.last_sitting = key[4]
        self.last_agenda = key[5]

        # remember last speaker, role
        self.last_speaker = key[0]
        self.last_role = key[1]

    # TODO this time of time striping is used in both scripts, consider
    #      creating a shared helper module
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

    def check_audio(self, audio_url):
        # different audio
        if (self.previous_audio != audio_url) and (type(audio_url) != float):
            self.save_audio()

    def save_audio(self):
        if self.previous_audio is not None:
            # finish counting
            self.finish_continuous()
            self.finish_segment("sentence")
            self.finish_segment("paragraph")
            self.finish_segment("utterance")

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
        # ensure key exists in the statistics object
        key = (
            row["speaker"],
            row["role"],
            row["election_period"],
            row["meeting"],
            row["sitting"],
            row["agenda"]
        )
        self.check_statistics(key)

        # get current values
        fields = {
            "word": None,
            "sentence": None,
            "paragraph": None,
            "utterance": None,
            "continuous": None,
            "word_count": None,
            "no_anchor": None
        }
        for f in fields:
            fields[f] = self.statistics[key][f]

        # update with values from file
        for f in fields:
            self.statistics[key][f] = fields[f] + row[f]

    def check_statistics(self, key):
        """Make sure statistics contain key corresponding to current situation"""
        if not (key in self.statistics):
            self.statistics[key] = {
                "word": 0,
                "sentence": 0,
                "paragraph": 0,
                "utterance": 0,
                "continuous": 0,
                "word_count": 0,
                "no_anchor": 0
            }

    def update_word(self, start, end, key):
        if (start is not None) and (end is not None):
            word_length = (end - start).total_seconds()*1000
            self.statistics[key]["word"] += word_length

    def update_word_count(self, key):
        self.statistics[key]["word_count"] += 1

    def update_missing_anchors(self, start, end, key):
        if (start is None) or (end is None):
            self.statistics[key]["no_anchor"] += 1

    def update_segment(self, start, end, sc, sl, seg_name):
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
            self.finish_segment(seg_name)

    def update_continuous(self, start, end, speaker, role):
        speaker_l = self.last_speaker
        role_l = self.last_role
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
            self.finish_continuous()

    def to_absolute(self, interval, absolute):
        # check if either value is not nan
        if (not math.isnan(interval)) and type(absolute) != float:
            dt = datetime.strptime(absolute, "%Y-%m-%dT%H:%M:%S")
            return dt + timedelta(milliseconds=interval)
        else:
            return None

    def key_from_row(self, row):
        """Key to index into the statistics object created from row data"""
        # extract time-related data from row id
        parts = row["id"].split("-")
        election_period = parts[0]
        meeting = parts[1]
        sitting = parts[2]
        agenda = parts[4].split(".")[0]

        # extract speaker data
        speaker = row["speaker"]
        role = row["role"]

        key = (speaker, role, election_period, meeting, sitting, agenda)
        return key

    def key_last(self):
        """Key to index into the statistics object created from previous row data"""
        speaker = self.last_speaker
        role = self.last_role
        election_period = self.last_term
        meeting = self.last_meeting
        sitting = self.last_sitting
        agenda = self.last_agenda

        key = (speaker, role, election_period, meeting, sitting, agenda)
        return key

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

