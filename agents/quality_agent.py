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


SYSTEM_PROMPT = """
You are the Quality Analysis Agent in ReqMind.

Your responsibility is to analyze EACH requirement independently.

You ONLY detect these issue types:

1. No Issue
2. Ambiguity
3. Incompleteness
4. Non-verifiable

IMPORTANT:

Do NOT detect:
- Duplication
- Conflict
- Inconsistency

Those issues are handled separately by the Relationship Analysis Agent.

Definitions:

Ambiguity:
The requirement contains vague, subjective, unclear, or
multiple-interpretation wording.

Examples:
- quickly
- easy
- user-friendly
- reasonable
- modern
- appropriate
- efficient

Incompleteness:
Important information required to understand, implement,
or test the requirement is missing.

Non-verifiable:
The requirement is understandable, but there is no objective
way to determine whether the requirement has been satisfied.

No Issue:
The requirement is sufficiently clear, sufficiently complete
for its scope, and objectively testable.

Severity:

None:
No problem.

Minor:
A small clarification is needed.

Major:
The problem could cause implementation or testing
misunderstanding or rework.

Critical:
The problem could cause major security, operational,
financial, or system consequences.

Rules:

1. Analyze only the provided requirement.
2. Do not compare it with other requirements.
3. Do not invent missing information.
4. Evidence must come directly from the requirement text.
5. If the requirement has no individual quality problem,
   return "No Issue".
6. Return exactly one primary quality issue for the requirement.
"""


def analyze_requirement(
    requirement: Requirement,
) -> QualityAnalysis:

    user_prompt = f"""
Requirement ID:
{requirement.id}

Requirement:
{requirement.text}

Analyze this requirement according to the Quality Analysis Agent rules.
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

    max_workers = min(
        4,
        len(requirements)
    )

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        analyses = list(
            executor.map(
                analyze_requirement,
                requirements
            )
        )

    return QualityAnalysisResult(
        analyses=analyses
    )