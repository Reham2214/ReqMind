import chromadb

from sentence_transformers import SentenceTransformer


CHROMA_PATH = "chroma_db"

COLLECTION_NAME = "requirements_knowledge"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def retrieve(
    query: str,
    top_k: int = 8,
) -> list[dict]:

    if not query.strip():
        return []

    if collection.count() == 0:
        return []

    query_embedding = (
        embedding_model.encode(
            query,
            normalize_embeddings=True,
        )
        .tolist()
    )

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=top_k,
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    retrieved = []

    for i, document in enumerate(
        documents
    ):

        metadata = (
            metadatas[i]
            if i < len(metadatas)
            else {}
        )

        distance = (
            distances[i]
            if i < len(distances)
            else None
        )

        retrieved.append(
            {
                "text": document,
                "source": metadata.get(
                    "source",
                    "Knowledge Base"
                ),
                "source_type": metadata.get(
                    "source_type",
                    "unknown"
                ),
                "chunk": metadata.get(
                    "chunk",
                    ""
                ),
                "distance": distance,
            }
        )

    return retrieved


def get_unique_sources(
    results: list[dict]
) -> list[str]:

    sources = []

    for result in results:

        source = result.get(
            "source",
            "Knowledge Base"
        )

        if source not in sources:
            sources.append(source)

    return sources


def format_retrieved_context(
    results: list[dict]
) -> str:

    if not results:

        return (
            "No relevant knowledge "
            "was retrieved."
        )

    context_parts = []

    for i, result in enumerate(
        results,
        start=1
    ):

        context_parts.append(
            f"""
--- Retrieved Knowledge {i} ---

Source:
{result["source"]}

Content:
{result["text"]}
"""
        )

    return "\n".join(
        context_parts
    )