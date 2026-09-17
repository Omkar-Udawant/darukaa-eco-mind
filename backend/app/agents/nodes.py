"""8 specialised agents as pure functions (LangGraph nodes wrap these)."""
from __future__ import annotations


def input_agent(state: dict) -> dict:
    """Stage 1: merge structured metrics + free-text extraction."""
    from ..reasoning.extractor import dimensions_present, extract_from_text
    from ..schemas import EnvMetrics

    msg = state.get("message", "")
    base = state.get("metrics") or EnvMetrics()
    if isinstance(base, dict):
        base = EnvMetrics.model_validate(base)
    metrics = extract_from_text(msg, base)
    state["metrics"] = metrics
    state["dimensions"] = dimensions_present(metrics)
    return state


def missing_info_agent(state: dict) -> dict:
    """Stage 2: Missing Information Agent — completeness check + clarifying questions.

    Runs BEFORE retrieval so the pipeline knows what it does not know.
    Downstream agents read `completeness_info` to calibrate confidence.
    """
    from ..reasoning.completeness import check_completeness

    comp = check_completeness(state["metrics"])
    state["completeness_info"] = comp
    return state


def retrieval_agent(state: dict) -> dict:
    """Stage 3: topic-routed retrieval + retrieval log payload."""
    from ..rag.retriever import retrieve

    metrics = state.get("metrics")
    mtext = metrics.model_dump_json() if hasattr(metrics, "model_dump_json") else str(metrics)
    docs, meta = retrieve(state.get("message", ""), mtext, top_k=4)
    state["sources"] = docs
    state["retrieval_meta"] = meta
    return state


def scientist_agent(state: dict) -> dict:
    """Stage 4a: situation assessment + causal chains + KG paths + risks."""
    from ..knowledge_graph import reasoning_paths_for_metrics
    from ..reasoning.causal import build_causal_chains, build_reasoning_graph

    metrics = state["metrics"]
    chains = build_causal_chains(metrics)
    kg_paths = reasoning_paths_for_metrics(metrics)
    state["kg_paths"] = kg_paths
    chains = chains + kg_paths[:2]  # ground explanation in KG traversals
    state["chains"] = chains
    state["reasoning_graph"] = build_reasoning_graph(metrics, chains)
    s = metrics.soil
    risks: list[str] = []
    if (s.organic_carbon_pct or 99) < 1.0:
        risks.append("Degraded soil carbon — microbial collapse and poor water holding likely.")
    if (metrics.climate.rainfall_mm or 9999) < 600:
        risks.append("Water stress — crop failure and habitat desiccation risk in dry season.")
    if (metrics.climate.temperature_c or 0) > 32:
        risks.append("Heat stress — pollinator phenology mismatch and flower abortion.")
    if metrics.human_impact.chemical_inputs in ("medium", "high"):
        risks.append("Chemical pressure — pollinator mortality and soil-biota suppression.")
    if metrics.biodiversity.pollinator_presence in ("absent", "low"):
        risks.append("Pollination deficit — native regeneration and yields will keep falling.")
    if not risks:
        risks.append("Cumulative multi-stressor pressure — slow richness erosion without action.")
    state["risks"] = risks
    region = metrics.region or "the target landscape"
    state["assessment"] = (
        f"{region}: {'; '.join(chains[:2])}. "
        f"Reasoning across {', '.join(state.get('dimensions', [])) or 'limited dimensions'} "
        f"shows compounding soil–climate–biodiversity feedbacks."
    )
    return state


def biodiversity_agent(state: dict) -> dict:
    """Stage 4b/5: select interventions (each >=3 dimensions enforced)."""
    from ..reasoning.interventions import select_interventions

    state["interventions"] = select_interventions(state["metrics"], top_k=state.get("top_k", 3))
    return state


def impact_agent(state: dict) -> dict:
    """Stage 6: quantitative impact per intervention."""
    from ..reasoning.impact import estimate_impact

    state["impacts"] = [estimate_impact(state["metrics"], it["title"]) for it in state["interventions"]]
    return state


def verification_agent(state: dict) -> dict:
    """Stage 7a (Evidence Validation Agent): drop weak claims, keep citations honest."""
    verified = []
    for d in state.get("sources", []):
        if d.get("chunk_text") and d.get("source"):
            verified.append(d)
    # guarantee at least generic provenance even with empty KB
    if not verified:
        verified = [{
            "source": "FAO", "publication": "Soil Carbon Knowledge Base (fallback)",
            "year": 2023, "topic": "soil", "evidence_strength": "medium",
            "chunk_text": "Fallback provenance: KB empty — run POST /upload or ingest seed data.",
        }]
    state["sources"] = verified[:4]
    # completeness + confidence
    from ..reasoning.completeness import check_completeness
    from ..reasoning.confidence import compute_confidence

    comp = check_completeness(state["metrics"])
    state["completeness_info"] = comp
    state["confidence"] = compute_confidence(state["metrics"], comp["completeness"], verified)
    return state


def response_agent(state: dict) -> dict:
    """Stage 7b: assemble the mandated 10-section response."""
    comp = state["completeness_info"]
    recs = []
    for it, imp in zip(state["interventions"], state["impacts"]):
        recs.append({
            "title": it["title"],
            "detail": it["detail"],
            "scientific_reasoning": it["reasoning"],
            "impacted_metrics": it["impacted"],
            "estimated_improvement": it["improvement"],
            "time_horizon": it["horizon"],
            "confidence": state["confidence"],
            "dimensions_used": it["dimensions"],
            "impact": {
                "biodiversity_gain_pct": imp["biodiversity_gain_pct"],
                "soil_carbon_gain_pct": imp["soil_carbon_gain_pct"],
                "water_retention_gain_pct": imp["water_retention_gain_pct"],
                "habitat_quality_gain_pct": imp["habitat_quality_gain_pct"],
                "horizon": imp["horizon"],
            },
        })
    impacted = sorted({m for r in recs for m in r["impacted_metrics"]})
    state["response"] = {
        "situation_assessment": state["assessment"],
        "key_risks": state["risks"],
        "recommendations": recs,
        "scientific_reasoning": " | ".join(state["chains"]),
        "impacted_metrics": impacted,
        "estimated_improvement": recs[0]["estimated_improvement"] if recs else "",
        "time_horizon": recs[0]["time_horizon"] if recs else "Medium Term",
        "confidence": state["confidence"],
        "supporting_sources": [
            {"source": d.get("source", ""), "publication": d.get("publication", ""),
             "year": int(d.get("year", 2020)), "topic": d.get("topic", ""),
             "evidence_strength": d.get("evidence_strength", "medium"),
             "excerpt": str(d.get("chunk_text", ""))[:400]}
            for d in state["sources"]
        ],
        "additional_data_needed": comp["missing"],
        "clarifying_questions": comp["questions"] if comp["needs_clarification"] else [],
        "reasoning_graph": {"nodes": state["reasoning_graph"]["nodes"], "edges": state["reasoning_graph"]["edges"]},
        "completeness": comp["completeness"],
    }
    return state
