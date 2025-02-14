from typing import List, Optional
from dataclasses import dataclass

@dataclass
class CodeRequest:
    prompt: str
    file: Optional[str]
    filename: Optional[str]

@dataclass
class CodeResponse:
    file: Optional[str]
    filename: Optional[str]
    success_msg: Optional[str]
    error_msg: Optional[str]
    status: bool