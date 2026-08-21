import pytest

from app.services.chunking import chunk_text


def test_empty_text_returns_empty_list():
    assert chunk_text("") == []
    assert chunk_text("   \n\n   ") == []


def test_short_text_creates_single_chunk():
    text = """
    Software engineering is the systematic approach
    to designing and maintaining software.
    """

    chunks = chunk_text(text)

    assert len(chunks) == 1
    assert "Software engineering" in chunks[0]


def test_paragraphs_are_kept_together_when_possible():
    text = """
    Requirements engineering identifies stakeholder needs.

    Software testing verifies that requirements are satisfied.
    """

    chunks = chunk_text(
        text,
        chunk_size=30,
        overlap=5,
    )

    assert len(chunks) == 1
    assert "Requirements engineering" in chunks[0]
    assert "Software testing" in chunks[0]


def test_long_text_creates_multiple_chunks():
    words = [f"word{i}" for i in range(100)]
    text = " ".join(words)

    chunks = chunk_text(
        text,
        chunk_size=30,
        overlap=5,
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert len(chunk.split()) <= 30


def test_overlap_between_long_chunks():
    words = [f"word{i}" for i in range(50)]
    text = " ".join(words)

    chunks = chunk_text(
        text,
        chunk_size=20,
        overlap=5,
    )

    first_chunk_words = chunks[0].split()
    second_chunk_words = chunks[1].split()

    assert first_chunk_words[-5:] == second_chunk_words[:5]


def test_multiple_paragraph_chunks_have_overlap():
    paragraph_one = " ".join(
        [f"first{i}" for i in range(15)]
    )

    paragraph_two = " ".join(
        [f"second{i}" for i in range(15)]
    )

    text = f"{paragraph_one}\n\n{paragraph_two}"

    chunks = chunk_text(
        text,
        chunk_size=20,
        overlap=5,
    )

    assert len(chunks) == 2

    assert (
        chunks[0].split()[-5:]
        == chunks[1].split()[:5]
    )


def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_text(
            "Some document text",
            chunk_size=0,
            overlap=0,
        )


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text(
            "Some document text",
            chunk_size=20,
            overlap=20,
        )


def test_negative_overlap():
    with pytest.raises(ValueError):
        chunk_text(
            "Some document text",
            chunk_size=20,
            overlap=-1,
        )