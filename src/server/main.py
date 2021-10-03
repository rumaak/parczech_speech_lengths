from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
import os

from src.aggregator import IntervalAggregator

import src.server.single.precomputed as sp
import src.server.single.interval as si
import src.server.multiple.interval as mi
import src.server.top.interval as ti
import src.server.data.speakers as ds

app = FastAPI()

origins = {
    "http://localhost:3000"
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# TODO refactoring


def aggregate(series):
    use_average = ['unanchored', 'words_per_minute']

    if series.name in use_average:
        return np.average(series)
    else:
        return np.sum(series)

@app.post("/single/precomputed", response_model=sp.Response)
async def single_precomputed(request: sp.Request):
    path = "samples/sample_statistics_output/precomputed/all.txt"
    all_df = pd.read_csv(path)
    speaker_df = all_df.loc[all_df["speaker"] == request.MoP]

    response = {
        "speaking_time": dict(),
        "relative_diff": dict(),
        "unanchored": dict(),
        "wpm": dict()
    }

    speaker_df.apply(lambda row: sp.update_response(response, row) , axis=1)

    return sp.Response(**response)

@app.post("/single/interval", response_model=si.Response)
async def single_interval(request: si.Request):
    input_dir = "samples/sample_audio_statistics_output/"
    output_dir = "samples/sample_statistics_output/"
    start = request.start.strftime("%Y-%m-%dT%H:%M:%S")
    end = request.end.strftime("%Y-%m-%dT%H:%M:%S")

    aggregator = IntervalAggregator(input_dir, output_dir, start, end)
    data_df = aggregator.aggregate()
    speaker_df = data_df.loc[data_df["speaker"] == request.MoP]

    response = {
        "speaking_time": dict(),
        "relative_diff": dict(),
        "unanchored": dict(),
        "wpm": dict()
    }

    speaker_df.apply(lambda row: si.update_response(response, row) , axis=1)

    return si.Response(**response)

# NOTE only some filtering is available as of now
#   - speakers - MoPs
#   - data - interval
@app.post("/multiple/interval", response_model=mi.Response)
async def multiple_interval(request: mi.Request):
    # aggregate corresponding data
    input_dir = "samples/sample_audio_statistics_output/"
    output_dir = "samples/sample_statistics_output/"
    data_df = None
    interval = request.data.interval
    if interval is not None:
        start = interval.start.strftime("%Y-%m-%dT%H:%M:%S")
        end = interval.end.strftime("%Y-%m-%dT%H:%M:%S")

        aggregator = IntervalAggregator(input_dir, output_dir, start, end)
        data_df = aggregator.aggregate()

    # filter out irrelevant speakers
    speaker_df = None
    if request.speakers is not None:
        if request.speakers.static is not None:
            speakers = request.speakers.static.MoPs
            if speakers is not None:
                speaker_df = data_df.loc[data_df["speaker"].isin(speakers)]
    else:
        speaker_df = data_df

    # get rid of the election_period column
    if "election_period" in speaker_df:
        speaker_df = speaker_df.drop("election_period", axis=1)

        # TODO this is just a temporary solution - we cannot take an average
        #      over election periods; the statistics have to be calculated
        #      differently (i.e. provide number of words)
        speaker_df = speaker_df.groupby(["speaker", "role"]).agg(aggregate)

        speaker_df.reset_index(inplace=True)

    # create response
    response = {
        "speaking_time": dict(),
        "relative_diff": dict(),
        "unanchored": dict(),
        "wpm": dict()
    }

    speaker_df.apply(lambda row: mi.update_response(response, row) , axis=1)

    return mi.Response(**response)

@app.post("/top/interval", response_model=ti.Response)
async def top_interval(request: ti.Request):
    input_dir = "samples/sample_audio_statistics_output/"
    output_dir = "samples/sample_statistics_output/"
    start = request.start.strftime("%Y-%m-%dT%H:%M:%S")
    end = request.end.strftime("%Y-%m-%dT%H:%M:%S")

    aggregator = IntervalAggregator(input_dir, output_dir, start, end)
    data_df = aggregator.aggregate()

    response = {
        "speaking_time": dict(),
        "relative_diff": dict(),
        "unanchored": dict(),
        "wpm": dict()
    }

    ti.update_response(data_df, response)
    return ti.Response(**response)

@app.get("/data/speakers", response_model=ds.Response)
async def data_speakers():
    input_dir = "samples/sample_personal_data_output/"
    path = os.path.join(input_dir, "ParCzech.ana.json")

    data = None
    with open(path, 'r') as file:
        raw_data = file.read()
        data = json.loads(raw_data)

    response = {
        "speakers": list(data.keys())
    }

    return ds.Response(**response)

