from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


RAG_DOCUMENTS_DIR = Path("rag_documents")
CHROMA_DIR = "chroma_db"


def load_guideline_documents():

    documents = []

    for pdf_path in RAG_DOCUMENTS_DIR.rglob("*.pdf"):

        print(f"Loading: {pdf_path}")

        loader = PyPDFLoader(
            str(pdf_path)
        )

        pages = loader.load()

        # Add useful metadata
        for page in pages:

            page.metadata["filename"] = pdf_path.name
            page.metadata["category"] = pdf_path.parent.name

        documents.extend(pages)

    return documents


def build_vector_database():

    documents = load_guideline_documents()

    print(
        f"Loaded {len(documents)} PDF pages."
    )


    # -----------------------------------------
    # Split long pages into smaller chunks
    # -----------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(
        documents
    )

    print(
        f"Created {len(chunks)} chunks."
    )


    # -----------------------------------------
    # Local Ollama embeddings
    # -----------------------------------------

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )


    # -----------------------------------------
    # Store chunks in local Chroma
    # -----------------------------------------

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="clinical_guidelines",
        persist_directory=CHROMA_DIR
    )

    print(
        "Chroma database created successfully."
    )


if __name__ == "__main__":
    build_vector_database()