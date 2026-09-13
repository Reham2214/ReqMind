import os
from dotenv import load_dotenv
from openai import OpenAI
from utils.schemas import ExtractionResult

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


SYSTEM_PROMPT = """
You are the Requirement Extraction Agent in ReqMind.

Your task is to extract software requirements from a requirements document.

Rules:
1. Extract only actual software/system requirements.
2. Ignore headings, introductions, notes, and general descriptions.
3. Keep the original requirement wording as much as possible.
4. Do not analyze or improve the requirements.
5. Give every requirement a unique ID such as R001, R002, R003.
6. Return all extracted requirements in structured format.
"""


def extract_requirements(document_text: str) -> ExtractionResult:

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
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

    return response.choices[0].message.parsed