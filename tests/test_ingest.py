from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from langchain_core.documents import Document
from src.ingest import ingest_directory

# ==============================================================================
# FIXTURES: Standardized Environment Initializers
# ==============================================================================

@pytest.fixture
def mock_embeddings():
    """Isolates the OllamaEmbeddings initialization loop."""
    with patch("src.ingest.OllamaEmbeddings") as mock_embed:
        yield mock_embed

@pytest.fixture
def mock_chroma():
    """Isolates the Chroma DB storage constructor and its writer instance."""
    with patch("src.ingest.Chroma") as mock_vector_store:
        mock_instance = MagicMock()
        mock_vector_store.return_value = mock_instance
        # Yielding both as an object or dictionary lets you track class and instance methods
        yield {"class": mock_vector_store, "instance": mock_instance}    

@pytest.fixture
def mock_rmtree():
    """Intercepts filesystem removal triggers."""
    with patch("src.ingest.shutil.rmtree") as mock_wipe:
        yield mock_wipe

# ==============================================================================
# TEST CASES: Verification Matrices
# ==============================================================================

def test_ingest_directory_handles_invalid_path(tmp_path, mock_chroma):
    """
    Test Case 1: Defensive Path Handling
    Ensures that passing a non-existent directory path fails gracefully, 
    bypasses document splitting, and never invokes database instantiation workflows.
    """
    chroma_instance = mock_chroma["instance"]
    invalid_path = Path("/tmp/non_existent_openops_workspace_path")

    # Execute target logic with a guaranteed broken path object
    ingest_directory(
        target_path=invalid_path,
        reset_db=False,
        base_url="http://fake-gateway-proxy:11434",
        db_path=str(tmp_path / "test_chroma_db")
    )

    # Assertions: No down-stream pipeline engines should be touched
    assert chroma_instance.add_documents.called is False

def test_ingest_directory_parses_and_chunks_files_successfully(tmp_path, mock_embeddings, mock_chroma):
    """
    Test Case 2: Happy Path File Traversal & Chunking Data Flow
    Uses the native `tmp_path` directory sandbox to drop actual files, ensuring 
    recursive looping functions cleanly and processes chunked Document arrays into Chroma.
    """
    # 1. Handle Mocks
    chroma_class = mock_chroma["class"]
    chroma_instance = mock_chroma["instance"]

    # 2. Structure a nested, production-like local knowledge tree inside the sandbox
    profile_dir = tmp_path / "data" / "profile"
    jobs_dir = tmp_path / "data" / "jobs"
    profile_dir.mkdir(parents=True)
    jobs_dir.mkdir(parents=True)

    # 3. Write out standard mock textual markdown document blocks
    resume_file = profile_dir / "resume.md"
    resume_file.write_text("Role: Senior Platform Engineer\nSkills: Kubernetes, Go, Python.", encoding="utf-8")

    job_file = jobs_dir / "cloud_job.md"
    job_file.write_text("Target Requirements:\nMust know Infrastructure-as-Code and CI/CD.", encoding="utf-8")

    # 4. Trigger execution block targeting our temporary sandboxed asset path
    test_db_path = str(tmp_path / "test_chroma_db")
    fake_url = "http://172.29.96.1:11434"
    ingest_directory(
        target_path=tmp_path,
        reset_db=False,
        base_url=fake_url,
        db_path=test_db_path,
    )

    # 5. Verification Layers
    # Assert OllamaEmbeddings driver was instantiated with the correct isolated gateway configuration
    mock_embeddings.assert_called_once_with(
        base_url=fake_url,
        model="nomic-embed-text"
    )

    # Assert Chroma store was set up targeting the specific persistent layout specs
    chroma_class.assert_called_once_with(
        collection_name="data",
        embedding_function=mock_embeddings.return_value,
        persist_directory=test_db_path
    )

    # Assert that documents were processed into the store instance
    assert chroma_instance.add_documents.called is True

    # Capture the actual processed document array passed into Chroma
    called_args, called_kwargs = chroma_instance.add_documents.call_args
    processed_chunks = called_kwargs.get("documents", called_args[0] if called_args else [])
    chroma_instance.add_documents.assert_called_once_with(documents=processed_chunks)

    # Verify our chunking constraints split things out cleanly and mapped string path metadata
    assert len(processed_chunks) > 0
    for chunk in processed_chunks:
        assert isinstance(chunk, Document)
        assert "source" in chunk.metadata
        assert isinstance(chunk.metadata["source"], str)  # Confirms string casting validation fix

def test_ingest_directory_triggers_conditional_database_reset(tmp_path, mock_embeddings, mock_chroma, mock_rmtree):
    """
    Test Case 3: State Management Flag Control
    Verifies that passing `reset_db=True` successfully prompts a filesystem purge 
    of the underlying `test_db_path` array prior to spinning up client initializations.
    """
    test_db_path = str(tmp_path / "test_chroma_db")

    # Use a patch on os.path.exists to simulate that a stale chroma_db folder actively exists
    with patch("src.ingest.os.path.exists", return_value=True):
        ingest_directory(
            target_path=tmp_path,
            reset_db=True,
            base_url="http://fake-gateway-proxy:11434",
            db_path=test_db_path
        )
        
        # Verify our context manager cleanly triggered the structural disk wipe routing
        mock_rmtree.assert_called_once_with(test_db_path)

def test_ingest_directory_skips_database_reset_when_flag_is_false(tmp_path, mock_embeddings, mock_chroma, mock_rmtree):
    """
    Test Case 4: State Preservation Verification
    Guarantees that when `reset_db=False`, the pipeline leaves preexisting data indices 
    completely intact, running purely incremental updates.
    """
    with patch("src.ingest.os.path.exists", return_value=True):
        ingest_directory(
            target_path=tmp_path,
            reset_db=False,
            base_url="http://fake-gateway-proxy:11434",
            db_path=str(tmp_path / "test_chroma_db")
        )
        
        # Assert rmtree was NEVER called despite the file path existing
        assert mock_rmtree.called is False
