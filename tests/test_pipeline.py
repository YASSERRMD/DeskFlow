import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.retriever import (
    load_knowledge_base,
    build_index,
    retrieve_context,
    invalidate_index,
)


RUNBOOKS_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "runbooks")


def _make_result(form_id: str, data: dict) -> dict:
    """Helper: create a plain FormResult-like dict for testing."""
    return {"form_id": form_id, "typed_data": data}


class TestLoadKnowledgeBase:
    def test_loads_real_runbooks(self):
        chunks = load_knowledge_base(RUNBOOKS_DIR)
        assert len(chunks) > 0, "Should load at least one chunk from runbooks"

    def test_chunk_structure(self):
        chunks = load_knowledge_base(RUNBOOKS_DIR)
        for chunk in chunks[:5]:
            assert "filename" in chunk
            assert "content" in chunk
            assert "chunk_index" in chunk
            assert isinstance(chunk["content"], str)
            assert len(chunk["content"]) > 0

    def test_all_md_files_loaded(self):
        chunks = load_knowledge_base(RUNBOOKS_DIR)
        filenames = {c["filename"] for c in chunks}
        expected = {"vpn.md", "account.md", "hardware.md", "software.md",
                    "network.md", "email.md", "access.md", "procurement.md",
                    "onboarding.md", "general.md"}
        assert expected.issubset(filenames), f"Missing files: {expected - filenames}"

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            chunks = load_knowledge_base(tmpdir)
            assert chunks == []

    def test_nonexistent_directory(self):
        chunks = load_knowledge_base("/nonexistent/path")
        assert chunks == []

    def test_chunks_have_overlap(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = os.path.join(tmpdir, "test.md")
            content = " ".join([f"word{i}" for i in range(600)])
            with open(fpath, "w") as f:
                f.write(content)
            chunks = load_knowledge_base(tmpdir)
            assert len(chunks) >= 2, "600-word doc should produce at least 2 chunks"


class TestBuildIndex:
    def test_builds_without_error(self):
        chunks = load_knowledge_base(RUNBOOKS_DIR)
        vectorizer, matrix, returned_chunks = build_index(chunks)
        assert vectorizer is not None
        assert matrix is not None
        assert len(returned_chunks) == len(chunks)

    def test_matrix_shape(self):
        chunks = load_knowledge_base(RUNBOOKS_DIR)
        vectorizer, matrix, _ = build_index(chunks)
        assert matrix.shape[0] == len(chunks)


class TestRetrieveContext:
    def setup_method(self):
        invalidate_index()

    def test_returns_string(self):
        result = _make_result("vpn_issue", {"os": "Windows 11", "error_type": "cant_connect"})
        context = retrieve_context(result, knowledge_dir=RUNBOOKS_DIR)
        assert isinstance(context, str)

    def test_returns_nonempty_for_vpn(self):
        result = _make_result("vpn_issue", {
            "os": "Windows 11", "vpn_client": "Cisco AnyConnect",
            "error_type": "cant connect", "urgency": "high",
        })
        context = retrieve_context(result, knowledge_dir=RUNBOOKS_DIR)
        assert len(context) > 0, "Should retrieve non-empty context for VPN issue"

    def test_returns_nonempty_for_account(self):
        result = _make_result("account_issue", {
            "issue_type": "Account locked", "system": "Windows Login", "urgency": "critical",
        })
        context = retrieve_context(result, knowledge_dir=RUNBOOKS_DIR)
        assert len(context) > 0

    def test_context_contains_relevant_file(self):
        result = _make_result("network_issue", {
            "issue": "No internet", "connection_type": "WiFi",
        })
        context = retrieve_context(result, knowledge_dir=RUNBOOKS_DIR)
        assert len(context) > 0

    def test_top_k_limits_results(self):
        result = _make_result("hardware_issue", {
            "device_type": "laptop", "issue": "not turning on",
        })
        context = retrieve_context(result, top_k=2, knowledge_dir=RUNBOOKS_DIR)
        # Each chunk is prefixed with "[filename.md]\n"
        import re
        chunk_headers = re.findall(r'^\[.+\.md\]', context, re.MULTILINE)
        assert len(chunk_headers) <= 2, f"Expected at most 2 chunks, got {len(chunk_headers)}"

    def test_empty_knowledge_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            invalidate_index()
            result = _make_result("vpn_issue", {})
            context = retrieve_context(result, knowledge_dir=tmpdir)
            assert context == ""

    def test_accepts_plain_dict_input(self):
        invalidate_index()
        result = {"form_id": "software_issue", "typed_data": {"app_name": "Chrome", "issue_type": "crashing"}}
        context = retrieve_context(result, knowledge_dir=RUNBOOKS_DIR)
        assert isinstance(context, str)
