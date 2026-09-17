"""LangGraph orchestration over the 8 agents, with sequential fallback."""
from __future__ import annotations

from .nodes import (
    biodiversity_agent,
    impact_agent,
    input_agent,
    missing_info_agent,
    response_agent,
    retrieval_agent,
    scientist_agent,
    verification_agent,
)

PIPELINE = [input_agent, missing_info_agent, retrieval_agent, scientist_agent,
            biodiversity_agent, impact_agent, verification_agent, response_agent]


def run_sequential(state: dict) -> dict:
    for fn in PIPELINE:
        state = fn(state)
    return state


def run_graph(state: dict) -> dict:
    """Use LangGraph when installed; otherwise run sequential pipeline."""
    try:
        from langgraph.graph import StateGraph, END  # type: ignore

        g = StateGraph(dict)
        g.add_node("input", input_agent)
        g.add_node("missing_info", missing_info_agent)
        g.add_node("retrieval", retrieval_agent)
        g.add_node("scientist", scientist_agent)
        g.add_node("biodiversity", biodiversity_agent)
        g.add_node("impact", impact_agent)
        g.add_node("verify", verification_agent)
        g.add_node("respond", response_agent)
        g.set_entry_point("input")
        g.add_edge("input", "missing_info")
        g.add_edge("missing_info", "retrieval")
        g.add_edge("retrieval", "scientist")
        g.add_edge("scientist", "biodiversity")
        g.add_edge("biodiversity", "impact")
        g.add_edge("impact", "verify")
        g.add_edge("verify", "respond")
        g.add_edge("respond", END)
        app = g.compile()
        out = app.invoke(state)
        return dict(out) if isinstance(out, dict) else run_sequential(state)
    except Exception:
        return run_sequential(state)


def run_full_reasoning(message: str, metrics, top_k: int = 3) -> dict:
    return run_graph({"message": message, "metrics": metrics, "top_k": top_k})
