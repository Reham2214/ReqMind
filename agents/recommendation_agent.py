import os

from dotenv import load_dotenv
from openai import OpenAI

from utils.schemas import (
    Requirement,
    Recommendation,
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
You are the Recommendation Agent in ReqMind.

Your task is to provide a practical recommendation for improving
a software requirement.

You receive:

- Original requirement
- Issue label
- Severity
- Explanation
- Evidence
- Retrieved requirements engineering guidance

Rules:

1. Preserve the original business intent.
2. Use the retrieved guidance as supporting knowledge.
3. Do not invent facts, standards, policies, thresholds, or values.
4. Keep recommendations practical.
5. Produce an improved requirement when improvement is possible.
6. If the requirement has no issue, keep the improved requirement
   unchanged.
7. Do not add unnecessary features.
8. Do not make business decisions on behalf of the user or stakeholder.

IMPORTANT DECISION-PRESERVATION RULE:

If improving the requirement requires a decision that has not been
specified, DO NOT choose an option yourself.

Examples of decisions that must NOT be invented:

- automatic vs manual
- optional vs mandatory
- specific threshold values
- retention period
- timeout value
- security level
- approval rules
- priority
- frequency
- business policy

Instead, preserve the decision explicitly.

For example:

Original:
"The system should process requests automatically or manually."

Do NOT produce:
"The system shall process requests automatically."

A better improvement is:
"The system shall support request processing through automatic
or manual processing, with the processing mode determined by
the responsible stakeholder."

The goal is to improve clarity without changing the decision
that belongs to the user, stakeholder, or business owner.

Evidence and recommendations must remain grounded in the
provided requirement.
"""


def generate_recommendation(
    requirement: Requirement,
    issue_label: str,
    severity: str,
    explanation: str,
    evidence: str,
    retrieved_context: str,
    sources: list[str],
) -> Recommendation:

    user_prompt = f"""
Requirement ID:
{requirement.id}

Original Requirement:
{requirement.text}

Issue:
{issue_label}

Severity:
{severity}

Explanation:
{explanation}

Evidence:
{evidence}

Retrieved Requirements Engineering Guidance:
{retrieved_context}

Knowledge Sources:
{sources}

Generate:

1. A practical recommendation.
2. An improved requirement.

Do not make unspecified business decisions.
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
        response_format=Recommendation,
    )

    return response.choices[0].message.parsed