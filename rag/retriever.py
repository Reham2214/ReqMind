import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "requirements_knowledge"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# Load embedding model
embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


# Connect to ChromaDB
client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# Get knowledge base collection
collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def retrieve(
    query: str,
    top_k: int = 4
) -> list[dict]:

    """
    Retrieve the most relevant knowledge
    from the ReqMind knowledge base.
    """

    if not query.strip():
        return []

    # Convert query into embedding
    query_embedding = embedding_model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
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

    for i, document in enumerate(documents):

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
                "distance": distance
            }
        )

    return retrieved


def format_retrieved_context(
    results: list[dict]
) -> str:

    """
    Convert retrieved documents into
    a text context for the LLM.
    """

    if not results:
        return "No relevant knowledge was retrieved."

    context_parts = []

    for i, result in enumerate(
        results,
        start=1
    ):

        context_parts.append(
            f"""
--- Source {i} ---
Source: {result['source']}

{result['text']}
"""
        )

    return "\n".join(
        context_parts
    )


if __name__ == "__main__":

    query = input(
        "Enter your test query: "
    )

    results = retrieve(
        query,
        top_k=4
    )

    print(
        "\nRetrieved Results:\n"
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n--- Result {i} ---"
        )

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Distance: {result['distance']}"
        )

        print(
            result["text"]
        )