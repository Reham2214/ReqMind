from concurrent.futures import ThreadPoolExecutor
from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from agents.extraction_agent import (
    extract_requirements,
)

from agents.quality_agent import (
    analyze_requirements,
)

from agents.conflict_agent import (
    analyze_relationships,
)

from agents.recommendation_agent import (
    generate_recommendation,
)

from rag.retriever import (
    retrieve,
    format_retrieved_context,
)

from utils.schemas import (
    FinalRequirementResult,
)


# Maximum number of recommendation/RAG jobs
# running at the same time.
MAX_WORKERS = 4


class ReqMindState(TypedDict, total=False):

    document_text: str

    requirements: list

    quality_analyses: list

    relationship_issues: list

    final_results: list


def extraction_node(
    state: ReqMindState,
):

    result = extract_requirements(
        state["document_text"]
    )

    return {
        "requirements": result.requirements
    }


def quality_node(
    state: ReqMindState,
):

    result = analyze_requirements(
        state["requirements"]
    )

    return {
        "quality_analyses": result.analyses
    }


def relationship_node(
    state: ReqMindState,
):

    result = analyze_relationships(
        state["requirements"]
    )

    return {
        "relationship_issues": result.issues
    }


def process_requirement_recommendation(
    requirement,
    quality,
    related_issues,
):
    """
    Process one requirement:

    1. Determine the final issue.
    2. Retrieve relevant RAG context.
    3. Generate recommendation.
    4. Return FinalRequirementResult.
    """

    # Default values from Quality Agent

    issue_label = (
        quality.issue_label
        if quality
        else "No Issue"
    )

    severity = (
        quality.severity
        if quality
        else "None"
    )

    explanation = (
        quality.explanation
        if quality
        else ""
    )

    evidence = (
        quality.evidence
        if quality
        else ""
    )

    # Relationship Agent can override
    # the individual quality label.

    if related_issues:

        strongest_issue = max(
            related_issues,
            key=lambda x: {
                "Critical": 4,
                "Major": 3,
                "Minor": 2,
                "None": 1,
            }.get(
                x.severity,
                1,
            ),
        )

        issue_label = (
            strongest_issue.issue_label
        )

        severity = (
            strongest_issue.severity
        )

        explanation = (
            strongest_issue.explanation
        )

        evidence = (
            strongest_issue.evidence
        )

    # Build RAG query.

    rag_query = f"""
Software requirement:
{requirement.text}

Issue:
{issue_label}

Explanation:
{explanation}
"""

    # Retrieve relevant requirements-engineering
    # knowledge.

    retrieved = retrieve(
        rag_query,
        top_k=4,
    )

    retrieved_context = (
        format_retrieved_context(
            retrieved
        )
    )

    sources = [
        item["source"]
        for item in retrieved
    ]

    # Generate recommendation.

    recommendation = generate_recommendation(
        requirement=requirement,
        issue_label=issue_label,
        severity=severity,
        explanation=explanation,
        evidence=evidence,
        retrieved_context=retrieved_context,
        sources=sources,
    )

    return FinalRequirementResult(
        requirement_id=requirement.id,
        requirement=requirement.text,
        issue_label=issue_label,
        severity=severity,
        explanation=explanation,
        evidence=evidence,
        recommendation=(
            recommendation.recommendation
        ),
        improved_requirement=(
            recommendation.improved_requirement
        ),
        sources=sources,
    )


def recommendation_node(
    state: ReqMindState,
):

    requirements = state["requirements"]

    quality_analyses = (
        state["quality_analyses"]
    )

    relationship_issues = (
        state["relationship_issues"]
    )

    # Process each requirement in parallel.

    tasks = []

    for requirement in requirements:

        quality = next(
            (
                item
                for item in quality_analyses
                if item.requirement_id
                == requirement.id
            ),
            None,
        )

        related_issues = [
            issue
            for issue in relationship_issues
            if (
                issue.requirement_id
                == requirement.id
                or
                issue.related_requirement_id
                == requirement.id
            )
        ]

        tasks.append(
            (
                requirement,
                quality,
                related_issues,
            )
        )

    if not tasks:

        return {
            "final_results": []
        }

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        final_results = list(
            executor.map(
                lambda task:
                    process_requirement_recommendation(
                        task[0],
                        task[1],
                        task[2],
                    ),
                tasks,
            )
        )

    return {
        "final_results": final_results
    }


def build_graph():

    builder = StateGraph(
        ReqMindState
    )

    # Nodes

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

    # Start

    builder.add_edge(
        START,
        "extraction",
    )

    # IMPORTANT:
    # Quality and Relationship analysis
    # now start after extraction and can
    # execute in parallel.

    builder.add_edge(
        "extraction",
        "quality_analysis",
    )

    builder.add_edge(
        "extraction",
        "relationship_analysis",
    )

    # Recommendation waits until BOTH
    # previous analysis nodes finish.

    builder.add_edge(
        "quality_analysis",
        "recommendation",
    )

    builder.add_edge(
        "relationship_analysis",
        "recommendation",
    )

    # End

    builder.add_edge(
        "recommendation",
        END,
    )

    return builder.compile()


graph = build_graph()