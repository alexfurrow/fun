from dataclasses import dataclass
from typing import Optional

@dataclass
class InitialText:
    raw_text: str
    ai_response: Optional[str] = None
