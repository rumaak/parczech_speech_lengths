from fastapi import FastAPI
import pandas as pd

from src.aggregator import IntervalAggregator

import src.server.single.precomputed as sp
import src.server.single.interval as si

app = FastAPI()


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
async def single_precomputed(request: si.Request):
    input_dir = "samples/sample_audio_statistics_output/"
    output_dir = "samples/sample_statistics_output/"
    start = request.start
    end = request.end

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

