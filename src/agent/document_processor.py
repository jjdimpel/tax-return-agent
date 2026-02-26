import base64
from pathlib import Path

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | {".pdf"}

IMAGE_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def load_document(file_path: str) -> dict:
    """
    Load a tax document and return a Claude API-compatible content block.

    Supports PDFs and images (JPEG, PNG, GIF, WebP).

    Args:
        file_path: Path to the document file.

    Returns:
        A dict representing a Claude API content block (document or image type).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file type is not supported.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{suffix}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    if suffix == ".pdf":
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": data,
            },
        }

    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": IMAGE_MEDIA_TYPES[suffix],
            "data": data,
        },
    }
