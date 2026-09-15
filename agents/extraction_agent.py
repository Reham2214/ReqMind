import os

from dotenv import load_dotenv
from openai import OpenAI

from utils.schemas import ExtractionResult


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)


SYSTEM_PROMPT = """
You are the Requirement Extraction Agent in ReqMind.

Your task is to extract software requirements from a requirements document.

Rules:

1. Extract only actual software/system requirements.
2. Ignore headings, introductions, notes, explanations, examples,
   and general descriptions.
3. Keep the original requirement wording as much as possible.
4. Do not analyze the requirements.
5. Do not improve or rewrite the requirements.
6. Do not classify issues.
7. Give every extracted requirement a unique ID:
   R001, R002, R003, etc.
8. Return all extracted requirements in structured format.
9. Preserve the meaning and wording of the original requirements.
"""


def extract_requirements(document_text: str) -> ExtractionResult:

    if not document_text.strip():
        return ExtractionResult(requirements=[])

    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": document_text,
            },
        ],
        response_format=ExtractionResult,
    )

    result = response.choices[0].message.parsed

    return result