import sys
import os
from datetime import datetime, date, time
from pathlib import Path
from copy import deepcopy

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class Aggregator:
    def __init__(self, input_dir, output_dir):
        self.input_dir = os.path.relpath(input_dir)
        self.output_dir = os.path.relpath(output_dir)

        self.total_length = dict()
        self.relative_diff = dict()
        self.words = dict()

        self.index_filename = "audio_index.csv"

    def aggregate(self):
        # accumulate the data from audio files
        for audio in self.correct_audios():
            data_df = pd.read_csv(audio)
            data_df.apply(self.compute_total_length, axis=1)
            data_df.apply(self.compute_relative_difference, axis=1)
            data_df.apply(self.compute_word_statistics, axis=1)

        # create a file with accumulated values
        statistics_df = pd.DataFrame()
        for period in self.total_length:
            length_period = self.total_length[period]
            for speaker in length_period:
                length_speaker = length_period[speaker]
                for role in length_speaker:
                    length = length_speaker[role]
                    diff = self.relative_diff[period][speaker][role]
                    words = self.words[period][speaker][role]

                    up = diff["utterance-paragraph"] / length["utterance"]
                    ps = diff["paragraph-sentence"] / length["paragraph"]
                    sw = diff["sentence-word"] / length["sentence"]

                    count = words["word_count"]
                    anchor = words["no_anchor"]
                    minutes = self.to_minutes(length["utterance"])

                    statistics_df = statistics_df.append({
                        "election_period": period,
                        "speaker": speaker,
                        "role": role,
                        "length_word": self.to_hours(length["word"]),
                        "length_sentence": self.to_hours(length["sentence"]),
                        "length_paragraph": self.to_hours(length["paragraph"]),
                        "length_utterance": self.to_hours(length["utterance"]),
                        "utterance-paragraph": up,
                        "paragraph-sentence": ps,
                        "sentence-word": sw,
                        "unanchored": anchor / count,
                        "words_per_minute": count / minutes
                    }, ignore_index=True)

        # make sure the directory exists
        path_to_dir = self.resolve_output_dir()
        Path(path_to_dir).mkdir(parents=True, exist_ok=True)

        path = os.path.join(path_to_dir, "all.txt")
        statistics_df.to_csv(path, index=False)

        return statistics_df

    def to_minutes(self, length):
        seconds = length / 1000
        minutes = seconds / 60
        return minutes

    def to_hours(self, length):
        seconds = length / 1000
        minutes = seconds / 60
        hours = minutes / 60
        return hours

    def compute_word_statistics(self, row):
        speaker, role = row["speaker"], row["role"]
        period = row["election_period"]

        default_values = {
            "word_count": 0,
            "no_anchor": 0
        }
        self.check_field_exists(
            self.words,
            default_values,
            speaker,
            role,
            period
        )

        words = self.words[period][speaker][role]
        
        words["word_count"] += row["word_count"]
        words["no_anchor"] += row["no_anchor"]

    def compute_relative_difference(self, row):
        speaker, role = row["speaker"], row["role"]
        period = row["election_period"]

        default_values = {
            "utterance-paragraph": 0,
            "paragraph-sentence": 0,
            "sentence-word": 0
        }
        self.check_field_exists(
            self.relative_diff,
            default_values,
            speaker,
            role,
            period
        )

        relative_diff = self.relative_diff[period][speaker][role]

        relative_diff["utterance-paragraph"] += row["utterance"] - row["paragraph"]
        relative_diff["paragraph-sentence"] += row["paragraph"] - row["sentence"]
        relative_diff["sentence-word"] += row["sentence"] - row["word"]

    def compute_total_length(self, row):
        speaker, role = row["speaker"], row["role"] 
        period = row["election_period"]

        default_values = {
            "word": 0,
            "sentence": 0,
            "paragraph": 0,
            "utterance": 0
        }
        self.check_field_exists(
            self.total_length,
            default_values,
            speaker,
            role,
            period
        )

        length = self.total_length[period][speaker][role]

        length["word"] += row["word"]
        length["sentence"] += row["sentence"]
        length["paragraph"] += row["paragraph"]
        length["utterance"] += row["utterance"]

    def check_field_exists(self, field, values, speaker, role, period):
        """Ensure there is a field in the field dict corresponding to this speaker, role and period."""
        if not (period in field):
            field[period] = dict()
        field_period = field[period]

        if not (speaker in field_period):
            field_period[speaker] = dict()
        field_speaker = field_period[speaker]

        if not (role in field_speaker):
            field_speaker[role] = values.copy()

    def correct_audios(self):
        raise NotImplementedError

    def resolve_output_dir(self):
        raise NotImplementedError

class TermAggregator(Aggregator):
    def __init__(self, input_dir, output_dir):
        super().__init__(input_dir, output_dir)

    def correct_audios(self):
        for dirpath,dirnames,filenames in os.walk(self.input_dir):
            for filename in filenames:
                if filename != self.index_filename:
                    audio = os.path.join(dirpath, filename)
                    yield audio

    def resolve_output_dir(self):
        path_to_dir = os.path.join(self.output_dir, "precomputed")
        return path_to_dir

# TODO not finished yet

class CustomAggregator(Aggregator):
    def __init__(self, input_dir, output_dir, start=None, end=None, term=None,
        meeting=None, sitting=None, agenda=None):
        super().__init__(input_dir, output_dir)

        self.n_constraints = self.number_constraints(term, meeting, sitting, agenda)
        if self.n_constraints > 1:
            raise ValueError(
                "only one of (term, meeting, sitting, agenda) can be " \
                "passed as an argument"
            )

        self.start, self.end = self.fill_interval(start, end)

        self.term = term
        self.meeting = meeting
        self.sitting = sitting
        self.agenda = agenda

    def number_constraints(self, *args):
        n_constraints = 0
        for arg in args:
            if arg is not None:
                n_constraints += 1

        return n_constraints

    def fill_interval(self, start, end):
        if start is None:
            start = datetime.min

        if end is None:
            end = datetime.max

        return start, end

    # TODO this looks bad, don't know how to make prettier yet simple
    def correct_audios(self):
        if self.n_constraints == 0:
            # Years
            for year_dir in os.listdir(self.input_dir):
                if self.check_year(year_dir):
                    year_path = os.path.join(self.input_dir, year_dir)

                    # Months
                    for month_dir in os.listdir(year_path):
                        if self.check_month(year_dir, month_dir):
                            month_path = os.path.join(year_path, month_dir)

                            # Days
                            for day_dir in os.listdir(month_path):
                                if self.check_day(year_dir, month_dir, day_dir):
                                    day_path = os.path.join(month_path, day_dir)

                                    # Audio files
                                    for audio in os.listdir(day_path):
                                        if self.check_audio(audio):
                                            yield os.path.join(day_path, audio)
        else:
            # acquire index of the audio files
            path = os.path.join(self.input_dir, self.index_filename)
            index_df = pd.read_csv(path)

            # filter only relevant audio files
            index_df = self.filter_term(index_df)
            index_df = self.filter_meeting(index_df)
            index_df = self.filter_sitting(index_df)
            index_df = self.filter_agenda(index_df)

            # retain only those in specified interval
            for file_path in set(index_df["filename"]):
                filename = os.path.basename(file_path)
                if self.check_audio(filename):
                    yield file_path

    # TODO this time of time striping is used in both script, consider
    #      creating a shared helper module
    def check_audio(self, audio):
        datetime_string = audio.split(".")[0]

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

        start = datetime.combine(d, time_start)
        end = datetime.combine(d, time_end)

        if (self.start <= start) and (end <= self.end):
            return True
        
        return False

    def check_day(self, year, month, day):
        # Day
        after_start = self.start.day <= int(day)
        before_end = int(day) <= self.end.day

        # Month
        if self.start.month < int(month): 
            after_start = True

        if int(month) < self.end.month: 
            before_end = True

        # Year
        if self.start.year < int(year): 
            after_start = True

        if int(year) < self.end.year: 
            before_end = True

        return after_start and before_end

    def check_month(self, year, month):
        # Month
        after_start = self.start.month <= int(month)
        before_end = int(month) <= self.end.month

        # Year
        if self.start.year < int(year): 
            after_start = True

        if int(year) < self.end.year: 
            before_end = True

        return after_start and before_end

    def check_year(self, year):
        # We only want audio files
        if year == self.index_filename:
            return False

        # Year
        after_start = self.start.year <= int(year)
        before_end = int(year) <= self.end.year
        return after_start and before_end

    def resolve_output_dir(self):
        start = self.start.strftime("%Y%m%d%H%M")
        end = self.end.strftime("%Y%m%d%H%M")

        path_to_dir = os.path.join(
            self.output_dir,
            start + "-" + end
        )

        return path_to_dir

    def filter_term(self, index_df):
        if self.term is not None:
            return index_df.loc[index_df["election_period"] == self.term]

        return index_df

    def filter_meeting(self, index_df):
        if self.meeting is not None:
            parts = self.meeting.split("/")
            term = parts[0]
            meeting = int(parts[1])

            term_df = index_df.loc[index_df["election_period"] == term]
            meeting_df = term_df.loc[term_df["meeting"] == meeting]

            return meeting_df

        return index_df

    def filter_sitting(self, index_df):
        if self.sitting is not None:
            parts = self.sitting.split("/")
            term = parts[0]
            meeting = int(parts[1])
            sitting = int(parts[2])

            term_df = index_df.loc[index_df["election_period"] == term]
            meeting_df = term_df.loc[term_df["meeting"] == meeting]
            sitting_df = meeting_df.loc[meeting_df["sitting"] == sitting]

            return sitting_df

        return index_df

    def filter_agenda(self, index_df):
        if self.agenda is not None:
            parts = self.agenda.split("/")
            term = parts[0]
            meeting = int(parts[1])
            agenda = int(parts[2])

            term_df = index_df.loc[index_df["election_period"] == term]
            meeting_df = term_df.loc[term_df["meeting"] == meeting]
            agenda_df = meeting_df.loc[meeting_df["agenda"] == agenda]

            return agenda_df

        return index_df

