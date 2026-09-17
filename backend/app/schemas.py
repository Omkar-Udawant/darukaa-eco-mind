"""Pydantic v2 schemas — request/response contracts for the whole API."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class SoilInput(BaseModel):
    ph: float | None = None
    organic_carbon_pct: float | None = None
    moisture_pct: float | None = None
    nutrient_quality: str = ""


class ClimateInput(BaseModel):
    temperature_c: float | None = None
    rainfall_mm: float | None = None
    seasonal_variability: str = ""


class BiodiversityInput(BaseModel):
    species_richness: int | None = None
    habitat_diversity: str = ""
    pollinator_presence: str = ""


class LandUseInput(BaseModel):
    cropland_pct: float | None = None
    forest_pct: float | None = None
    grassland_pct: float | None = None
    urban_pct: float | None = None
    wetlands_pct: float | None = None
    dominant_type: str = ""


class HumanImpactInput(BaseModel):
    pollution: str = ""
    deforestation: str = ""
    fragmentation: str = ""
    chemical_inputs: str = ""


class EnvMetrics(BaseModel):
    soil: SoilInput = Field(default_factory=SoilInput)
    climate: ClimateInput = Field(default_factory=ClimateInput)
    biodiversity: BiodiversityInput = Field(default_factory=BiodiversityInput)
    land_use: LandUseInput = Field(default_factory=LandUseInput)
    human_impact: HumanImpactInput = Field(default_factory=HumanImpactInput)
    region: str = ""
    notes: str = ""


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    metrics: EnvMetrics | None = None
    user_email: str | None = None


class SourceCitation(BaseModel):
    source: str
    publication: str
    year: int
    topic: str
    evidence_strength: str
    excerpt: str


class ImpactEstimate(BaseModel):
    biodiversity_gain_pct: float
    soil_carbon_gain_pct: float
    water_retention_gain_pct: float
    habitat_quality_gain_pct: float
    horizon: str


class RecommendationOut(BaseModel):
    title: str
    detail: str
    scientific_reasoning: str
    impacted_metrics: list[str]
    estimated_improvement: str
    time_horizon: str
    confidence: float
    dimensions_used: list[str]
    impact: ImpactEstimate


class ReasoningGraph(BaseModel):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


class ChatResponse(BaseModel):
    conversation_id: str
    situation_assessment: str
    key_risks: list[str]
    recommendations: list[RecommendationOut]
    scientific_reasoning: str
    impacted_metrics: list[str]
    estimated_improvement: str
    time_horizon: str
    confidence: float
    supporting_sources: list[SourceCitation]
    additional_data_needed: list[str]
    clarifying_questions: list[str] = []
    reasoning_graph: ReasoningGraph
    completeness: float


class AnalyzeRequest(BaseModel):
    conversation_id: str | None = None
    metrics: EnvMetrics


class RecommendRequest(BaseModel):
    conversation_id: str | None = None
    metrics: EnvMetrics
    top_k: int = 3


class ImpactRequest(BaseModel):
    metrics: EnvMetrics
    intervention: str


class UploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    source: str
