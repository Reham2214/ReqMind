import os
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from openai import OpenAI

from utils.schemas import (
    Requirement,
    QualityAnalysis,
    QualityAnalysisResult,
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)

# Maximum number of API requests running at the same time.
MAX_WORKERS = 4


SYSTEM_PROMPT = """
You are the Quality Analysis Agent in ReqMind.

Analyze each software requirement independently.

Allowed issue labels:

1. No Issue
2. Ambiguity
3. Incompleteness
4. Non-verifiable

Definitions:

Ambiguity:
The requirement contains vague or subjective wording that can have multiple interpretations.
Examples:
- quickly
- easy
- user-friendly
- reasonable
- modern

Incompleteness:
Important information needed to understand or implement the requirement is missing.

Non-verifiable:
The requirement is understandable but there is no objective way to determine whether it has been satisfied.

No Issue:
The requirement is sufficiently clear, complete for its scope, and objectively testable.

Severity:

None:
No problem.

Minor:
Small clarification is needed.

Major:
The problem could cause implementation or testing misunderstanding or rework.

Critical:
The problem could cause major security, operational, financial, or system consequences.

Important:
Do not classify conflicts, duplication, or cross-requirement inconsistency here.
Those are handled by another agent.

Return evidence based directly on the requirement text.
Do not invent information.
"""


def analyze_requirement(
    requirement: Requirement,
) -> QualityAnalysis:

    user_prompt = f"""
Requirement ID:
{requirement.id}

Requirement:
{requirement.text}

Analyze this requirement.
"""

    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        response_format=QualityAnalysis,
    )

    return response.choices[0].message.parsed


def analyze_requirements(
    requirements: list[Requirement],
) -> QualityAnalysisResult:

    if not requirements:
        return QualityAnalysisResult(
            analyses=[]
        )

    # Run multiple requirements in parallel.
    # executor.map preserves the original requirement order.
    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        analyses = list(
            executor.map(
                analyze_requirement,
                requirements,
            )
        )

    return QualityAnalysisResult(
        analyses=analyses
    )