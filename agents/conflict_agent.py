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

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


SYSTEM_PROMPT = """
You are the Relationship Analysis Agent in ReqMind.

Your responsibility is to compare TWO software requirements.

You detect ONLY:

1. No Issue
2. Duplication
3. Conflict
4. Inconsistency

Definitions:

Duplication:
Both requirements express the same or substantially overlapping
behavior.

Conflict:
The requirements impose mutually incompatible behaviors,
constraints, rules, or values.

Inconsistency:
The requirements refer to concepts, rules, values, or behaviors
that do not agree consistently, even if they are not directly
mutually exclusive.

No Issue:
The two requirements can coexist without a meaningful relationship
problem.

Rules:

1. Compare only the two provided requirements.
2. Do not use information that is not present in the requirements.
3. Do not invent missing information.
4. Explain exactly why the relationship exists.
5. Evidence must reference the provided requirement IDs.
6. Return "No Issue" when there is no meaningful relationship problem.
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
        show_progress_bar=False,
    )

    similarity_matrix = cosine_similarity(
        embeddings
    )

    pairs = []

    for i, j in combinations(
        range(len(requirements)),
        2
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

ID:
{requirement_a.id}

Text:
{requirement_a.text}


Requirement B:

ID:
{requirement_b.id}

Text:
{requirement_b.text}


Compare the two requirements.
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

    max_workers = min(
        4,
        len(candidate_pairs)
    )

    with ThreadPoolExecutor(
        max_workers=max_workers
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

    issues = [
        result
        for result in results
        if result.issue_label != "No Issue"
    ]

    return RelationshipAnalysisResult(
        issues=issues
    )