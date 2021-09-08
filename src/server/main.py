from fastapi import FastAPI
import pandas as pd

import src.server.single.precomputed as sp

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

