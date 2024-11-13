from pydantic import BaseModel
from typing import List, Tuple
from parseval.parsers.schema import ParserOutput


class ImageMetadata(BaseModel):
    url: str
    caption: str
    filename: str
    filepath: str
    timestamp: str


class Metadata(BaseModel):
    url: str
    timestamp: str
    html_filename: str
    images: List[ImageMetadata]


class GroundTruth(BaseModel):
    html_paths: List[str]
    html_contents: List[str]
    metadatas: List[Metadata]



class Predictions(BaseModel):
    predictions: List[ParserOutput]



class ChunkEvaluation(BaseModel):
    chunks: List[Tuple[str, str]]
    scores: List[float]
    binary_scores: List[bool]




