from pydantic import BaseModel
from typing import List, Any

class RunInput(BaseModel):
    args: List[Any]
    