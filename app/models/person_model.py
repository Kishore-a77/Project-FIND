from dataclasses import dataclass
from typing import List

@dataclass
class MissingPerson:
    person_id: str
    name: str
    age: int
    notes: str
    image_path: str
    embedding: List[float]
