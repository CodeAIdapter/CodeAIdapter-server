from typing import List, Optional
from dataclasses import dataclass

@dataclass
class CodeRequest:
    prompt: str
    file: Optional[str]
    filename: Optional[str]