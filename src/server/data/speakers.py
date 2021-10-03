from typing import List
from pydantic import BaseModel

class Response(BaseModel):
    speakers: List[str]

