from pathlib import Path

import chromadb
import fitz

from sentence_transformers import SentenceTransformer


KB_DIR = Path("knowledge_base")

CHROMA_DIR = "chroma_db"

COLLECTION_NAME = "requirements_knowledge"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


def extract_pdf_text(
    pdf_path: Path
) -> str:

    text_parts = []

    document = fitz.open(
        pdf_path
    )

    for page_number, page in enumerate(
        document,
        start=1
    ):

        page_text = page.get_text()

        if page_text.strip():

            text_parts.append(
                f"\n[Page {page_number}]\n"
                f"{page_text}"
            )

    document.close()

    return "\n".join(
        text_parts
    )


def read_text_file(
    file_path: Path
) -> str:

    return file_path.read_text(
        encoding="utf-8"
    )


def read_knowledge_file(
    file_path: Path
) -> str:

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(
            file_path
        )

    if extension in [
        ".md",
        ".txt",
    ]:
        return read_text_file(
            file_path
        )

    return ""


def get_knowledge_files():

    supported_extensions = {
        ".md",
        ".txt",
        ".pdf",
    }

    files = []

    if not KB_DIR.exists():
        return files

    for file_path in KB_DIR.rglob("*"):

        if (
            file_path.is_file()
            and file_path.suffix.lower()
            in supported_extensions
        ):
            files.append(file_path)

    return sorted(files)


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
):

    text = " ".join(
        text.split()
    )

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[
            start:end
        ].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def build_knowledge_base():

    print(
        "Starting Knowledge Base ingestion..."
    )

    client = chromadb.PersistentClient(
        path=CHROMA_DIR
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    files = get_knowledge_files()

    if not files:

        raise RuntimeError(
            "No knowledge base files were found."
        )

    documents = []
    ids = []
    metadatas = []

    counter = 0

    for file_path in files:

        print(
            f"Reading: {file_path}"
        )

        text = read_knowledge_file(
            file_path
        )

        if not text.strip():

            print(
                f"Skipped empty file: "
                f"{file_path.name}"
            )

            continue

        chunks = chunk_text(
            text
        )

        relative_source = str(
            file_path.relative_to(
                KB_DIR
            )
        )

        source_type = (
            "pdf"
            if file_path.suffix.lower()
            == ".pdf"
            else "guideline"
        )

        for chunk_index, chunk in enumerate(
            chunks
        ):

            document_id = (
                f"{relative_source}"
                f"_chunk_{chunk_index}"
                f"_{counter}"
            )

            documents.append(
                chunk
            )

            ids.append(
                document_id
            )

            metadatas.append(
                {
                    "source": relative_source,
                    "source_type": source_type,
                    "chunk": chunk_index,
                }
            )

            counter += 1

    if not documents:

        raise RuntimeError(
            "No text chunks were created."
        )

    print(
        f"Creating embeddings for "
        f"{len(documents)} chunks..."
    )

    embeddings = (
        embedding_model.encode(
            documents,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        .tolist()
    )

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print("=" * 60)

    print(
        "Knowledge Base completed successfully."
    )

    print(
        f"Files processed: {len(files)}"
    )

    print(
        f"Chunks stored: {len(documents)}"
    )

    print(
        f"Collection: {COLLECTION_NAME}"
    )

    print("=" * 60)


if __name__ == "__main__":
    build_knowledge_base()