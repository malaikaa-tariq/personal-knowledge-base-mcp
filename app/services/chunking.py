import re


DEFAULT_CHUNK_SIZE = 120
DEFAULT_OVERLAP = 24


def _normalize_paragraphs(text: str) -> list[str]:
    """
    Split text by paragraph boundaries and normalize whitespace.
    """
    paragraphs = re.split(r"\n\s*\n", text.strip())

    return [
        " ".join(paragraph.split())
        for paragraph in paragraphs
        if paragraph.strip()
    ]


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:
    """
    Split extracted document text into paragraph-aware chunks.

    - Attempts to keep paragraphs together.
    - Splits very long paragraphs when necessary.
    - Adds word overlap between neighboring chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    if not text or not text.strip():
        return []

    paragraphs = _normalize_paragraphs(text)

    chunks: list[str] = []
    current_words: list[str] = []

    for paragraph in paragraphs:
        paragraph_words = paragraph.split()

        # Handle a paragraph that is itself larger than one chunk.
        if len(paragraph_words) > chunk_size:
            if current_words:
                chunks.append(" ".join(current_words))
                current_words = []

            step = chunk_size - overlap
            start = 0

            while start < len(paragraph_words):
                segment = paragraph_words[start : start + chunk_size]

                if segment:
                    chunks.append(" ".join(segment))

                if start + chunk_size >= len(paragraph_words):
                    break

                start += step

            continue

        # Start first chunk.
        if not current_words:
            current_words = paragraph_words
            continue

        # Paragraph still fits in current chunk.
        if len(current_words) + len(paragraph_words) <= chunk_size:
            current_words.extend(paragraph_words)
            continue

        # Current chunk is full.
        previous_chunk = current_words
        chunks.append(" ".join(previous_chunk))

        overlap_words = (
            previous_chunk[-overlap:]
            if overlap
            else []
        )

        # Ensure overlap + new paragraph does not exceed chunk size.
        allowed_overlap = max(
            0,
            chunk_size - len(paragraph_words),
        )

        if len(overlap_words) > allowed_overlap:
            overlap_words = (
                overlap_words[-allowed_overlap:]
                if allowed_overlap
                else []
            )

        current_words = overlap_words + paragraph_words

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks