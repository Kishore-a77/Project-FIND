from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MissingPerson:
    person_id: str
    name: str
    age: Optional[int] = 0  # Make optional with default
    notes: Optional[str] = ""  # Make optional with default
    image_path: Optional[str] = ""  # Make optional with default  
    embedding: Optional[List[float]] = None  # Make optional with default
    
    def __post_init__(self):
        """Optional: Add validation after initialization"""
        if not self.name or not self.name.strip():
            raise ValueError("Name cannot be empty")