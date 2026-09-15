from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

from app.services.scoring import compute_hybrid_score
from app.services.decision import decide
from app.services.rag import retrieve_context
from app.services.routing import route_lead
from app.services.message_generation import generate_message


class PipelineState(TypedDict):
    lead: Any
    rag_context: str | None
    score_result: dict | None
    decision: dict | None
    action: dict | None   # nouveau : message + routage


def rag_node(state: PipelineState) -> PipelineState:
    lead = state["lead"]
    query = (
        f"Secteur : {lead.industry}. Poste : {lead.job_title}. "
        f"Taille : {lead.company_size} employés. "
        f"Signaux : {lead.recent_signals}."
    )
    state["rag_context"] = retrieve_context(query, top_k=3)
    return state


def scoring_node(state: PipelineState) -> PipelineState:
    result = compute_hybrid_score(state["lead"], rag_context=state.get("rag_context"))
    state["score_result"] = result
    return state


def decision_node(state: PipelineState) -> PipelineState:
    score = state["score_result"]["score"]
    state["decision"] = decide(score)
    return state


def action_node(state: PipelineState) -> PipelineState:
    """Nœud d'action : message personnalisé + routage (leads non rejetés)."""
    lead = state["lead"]
    routing = route_lead(lead)
    message = generate_message(lead, rag_context=state.get("rag_context"))
    state["action"] = {**routing, **message}
    return state


def route_after_decision(state: PipelineState) -> str:
    """Branchement conditionnel : action seulement si non rejeté."""
    if state["decision"]["status"] == "rejeté":
        return "end"
    return "action"


def build_pipeline():
    graph = StateGraph(PipelineState)

    graph.add_node("rag", rag_node)
    graph.add_node("scoring", scoring_node)
    graph.add_node("decision", decision_node)
    graph.add_node("action", action_node)

    graph.add_edge(START, "rag")
    graph.add_edge("rag", "scoring")
    graph.add_edge("scoring", "decision")

    # Branchement conditionnel après la décision
    graph.add_conditional_edges(
        "decision",
        route_after_decision,
        {"action": "action", "end": END},
    )
    graph.add_edge("action", END)

    return graph.compile()


pipeline = build_pipeline()