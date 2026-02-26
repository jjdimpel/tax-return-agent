from unittest.mock import MagicMock, patch

from src.agent.agent import SYSTEM_PROMPT, run_agent


def test_run_agent_appends_user_message():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Here is some tax guidance.")]

    with patch("src.agent.agent.client.messages.create", return_value=mock_response):
        response, history = run_agent("What is a W-2?", [])

    assert history[0] == {"role": "user", "content": "What is a W-2?"}
    assert history[1] == {"role": "assistant", "content": "Here is some tax guidance."}
    assert response == "Here is some tax guidance."


def test_run_agent_preserves_history():
    existing_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help with your taxes?"},
    ]

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="A W-2 reports your wages.")]

    with patch("src.agent.agent.client.messages.create", return_value=mock_response):
        response, history = run_agent("What is a W-2?", existing_history)

    assert len(history) == 4
    assert history[2]["role"] == "user"
    assert history[3]["role"] == "assistant"


def test_system_prompt_contains_disclaimer():
    assert "tax professional" in SYSTEM_PROMPT.lower() or "licensed" in SYSTEM_PROMPT.lower()
