from dataclasses import dataclass
from typing import Optional



@dataclass
class HttpResponse:
    status_code: int
    text: str
    json_data: Optional[dict] = None