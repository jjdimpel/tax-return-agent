import base64
import tempfile
from pathlib import Path

import pytest

from src.agent.document_processor import load_document


def _write_temp_file(suffix: str, content: bytes = b"fake content") -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


def test_load_pdf_returns_document_block():
    path = _write_temp_file(".pdf", b"%PDF-1.4 fake pdf content")
    try:
        block = load_document(str(path))
        assert block["type"] == "document"
        assert block["source"]["media_type"] == "application/pdf"
        assert block["source"]["type"] == "base64"
        assert base64.b64decode(block["source"]["data"]) == b"%PDF-1.4 fake pdf content"
    finally:
        path.unlink()


def test_load_jpeg_returns_image_block():
    path = _write_temp_file(".jpg", b"fake jpeg bytes")
    try:
        block = load_document(str(path))
        assert block["type"] == "image"
        assert block["source"]["media_type"] == "image/jpeg"
    finally:
        path.unlink()


def test_load_png_returns_image_block():
    path = _write_temp_file(".png", b"fake png bytes")
    try:
        block = load_document(str(path))
        assert block["type"] == "image"
        assert block["source"]["media_type"] == "image/png"
    finally:
        path.unlink()


def test_load_nonexistent_file_raises():
    with pytest.raises(FileNotFoundError):
        load_document("/tmp/does_not_exist_12345.pdf")


def test_load_unsupported_extension_raises():
    path = _write_temp_file(".docx", b"fake docx")
    try:
        with pytest.raises(ValueError, match="Unsupported file type"):
            load_document(str(path))
    finally:
        path.unlink()


def test_returned_block_has_no_extra_keys():
    path = _write_temp_file(".pdf", b"pdf data")
    try:
        block = load_document(str(path))
        assert set(block.keys()) == {"type", "source"}
    finally:
        path.unlink()
