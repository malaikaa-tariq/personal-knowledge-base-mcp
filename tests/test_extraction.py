import pytest

from app.services import extraction
from app.services.extraction import (
    DocumentExtractionError,
    extract_text,
)


def test_extract_txt_file():
    content = b"""
Software Engineering Notes

Requirements engineering identifies stakeholder needs.

Testing improves software quality.
"""

    result = extract_text("notes.txt", content)

    assert "Software Engineering Notes" in result
    assert "Requirements engineering" in result
    assert "Testing improves software quality" in result


def test_extract_markdown_file():
    content = b"""
# Artificial Intelligence

Semantic search retrieves documents based on meaning.

## Embeddings

Embeddings convert text into numerical vectors.
"""

    result = extract_text("ai-notes.md", content)

    assert "# Artificial Intelligence" in result
    assert "Semantic search" in result
    assert "Embeddings convert text" in result


def test_extension_is_case_insensitive():
    result = extract_text(
        "NOTES.TXT",
        b"Knowledge base test document"
    )

    assert result == "Knowledge base test document"


def test_unsupported_file_type():
    with pytest.raises(DocumentExtractionError) as exc:
        extract_text("image.png", b"fake image data")

    assert "Unsupported file type" in str(exc.value)


def test_empty_file():
    with pytest.raises(DocumentExtractionError) as exc:
        extract_text("empty.txt", b"")

    assert "empty" in str(exc.value).lower()


def test_empty_document_text():
    with pytest.raises(DocumentExtractionError) as exc:
        extract_text("blank.md", b"   \n\n   ")

    assert "No readable text" in str(exc.value)


def test_pdf_extraction(monkeypatch):
    class FakePage:
        def __init__(self, text):
            self.text = text

        def extract_text(self):
            return self.text

    class FakeReader:
        def __init__(self, stream):
            self.pages = [
                FakePage("Page one knowledge base content."),
                FakePage("Page two semantic search content."),
            ]

    monkeypatch.setattr(extraction, "PdfReader", FakeReader)

    result = extract_text(
        "semester-notes.pdf",
        b"fake-pdf-bytes"
    )

    assert "Page one knowledge base content." in result
    assert "Page two semantic search content." in result