import os
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations

from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from utils.schemas import (
    Requirement,
    RelationshipIssue,
    RelationshipAnalysisResult,
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)

# Maximum number of relationship-analysis API requests
# running at the same time.
MAX_WORKERS = 4


# Load embedding model once.
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


SYSTEM_PROMPT = """
You are the Relationship Analysis Agent in ReqMind.

Compare two software requirements and determine whether they have a relationship problem.

Allowed labels:

No Issue:
The two requirements can coexist without a problem.

Duplication:
Both requirements express the same or substantially overlapping behavior.

Conflict:
The requirements impose mutually incompatible behaviors or constraints.

Inconsistency:
The requirements use concepts, rules, values, or behaviors that do not agree consistently.

Rules:
- Do not invent information.
- Use only the two provided requirements.
- Explain exactly why the relationship exists.
- Use the requirement IDs in the evidence.
"""


def find_similar_pairs(
    requirements: list[Requirement],
    similarity_threshold: float = 0.55,
) -> list[tuple[Requirement, Requirement]]:

    if len(requirements) < 2:
        return []

    texts = [
        requirement.text
        for requirement in requirements
    ]

    embeddings = embedding_model.encode(
        texts,
        normalize_embeddings=True,
    )

    similarity_matrix = cosine_similarity(
        embeddings
    )

    pairs = []

    for i, j in combinations(
        range(len(requirements)),
        2,
    ):

        similarity = similarity_matrix[i][j]

        if similarity >= similarity_threshold:

            pairs.append(
                (
                    requirements[i],
                    requirements[j],
                )
            )

    return pairs


def analyze_pair(
    requirement_a: Requirement,
    requirement_b: Requirement,
) -> RelationshipIssue:

    user_prompt = f"""
Requirement A:
ID: {requirement_a.id}
Text: {requirement_a.text}

Requirement B:
ID: {requirement_b.id}
Text: {requirement_b.text}

Compare them.
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
        response_format=RelationshipIssue,
    )

    return response.choices[0].message.parsed


def analyze_relationships(
    requirements: list[Requirement],
) -> RelationshipAnalysisResult:

    candidate_pairs = find_similar_pairs(
        requirements
    )

    if not candidate_pairs:
        return RelationshipAnalysisResult(
            issues=[]
        )

    # Analyze candidate pairs in parallel.
    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        results = list(
            executor.map(
                lambda pair: analyze_pair(
                    pair[0],
                    pair[1],
                ),
                candidate_pairs,
            )
        )

    # Keep only actual relationship issues.
    issues = [
        result
        for result in results
        if result.issue_label != "No Issue"
    ]

    return RelationshipAnalysisResult(
        issues=issues
    )