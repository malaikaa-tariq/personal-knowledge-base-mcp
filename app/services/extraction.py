from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}


class DocumentExtractionError(ValueError):
    """Raised when uploaded document text cannot be extracted."""


def _clean_text(text: str) -> str:
    """
    Normalize extracted text while preserving paragraph boundaries.
    """
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    cleaned_lines: list[str] = []
    blank_pending = False

    for line in text.split("\n"):
        line = " ".join(line.split())

        if line:
            if blank_pending and cleaned_lines:
                cleaned_lines.append("")

            cleaned_lines.append(line)
            blank_pending = False
        else:
            blank_pending = True

    return "\n".join(cleaned_lines).strip()


def _extract_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
    except Exception as exc:
        raise DocumentExtractionError(
            "Unable to read this PDF file."
        ) from exc

    pages: list[str] = []

    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception as exc:
            raise DocumentExtractionError(
                "Failed while extracting text from PDF."
            ) from exc

        if page_text.strip():
            pages.append(page_text)

    return "\n\n".join(pages)


def _extract_text_file(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DocumentExtractionError(
            "Text and Markdown files must use UTF-8 encoding."
        ) from exc


def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Extract readable text from PDF, Markdown, or TXT document bytes.

    Parameters:
        filename: Original uploaded filename.
        file_bytes: Raw uploaded file contents.

    Returns:
        Clean extracted document text.

    Raises:
        DocumentExtractionError:
            For unsupported, empty, unreadable, or textless files.
    """

    if not filename:
        raise DocumentExtractionError("Filename is required.")

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise DocumentExtractionError(
            "Unsupported file type. Only PDF, MD, and TXT files are allowed."
        )

    if not file_bytes:
        raise DocumentExtractionError("The uploaded file is empty.")

    if extension == ".pdf":
        raw_text = _extract_pdf(file_bytes)
    else:
        raw_text = _extract_text_file(file_bytes)

    cleaned_text = _clean_text(raw_text)

    if not cleaned_text:
        raise DocumentExtractionError(
            "No readable text was found in the uploaded document."
        )

    return cleaned_text