from pydantic import BaseModel
from typing import List

class TaskQuantum(BaseModel):
    n: int
    frequency: float
    energy: float
    description: str
    dependencies: List[str]
