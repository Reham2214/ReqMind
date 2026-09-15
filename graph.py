from concurrent.futures import ThreadPoolExecutor
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from utils.schemas import (
    Requirement,
    QualityAnalysisResult,
    RelationshipAnalysisResult,
    FinalRequirementResult,
)

from agents.extraction_agent import extract_requirements
from agents.quality_agent import analyze_requirements
from agents.conflict_agent import analyze_relationships
from agents.recommendation_agent import generate_recommendation

from rag.retriever import (
    retrieve,
    get_unique_sources,
    format_retrieved_context,
)


class ReqMindState(TypedDict, total=False):
    document_text: str
    requirements: list[Requirement]
    quality_result: QualityAnalysisResult
    relationship_result: RelationshipAnalysisResult
    final_results: list[FinalRequirementResult]


# ==========================================================
# Extraction
# ==========================================================

def extraction_node(state):
    document_text = state.get("document_text", "")

    result = extract_requirements(
        document_text
    )

    return {
        "requirements": result.requirements
    }


# ==========================================================
# Quality Analysis
# ==========================================================

def quality_node(state):

    requirements = state.get(
        "requirements",
        []
    )

    result = analyze_requirements(
        requirements
    )

    return {
        "quality_result": result
    }


# ==========================================================
# Relationship Analysis
# ==========================================================

def relationship_node(state):

    requirements = state.get(
        "requirements",
        []
    )

    result = analyze_relationships(
        requirements
    )

    return {
        "relationship_result": result
    }


# ==========================================================
# Primary Issue Selection
# ==========================================================

def select_primary_issue(
    requirement,
    quality_result,
    relationship_result,
):
    """
    Select exactly one primary issue for each requirement.

    Decision rules:

    1. Collect all detected quality and relationship issues.
    2. Higher severity has priority:
       Critical > Major > Minor > None
    3. If severity is equal, relationship issues use:
       Conflict > Inconsistency > Duplication
    4. A real detected issue always has priority over No Issue.
    """

    severity_rank = {
        "Critical": 4,
        "Major": 3,
        "Minor": 2,
        "None": 1,
    }

    relationship_priority = {
        "Conflict": 3,
        "Inconsistency": 2,
        "Duplication": 1,
    }

    candidates = []

    # ------------------------------------------------------
    # Quality Issue
    # ------------------------------------------------------

    quality_by_id = {
        item.requirement_id: item
        for item in quality_result.analyses
    }

    quality_issue = quality_by_id.get(
        requirement.id
    )

    if quality_issue:

        candidates.append(
            {
                "issue_label": quality_issue.issue_label,
                "severity": quality_issue.severity,
                "explanation": quality_issue.explanation,
                "evidence": quality_issue.evidence,
                "priority": 0,
                "is_real_issue": (
                    quality_issue.issue_label
                    != "No Issue"
                ),
            }
        )

    # ------------------------------------------------------
    # Relationship Issues
    # ------------------------------------------------------

    for issue in relationship_result.issues:

        if (
            issue.requirement_id == requirement.id
            or issue.related_requirement_id
            == requirement.id
        ):

            candidates.append(
                {
                    "issue_label": issue.issue_label,
                    "severity": issue.severity,
                    "explanation": issue.explanation,
                    "evidence": issue.evidence,
                    "priority": relationship_priority.get(
                        issue.issue_label,
                        0,
                    ),
                    "is_real_issue": (
                        issue.issue_label
                        != "No Issue"
                    ),
                }
            )

    # ------------------------------------------------------
    # No Issues Found
    # ------------------------------------------------------

    if not candidates:

        return {
            "issue_label": "No Issue",
            "severity": "None",
            "explanation": (
                "No quality or relationship "
                "issue was detected."
            ),
            "evidence": "",
        }

    # ------------------------------------------------------
    # Remove No Issue if a real issue exists
    # ------------------------------------------------------

    real_issues = [
        candidate
        for candidate in candidates
        if candidate["is_real_issue"]
    ]

    if real_issues:

        candidates = real_issues

    # ------------------------------------------------------
    # Select Primary Issue
    # ------------------------------------------------------

    candidates.sort(
        key=lambda item: (
            severity_rank.get(
                item["severity"],
                1,
            ),
            item["priority"],
        ),
        reverse=True,
    )

    selected = candidates[0]

    return {
        "issue_label": selected["issue_label"],
        "severity": selected["severity"],
        "explanation": selected["explanation"],
        "evidence": selected["evidence"],
    }


# ==========================================================
# Recommendation + RAG
# ==========================================================

def generate_one_recommendation(
    requirement,
    issue_data,
):

    retrieved_results = retrieve(
        query=requirement.text,
        top_k=8,
    )

    sources = get_unique_sources(
        retrieved_results
    )

    retrieved_context = (
        format_retrieved_context(
            retrieved_results
        )
    )

    recommendation = generate_recommendation(
        requirement=requirement,
        issue_label=issue_data["issue_label"],
        severity=issue_data["severity"],
        explanation=issue_data["explanation"],
        evidence=issue_data["evidence"],
        retrieved_context=retrieved_context,
        sources=sources,
    )

    return recommendation, sources


# ==========================================================
# Recommendation Node
# ==========================================================

def recommendation_node(state):

    requirements = state.get(
        "requirements",
        []
    )

    quality_result = state[
        "quality_result"
    ]

    relationship_result = state[
        "relationship_result"
    ]

    issue_data_by_id = {}

    for requirement in requirements:

        issue_data = select_primary_issue(
            requirement,
            quality_result,
            relationship_result,
        )

        issue_data_by_id[
            requirement.id
        ] = issue_data

    # ------------------------------------------------------
    # Process Recommendations
    # ------------------------------------------------------

    def process_requirement(
        requirement
    ):

        issue_data = issue_data_by_id[
            requirement.id
        ]

        recommendation, sources = (
            generate_one_recommendation(
                requirement,
                issue_data,
            )
        )

        return (
            requirement.id,
            issue_data,
            recommendation,
            sources,
        )

    max_workers = min(
        4,
        max(len(requirements), 1),
    )

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        results = list(
            executor.map(
                process_requirement,
                requirements,
            )
        )

    # ------------------------------------------------------
    # Build Final Results
    # ------------------------------------------------------

    final_results = []

    for (
        requirement_id,
        issue_data,
        recommendation,
        sources,
    ) in results:

        requirement = next(
            req
            for req in requirements
            if req.id == requirement_id
        )

        final_results.append(
            FinalRequirementResult(
                requirement_id=requirement.id,
                requirement=requirement.text,
                issue_label=issue_data[
                    "issue_label"
                ],
                severity=issue_data[
                    "severity"
                ],
                explanation=issue_data[
                    "explanation"
                ],
                evidence=issue_data[
                    "evidence"
                ],
                recommendation=(
                    recommendation.recommendation
                ),
                improved_requirement=(
                    recommendation.improved_requirement
                ),
                sources=sources,
            )
        )

    return {
        "final_results": final_results
    }


# ==========================================================
# LangGraph
# ==========================================================

builder = StateGraph(
    ReqMindState
)

builder.add_node(
    "extraction",
    extraction_node,
)

builder.add_node(
    "quality_analysis",
    quality_node,
)

builder.add_node(
    "relationship_analysis",
    relationship_node,
)

builder.add_node(
    "recommendation",
    recommendation_node,
)

builder.add_edge(
    START,
    "extraction",
)

builder.add_edge(
    "extraction",
    "quality_analysis",
)

builder.add_edge(
    "extraction",
    "relationship_analysis",
)

builder.add_edge(
    "quality_analysis",
    "recommendation",
)

builder.add_edge(
    "relationship_analysis",
    "recommendation",
)

builder.add_edge(
    "recommendation",
    END,
)

graph = builder.compile()


# ==========================================================
# Direct Dataset Analysis
# ==========================================================

def analyze_requirements_direct(
    requirements
):

    if not requirements:
        return []

    print(
        f"Starting direct analysis for "
        f"{len(requirements)} requirements..."
    )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:

        quality_future = executor.submit(
            analyze_requirements,
            requirements,
        )

        relationship_future = (
            executor.submit(
                analyze_relationships,
                requirements,
            )
        )

        quality_result = (
            quality_future.result()
        )

        relationship_result = (
            relationship_future.result()
        )

    print(
        "Quality analysis completed."
    )

    print(
        "Relationship analysis completed."
    )

    issue_data_by_id = {}

    for requirement in requirements:

        issue_data = select_primary_issue(
            requirement,
            quality_result,
            relationship_result,
        )

        issue_data_by_id[
            requirement.id
        ] = issue_data

    # ------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------

    def process_requirement(
        requirement
    ):

        issue_data = issue_data_by_id[
            requirement.id
        ]

        recommendation, sources = (
            generate_one_recommendation(
                requirement,
                issue_data,
            )
        )

        return (
            requirement,
            issue_data,
            recommendation,
            sources,
        )

    max_workers = min(
        4,
        max(len(requirements), 1),
    )

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        results = list(
            executor.map(
                process_requirement,
                requirements,
            )
        )

    final_results = []

    for (
        requirement,
        issue_data,
        recommendation,
        sources,
    ) in results:

        final_results.append(
            FinalRequirementResult(
                requirement_id=(
                    requirement.id
                ),
                requirement=(
                    requirement.text
                ),
                issue_label=(
                    issue_data[
                        "issue_label"
                    ]
                ),
                severity=(
                    issue_data[
                        "severity"
                    ]
                ),
                explanation=(
                    issue_data[
                        "explanation"
                    ]
                ),
                evidence=(
                    issue_data[
                        "evidence"
                    ]
                ),
                recommendation=(
                    recommendation.recommendation
                ),
                improved_requirement=(
                    recommendation.improved_requirement
                ),
                sources=sources,
            )
        )

    print(
        "Direct dataset analysis completed."
    )

    return final_results