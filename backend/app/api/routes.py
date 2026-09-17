"""All REST endpoints. Persistence + reasoning-log + retrieval-log observability."""
from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..agents.graph import run_full_reasoning
from ..database import (
    BiodiversityMetrics,
    ClimateMetrics,
    Conversation,
    ConversationMemory,
    HumanImpactMetrics,
    ImpactPrediction,
    LandUseMetrics,
    ReasoningLog,
    Recommendation,
    RetrievalLog,
    ScientificSource,
    SoilMetrics,
    get_db,
    init_db,
)
from ..memory.manager import memory
from ..schemas import (
    AnalyzeRequest,
    ChatRequest,
    ChatResponse,
    ImpactRequest,
    RecommendRequest,
    UploadResponse,
)

router = APIRouter()


def _ensure_conversation(db: Session, cid: str | None, message: str, email: str | None = None) -> Conversation:
    from ..database import User

    user_id = None
    if email:
        u = db.query(User).filter(User.email == email).first()
        if not u:
            u = User(email=email, name=email.split("@")[0])
            db.add(u)
            db.commit()
            db.refresh(u)
        user_id = u.id
    if cid:
        c = db.query(Conversation).filter(Conversation.id == cid).first()
        if c:
            return c
    c = Conversation(id=cid or str(uuid.uuid4()), user_id=user_id, title=(message[:80] or "New assessment"))
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _persist_metrics(db: Session, cid: str, m) -> None:
    db.add(SoilMetrics(conversation_id=cid, ph=m.soil.ph,
                       organic_carbon_pct=m.soil.organic_carbon_pct,
                       moisture_pct=m.soil.moisture_pct, nutrient_quality=m.soil.nutrient_quality))
    db.add(ClimateMetrics(conversation_id=cid, temperature_c=m.climate.temperature_c,
                          rainfall_mm=m.climate.rainfall_mm,
                          seasonal_variability=m.climate.seasonal_variability))
    db.add(BiodiversityMetrics(conversation_id=cid, species_richness=m.biodiversity.species_richness,
                               habitat_diversity=m.biodiversity.habitat_diversity,
                               pollinator_presence=m.biodiversity.pollinator_presence))
    db.add(LandUseMetrics(conversation_id=cid, cropland_pct=m.land_use.cropland_pct,
                          forest_pct=m.land_use.forest_pct, grassland_pct=m.land_use.grassland_pct,
                          urban_pct=m.land_use.urban_pct, wetlands_pct=m.land_use.wetlands_pct,
                          dominant_type=m.land_use.dominant_type))
    db.add(HumanImpactMetrics(conversation_id=cid, pollution=m.human_impact.pollution,
                              deforestation=m.human_impact.deforestation,
                              fragmentation=m.human_impact.fragmentation,
                              chemical_inputs=m.human_impact.chemical_inputs))
    db.commit()


def _log_and_store(db: Session, conv: Conversation, message: str, result: dict,
                   retrieval_meta: dict, metrics) -> ChatResponse:
    resp = result["response"]
    memory.append_turn(conv.id, "user", message)
    memory.append_turn(conv.id, "assistant", resp["situation_assessment"])
    memory.persist(conv.id, "user", message)
    memory.persist(conv.id, "assistant", resp["situation_assessment"])
    _persist_metrics(db, conv.id, metrics)
    for r in resp["recommendations"]:
        rec = Recommendation(
            conversation_id=conv.id, title=r["title"], detail=r["detail"],
            reasoning=r["scientific_reasoning"], impacted_metrics=r["impacted_metrics"],
            estimated_improvement=r["estimated_improvement"], time_horizon=r["time_horizon"],
            confidence=r["confidence"], dimensions_used=r["dimensions_used"],
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        db.add(ImpactPrediction(
            recommendation_id=rec.id,
            biodiversity_gain_pct=r["impact"]["biodiversity_gain_pct"],
            soil_carbon_gain_pct=r["impact"]["soil_carbon_gain_pct"],
            water_retention_gain_pct=r["impact"]["water_retention_gain_pct"],
            habitat_quality_gain_pct=r["impact"]["habitat_quality_gain_pct"],
            horizon=r["impact"]["horizon"],
        ))
    db.add(RetrievalLog(conversation_id=conv.id, query=message,
                        topics=retrieval_meta.get("topics", []),
                        doc_ids=[s.get("publication", "") for s in resp["supporting_sources"]],
                        latency_ms=retrieval_meta.get("latency_ms", 0)))
    db.add(ReasoningLog(conversation_id=conv.id, stage="full_pipeline",
                        payload={"chains": result.get("chains", []),
                                 "dimensions": result.get("dimensions", []),
                                 "confidence": resp["confidence"]}))
    db.commit()
    return ChatResponse(conversation_id=conv.id, **resp)


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    from ..schemas import EnvMetrics

    conv = _ensure_conversation(db, req.conversation_id, req.message, req.user_email)
    metrics = req.metrics or EnvMetrics()
    t0 = time.time()
    result = run_full_reasoning(req.message, metrics, top_k=3)
    meta = result.get("retrieval_meta", {"topics": [], "latency_ms": int((time.time() - t0) * 1000)})
    return _log_and_store(db, conv, req.message, result, meta, result["metrics"])


@router.post("/analyze")
def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)):
    result = run_full_reasoning(req.metrics.notes or "Analyze these metrics.", req.metrics, top_k=3)
    r = result["response"]
    return {"assessment": r["situation_assessment"], "risks": r["key_risks"],
            "chains": result.get("chains", []), "graph": r["reasoning_graph"],
            "completeness": r["completeness"], "missing": r["additional_data_needed"]}


@router.post("/recommend")
def recommend(req: RecommendRequest, db: Session = Depends(get_db)):
    result = run_full_reasoning(req.metrics.notes or "Recommend interventions.", req.metrics, top_k=req.top_k)
    return {"recommendations": result["response"]["recommendations"],
            "confidence": result["response"]["confidence"]}


@router.post("/reasoning")
def reasoning(req: AnalyzeRequest):
    result = run_full_reasoning(req.metrics.notes or "Show reasoning.", req.metrics, top_k=3)
    return {"chains": result.get("chains", []), "kg_paths": result.get("kg_paths", []),
            "graph": result["response"]["reasoning_graph"],
            "dimensions": result.get("dimensions", []),
            "scientific_reasoning": result["response"]["scientific_reasoning"]}


@router.post("/reason")
def reason(req: AnalyzeRequest):
    """Challenge-spec alias for /reasoning with KG paths surfaced first."""
    result = run_full_reasoning(req.metrics.notes or "Show reasoning.", req.metrics, top_k=3)
    return {"chains": result.get("chains", []), "kg_paths": result.get("kg_paths", []),
            "graph": result["response"]["reasoning_graph"],
            "dimensions": result.get("dimensions", []),
            "scientific_reasoning": result["response"]["scientific_reasoning"]}


class IngestRequest(BaseModel):
    text: str
    source: str = "USER"
    publication: str = "Direct ingest"
    year: int = 2026
    topic: str = "general"
    evidence_strength: str = "emerging"


@router.post("/ingest")
def ingest(req: IngestRequest, db: Session = Depends(get_db)):
    """JSON knowledge-ingest for per-source pipelines (FAO/IPCC/UNEP/IUCN/GBIF/NASA/papers)."""
    from ..rag.ingest import build_records
    from ..rag.vectorstore import get_vector_store

    docs = build_records(req.source, req.publication, req.year, req.topic,
                         req.evidence_strength, req.text)
    n = get_vector_store().upsert(docs)
    for d in docs:
        db.add(ScientificSource(source=d["source"], publication=d["publication"], year=d["year"],
                                topic=d["topic"], evidence_strength=d["evidence_strength"],
                                chunk_text=d["chunk_text"][:4000], embedding_id=d["embedding_id"]))
    db.commit()
    return {"chunks_indexed": n, "source": req.source, "topic": req.topic}


@router.get("/history")
def history(user_email: str | None = None, limit: int = 20, db: Session = Depends(get_db)):
    """Longitudinal conversation memory: baseline -> intervention -> re-measurement."""
    from ..database import User

    q = db.query(Conversation).order_by(Conversation.updated_at.desc())
    if user_email:
        u = db.query(User).filter(User.email == user_email).first()
        q = q.filter(Conversation.user_id == (u.id if u else "__none__"))
    rows = q.limit(max(1, min(limit, 100))).all()
    return [{"id": c.id, "title": c.title, "region": c.region,
             "turns": len(memory.history(c.id, limit=100))} for c in rows]


@router.get("/graph")
def knowledge_graph(src: str | None = None, dst: str | None = None):
    """Environmental knowledge graph: full graph or directed paths src -> dst."""
    from ..knowledge_graph import find_paths, full_graph, neighbors

    if src and dst:
        return {"paths": find_paths(src, dst)}
    if src:
        return {"entity": src, "out": neighbors(src, "out"), "in": neighbors(src, "in")}
    return full_graph()


@router.post("/impact")
def impact(req: ImpactRequest):
    from ..reasoning.impact import estimate_impact

    return estimate_impact(req.metrics, req.intervention)


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile, source: str = "USER", db: Session = Depends(get_db)):
    raw = (await file.read()).decode("utf-8", errors="ignore")
    from ..rag.ingest import build_records
    from ..rag.vectorstore import get_vector_store

    docs = build_records(source, file.filename or "upload", 2026, "general", "emerging", raw)
    n = get_vector_store().upsert(docs)
    for d in docs:
        db.add(ScientificSource(source=d["source"], publication=d["publication"], year=d["year"],
                                topic=d["topic"], evidence_strength=d["evidence_strength"],
                                chunk_text=d["chunk_text"][:4000], embedding_id=d["embedding_id"]))
    db.commit()
    return UploadResponse(filename=file.filename or "upload", chunks_indexed=n, source=source)


@router.get("/conversation/{cid}")
def get_conversation(cid: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == cid).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    recs = db.query(Recommendation).filter(Recommendation.conversation_id == cid).all()
    return {
        "conversation": {"id": conv.id, "title": conv.title, "region": conv.region},
        "memory": memory.history(cid),
        "recommendations": [{"title": r.title, "detail": r.detail, "confidence": r.confidence} for r in recs],
    }


@router.get("/sources")
def get_sources(topic: str | None = None, db: Session = Depends(get_db)):
    q = db.query(ScientificSource)
    if topic:
        q = q.filter(ScientificSource.topic.ilike(f"%{topic}%"))
    rows = q.order_by(ScientificSource.year.desc()).limit(50).all()
    return [{"source": r.source, "publication": r.publication, "year": r.year,
             "topic": r.topic, "evidence_strength": r.evidence_strength,
             "excerpt": r.chunk_text[:400]} for r in rows]


@router.get("/metrics/{cid}")
def get_metrics(cid: str, db: Session = Depends(get_db)):
    def latest(model):
        return db.query(model).filter(model.conversation_id == cid).order_by(model.created_at.desc()).first()

    s, c, b, l, h = (latest(M) for M in (SoilMetrics, ClimateMetrics, BiodiversityMetrics,
                                         LandUseMetrics, HumanImpactMetrics))
    return {
        "soil": {"ph": s.ph, "organic_carbon_pct": s.organic_carbon_pct} if s else None,
        "climate": {"temperature_c": c.temperature_c, "rainfall_mm": c.rainfall_mm} if c else None,
        "biodiversity": {"pollinator_presence": b.pollinator_presence} if b else None,
        "land_use": {"dominant_type": l.dominant_type} if l else None,
        "human_impact": {"pollution": h.pollution} if h else None,
    }


@router.get("/health")
def health():
    return {"status": "ok", "service": "darukaa-earth", "mode": "reasoning-engine"}
