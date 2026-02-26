import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.agent.agent import SYSTEM_PROMPT, analyze_documents, run_agent


def _make_mock_response(text: str) -> MagicMock:
    response = MagicMock()
    response.content = [MagicMock(text=text)]
    return response


def _write_temp_pdf() -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.write(b"%PDF-1.4 fake pdf")
    tmp.close()
    return Path(tmp.name)


# --- run_agent tests ---

def test_run_agent_appends_messages():
    with patch("src.agent.agent.client.messages.create", return_value=_make_mock_response("Tax guidance.")):
        response, history = run_agent("What is a W-2?", [])

    assert history[0] == {"role": "user", "content": "What is a W-2?"}
    assert history[1] == {"role": "assistant", "content": "Tax guidance."}
    assert response == "Tax guidance."


def test_run_agent_preserves_existing_history():
    prior = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
    ]
    with patch("src.agent.agent.client.messages.create", return_value=_make_mock_response("A W-2 reports wages.")):
        _, history = run_agent("What is a W-2?", prior)

    assert len(history) == 4
    assert history[2]["role"] == "user"
    assert history[3]["role"] == "assistant"


# --- analyze_documents tests ---

def test_analyze_documents_returns_analysis_and_history():
    path = _write_temp_pdf()
    try:
        mock_response = _make_mock_response("You are owed a $500 refund.")
        with patch("src.agent.agent.client.messages.create", return_value=mock_response):
            analysis, history = analyze_documents([str(path)])

        assert analysis == "You are owed a $500 refund."
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "You are owed a $500 refund."
    finally:
        path.unlink()


def test_analyze_documents_includes_filenames_in_history():
    path = _write_temp_pdf()
    try:
        with patch("src.agent.agent.client.messages.create", return_value=_make_mock_response("Analysis.")):
            _, history = analyze_documents([str(path)])

        assert path.name in history[0]["content"]
    finally:
        path.unlink()


def test_analyze_documents_sends_multipart_content():
    path = _write_temp_pdf()
    try:
        with patch("src.agent.agent.client.messages.create", return_value=_make_mock_response("ok")) as mock_create:
            analyze_documents([str(path)])

        call_messages = mock_create.call_args.kwargs["messages"]
        content = call_messages[0]["content"]
        types = [block["type"] for block in content]
        assert "text" in types
        assert "document" in types
    finally:
        path.unlink()


# --- system prompt check ---

def test_system_prompt_mentions_tax_professional():
    assert "tax professional" in SYSTEM_PROMPT.lower()
