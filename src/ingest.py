import argparse, os, shutil
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from pathlib import Path

def ingest_directory(target_path: Path, reset_db: bool, base_url: str, db_path: str = "./chroma_db") -> None:

    if target_path.is_dir():
        document_list: list[Document] = []
        files = [item for item in target_path.rglob("*") if item.is_file()]

        for file in files:
            with open(file, mode="r", encoding="utf-8") as f:
                document_list.append(
                    Document(
                        page_content=f.read(),
                        metadata={"source": str(file)},
                    )
                )

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""],
        )

        chunked_documents = text_splitter.split_documents(document_list)

        embeddings = OllamaEmbeddings(
            base_url=base_url,
            model="nomic-embed-text"
        )

        if reset_db and os.path.exists(db_path):
            shutil.rmtree(db_path)

        db_writer = Chroma(
            collection_name="data",
            embedding_function=embeddings,
            persist_directory=db_path
        )

        db_writer.add_documents(documents=chunked_documents)
    else:
        print(f"Error: The path '{target_path}' is not a valid directory path.")

if __name__ == "__main__":

    load_dotenv()
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    parser = argparse.ArgumentParser(description="Enumerate files in a dynamic directory.")
    
    parser.add_argument(
        "-p", "--path",
        required=True,
        help="The target directory path to search",
    )

    parser.add_argument(
        "-r", "--reset",
        action="store_true",
        help="If set, delete existing ChromaDB folder"
    )

    parser.add_argument(
        "-db", "--db-path",
        required=False,
        default="./chroma_db",
        help="Path at which to store the ChromaDB"
    )

    args = parser.parse_args()
    target_dir = Path(args.path)
    ingest_directory(target_dir, args.reset, base_url, args.db_path)