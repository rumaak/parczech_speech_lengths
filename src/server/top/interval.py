from datetime import datetime
from enum import Enum

import pandas as pd
from typing import Optional, List, Dict
from pydantic import BaseModel

Series = pd.core.series.Series
DataFrame = pd.core.frame.DataFrame

class Request(BaseModel):
    start: datetime
    end: datetime

class Response(BaseModel):
    speaking_time: Dict[str, List[List]]
    relative_diff: Dict[str, List[List]]
    unanchored: Dict[str, List[List]]
    wpm: Dict[str, List[List]]


def update_response(data_df: DataFrame, response: Response) -> None:
    roles = data_df.role.unique()
    for role in roles:
        role_df = data_df.loc[data_df["role"] == role]

        # top speaking time
        speaker_df = role_df.sort_values("length_utterance", ascending=False)
        n_select = min(5, len(speaker_df))
        top_df = speaker_df.iloc[:n_select, :]
        top_df.apply(lambda row: update_speaking_time(response, row) , axis=1)

        # top relative difference
        speaker_df = role_df.sort_values("sentence-word", ascending=False)
        n_select = min(5, len(speaker_df))
        top_df = speaker_df.iloc[:n_select, :]
        top_df.apply(lambda row: update_relative_diff(response, row) , axis=1)

        # top unanchored
        speaker_df = role_df.sort_values("unanchored", ascending=False)
        n_select = min(5, len(speaker_df))
        top_df = speaker_df.iloc[:n_select, :]
        top_df.apply(lambda row: update_unanchored(response, row) , axis=1)

        # top wpm
        speaker_df = role_df.sort_values("words_per_minute", ascending=False)
        n_select = min(5, len(speaker_df))
        top_df = speaker_df.iloc[:n_select, :]
        top_df.apply(lambda row: update_wpm(response, row) , axis=1)

def update_speaking_time(response: Response, row: Series) -> None:
    role = row["role"]
    if role not in response["speaking_time"]:
        response["speaking_time"][role] = [[
            "Speaker",
            "Words",
            "Sentences",
            "Paragraphs",
            "Utterances"
        ]]

    response["speaking_time"][role].append([
        row["speaker"],
        row["length_word"],
        row["length_sentence"],
        row["length_paragraph"],
        row["length_utterance"]
    ])

def update_relative_diff(response: Response, row: Series) -> None:
    role = row["role"]
    if role not in response["relative_diff"]:
        response["relative_diff"][role] = [[
            "Speaker",
            "Utterance vs paragraph",
            "Paragraph vs sentence",
            "Sentence vs word"
        ]]

    response["relative_diff"][role].append([
        row["speaker"],
        row["utterance-paragraph"],
        row["paragraph-sentence"],
        row["sentence-word"]
    ])

def update_unanchored(response: Response, row: Series) -> None:
    role = row["role"]
    if role not in response["unanchored"]:
        response["unanchored"][role] = [["Speaker", "Unanchored"]]

    response["unanchored"][role].append([
        row["speaker"],
        row["unanchored"]
    ])

def update_wpm(response: Response, row: Series) -> None:
    role = row["role"]
    if role not in response["wpm"]:
        response["wpm"][role] = [["Speaker", "Words per mminute"]]

    response["wpm"][role].append([
        row["speaker"],
        row["words_per_minute"]
    ])

