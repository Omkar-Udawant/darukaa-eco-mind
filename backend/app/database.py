"""PostgreSQL (Supabase-ready) schema via SQLAlchemy 2.0.
Falls back to SQLite for local demo — same models work on both.
Covers all 13 required tables.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


def _uid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500), default="New assessment")
    region: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ConversationMemory(Base):
    __tablename__ = "conversation_memory"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), index=True
    )
    role: Mapped[str] = mapped_column(String(32))  # user | assistant | system
    content: Mapped[str] = mapped_column(Text)
    entities: Mapped[dict] = mapped_column(JSON, default=dict)  # extracted env entities
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SoilMetrics(Base):
    __tablename__ = "soil_metrics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), index=True)
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    organic_carbon_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    nutrient_quality: Mapped[str] = mapped_column(String(64), default="")  # low|medium|high
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ClimateMetrics(Base):
    __tablename__ = "climate_metrics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), index=True)
    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    seasonal_variability: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BiodiversityMetrics(Base):
    __tablename__ = "biodiversity_metrics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), index=True)
    species_richness: Mapped[int | None] = mapped_column(Integer, nullable=True)
    habitat_diversity: Mapped[str] = mapped_column(String(64), default="")
    pollinator_presence: Mapped[str] = mapped_column(String(64), default="")  # absent|low|medium|high
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LandUseMetrics(Base):
    __tablename__ = "land_use_metrics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), index=True)
    cropland_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    forest_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    grassland_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    urban_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    wetlands_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    dominant_type: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class HumanImpactMetrics(Base):
    __tablename__ = "human_impact_metrics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), index=True)
    pollution: Mapped[str] = mapped_column(String(64), default="")
    deforestation: Mapped[str] = mapped_column(String(64), default="")
    fragmentation: Mapped[str] = mapped_column(String(64), default="")
    chemical_inputs: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    detail: Mapped[str] = mapped_column(Text, default="")
    reasoning: Mapped[str] = mapped_column(Text, default="")
    impacted_metrics: Mapped[list] = mapped_column(JSON, default=list)
    estimated_improvement: Mapped[str] = mapped_column(String(500), default="")
    time_horizon: Mapped[str] = mapped_column(String(64), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    dimensions_used: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ScientificSource(Base):
    __tablename__ = "scientific_sources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    source: Mapped[str] = mapped_column(String(255), index=True)  # FAO, IPCC, ...
    publication: Mapped[str] = mapped_column(String(500))
    year: Mapped[int] = mapped_column(Integer, default=2020)
    topic: Mapped[str] = mapped_column(String(255), default="")
    evidence_strength: Mapped[str] = mapped_column(String(32), default="medium")
    chunk_text: Mapped[str] = mapped_column(Text)
    embedding_id: Mapped[str] = mapped_column(String(255), default="")


class RetrievalLog(Base):
    __tablename__ = "retrieval_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), index=True)
    query: Mapped[str] = mapped_column(Text)
    topics: Mapped[list] = mapped_column(JSON, default=list)
    doc_ids: Mapped[list] = mapped_column(JSON, default=list)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReasoningLog(Base):
    __tablename__ = "reasoning_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), index=True)
    stage: Mapped[str] = mapped_column(String(128))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ImpactPrediction(Base):
    __tablename__ = "impact_predictions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uid)
    recommendation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("recommendations.id"), index=True
    )
    biodiversity_gain_pct: Mapped[float] = mapped_column(Float, default=0.0)
    soil_carbon_gain_pct: Mapped[float] = mapped_column(Float, default=0.0)
    water_retention_gain_pct: Mapped[float] = mapped_column(Float, default=0.0)
    habitat_quality_gain_pct: Mapped[float] = mapped_column(Float, default=0.0)
    horizon: Mapped[str] = mapped_column(String(64), default="Medium Term")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# --- engine ---
_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
