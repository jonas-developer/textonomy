from pydantic import BaseModel, Field
from typing import List

class ModelJudgement(BaseModel):
    provider: str                 # "openai" | "deepseek" | "watsonx"
    model: str
    ai_likelihood_score: int = Field(..., ge=0, le=100)
    reasoning: str
    signals: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)

class UnifiedResult(BaseModel):
    final_label: str              # GREEN/YELLOW/RED
    final_score: int = Field(..., ge=0, le=100)
    confidence: str               # low/medium/high
    aggregation_notes: str
    per_model: List[ModelJudgement]
