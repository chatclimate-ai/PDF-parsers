from pydantic import BaseModel
from typing import Optional, List


class GroundTruth(BaseModel):
    file_path: str
    file_name: str
    company_name: Optional[str]
    region: Optional[str]
    date: Optional[int]
    query: str
    stance: str
    comment: Optional[str]
    evidences: List[str]
