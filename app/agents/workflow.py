
from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.agents.llm_agent import generate_explanation
from app.services.validator import extract_info, check_claims
from app.core.config import settings


class InvestigationState(TypedDict, total=False):

    facts: dict
    response: dict
    extracted_info: dict
    mismatches: dict

    attempts: int
    max_attempts: int

    status: str
    final_explanation: str
    validation_history: list


# STEP 1: Generate explanation using trusted detector evidence

def generate_node(state):

    response = generate_explanation(
        facts=state["facts"],
        previous_response=(
            state.get("response", {}).get("explanation")
        ),
        mismatches=state.get("mismatches")
    )

    return {
        "response": response,
        "attempts": state.get("attempts", 0) + 1
    }


# STEP 2: Extract factual information from actual LLM explanation

def extract_node(state):

    explanation = state["response"]["explanation"]

    extracted_info = extract_info(explanation)

    return {
        "extracted_info": extracted_info
    }


# STEP 3: Validate extracted information against detector evidence

def validate_node(state):

    mismatches = check_claims(
        trusted_facts=state["facts"],
        extracted_claims=state["extracted_info"]
    )["mismatches"]

    history = list(
        state.get("validation_history", [])
    )

    history.append({
        "attempt": state["attempts"],
        "extracted_info": state["extracted_info"],
        "mismatches": mismatches
    })

    return {
        "mismatches": mismatches,
        "validation_history": history,
        "status": (
            "validated"
            if not mismatches
            else "correction_required"
        ),
        "final_explanation": (
            state["response"]["explanation"]
            if not mismatches
            else ""
        )
    }


# STEP 4: Decide next action

def route_after_validation(state):

    if not state["mismatches"]:
        return "accepted"

    if state["attempts"] >= state["max_attempts"]:
        return "failed"

    return "retry"


# STEP 5: Build LangGraph workflow

graph = StateGraph(InvestigationState)

graph.add_node(
    "generate_explanation",
    generate_node
)

graph.add_node(
    "extract_information",
    extract_node
)

graph.add_node(
    "validate_evidence",
    validate_node
)

graph.set_entry_point("generate_explanation")

graph.add_edge(
    "generate_explanation",
    "extract_information"
)

graph.add_edge(
    "extract_information",
    "validate_evidence"
)

graph.add_conditional_edges(
    "validate_evidence",
    route_after_validation,
    {
        "accepted": END,
        "retry": "generate_explanation",
        "failed": END
    }
)

workflow = graph.compile()


# STEP 6: Run investigation workflow

def run_explanation_workflow(facts):

    result = workflow.invoke({

        "facts": facts,

        "attempts": 0,

        "max_attempts": (
            settings.max_correction_attempts + 1
        ),

        "validation_history": [],

        "mismatches": {}
    })

    valid = result["status"] == "validated"

    return {

        "status": (
            "validated"
            if valid
            else "needs_human_review"
        ),

        "explanation": (
            result["final_explanation"]
            if valid
            else None
        ),

        "extracted_info": result.get("extracted_info", {}),

        "mismatches": result["mismatches"],

        "attempts": result["attempts"],

        "validation_history": result["validation_history"],

        "usage": result.get("response", {}).get("usage")
    }
