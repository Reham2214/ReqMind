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

Your task is to provide a clear recommendation for improving a software requirement.

You will receive:
- Original requirement
- Issue label
- Severity
- Explanation
- Evidence
- Retrieved requirements engineering guidance

Rules:
1. Use the retrieved guidance as supporting knowledge.
2. Do not invent standards or citations.
3. Keep the recommendation practical.
4. Produce an improved requirement when improvement is possible.
5. Preserve the original intent.
6. Do not add unnecessary features.
7. If the requirement has no issue, keep the improved requirement unchanged.
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

Sources:
{sources}

Generate the recommendation and improved requirement.
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