from pydantic import BaseModel
from typing import List

class PredictionItem(BaseModel):
    disease: str
    confidence: float

class SkinAnalysisResponse(BaseModel):
    disease: str
    confidence: float
    top_predictions: List[PredictionItem]
    recommendations: List[str]
    next_steps: List[str]
    tips: List[str]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool