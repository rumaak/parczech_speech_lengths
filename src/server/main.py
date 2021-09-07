from typing import Optional, List, Dict
from pydantic import BaseModel

from fastapi import FastAPI
import pandas as pd

import src.server.single.precomputed as sp

class Person(BaseModel):
    id: str

class Response(BaseModel):
    speaking_time: Dict[str, List[List]]
    relative_diff: Dict[str, List[List]]
    unanchored: Dict[str, List[List]]
    wpm: Dict[str, List[List]]

app = FastAPI()


@app.post("/single/precomputed", response_model=Response)
async def single_precomputed(person: Person):
    path = "samples/sample_statistics_output/precomputed/all.txt"
    all_df = pd.read_csv(path)
    speaker_df = all_df.loc[all_df["speaker"] == person.id]

    response = {
        "speaking_time": dict(),
        "relative_diff": dict(),
        "unanchored": dict(),
        "wpm": dict()
    }

    speaker_df.apply(lambda row: sp.update_response(response, row) , axis=1)

    return Response(**response)

