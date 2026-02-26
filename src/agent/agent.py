import os
from pathlib import Path

import anthropic

from src.agent.document_processor import load_document

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a knowledgeable tax return assistant. You help users:
- Extract and interpret key figures from tax documents (W-2, 1099-INT, 1099-DIV,
  1099-B, 1098, 1099-R, 1099-SA, Schedule K-1, etc.)
- Identify income, withholding, deductions, and credits
- Estimate federal tax liability using current tax brackets
- Calculate whether the user is likely to owe money or receive a refund
- Explain tax concepts in plain language and answer follow-up questions

Always clarify that you provide general guidance only and that users should consult
a licensed tax professional (CPA or enrolled agent) before filing. Do not store or
transmit personal financial data beyond the current session."""

TAX_ANALYSIS_PROMPT = """Please analyze all the tax documents provided above.

For each document:
1. Identify the form type (W-2, 1099-INT, 1099-DIV, 1099-B, 1098, 1099-R, etc.)
2. Extract all relevant financial figures (wages, interest, dividends, capital gains,
   taxes withheld, mortgage interest paid, retirement distributions, etc.)

After reviewing all documents, provide:
- A summary table of all income sources and amounts
- Total federal (and state if available) taxes already withheld
- Applicable deductions identified (e.g. mortgage interest, student loan interest)
- Estimated federal tax liability using 2024 tax brackets
  (assume single filer unless filing status is visible in the documents)
- Estimated refund or balance owed = total withholding − tax liability
- Any tax credits that may apply based on what you see (e.g. child tax credit,
  education credits, retirement savers credit)

Be explicit about any assumptions you make. Remind the user to consult a licensed
tax professional before filing their return."""


def analyze_documents(file_paths: list[str]) -> tuple[str, list[dict]]:
    """
    Load and analyze tax documents using Claude's vision and PDF capabilities.

    Args:
        file_paths: List of paths to tax document files.

    Returns:
        A tuple of (analysis_text, conversation_history) where conversation_history
        can be passed to run_agent for follow-up questions.
    """
    content = []
    for i, path in enumerate(file_paths, start=1):
        content.append({"type": "text", "text": f"Document {i}: {Path(path).name}"})
        content.append(load_document(path))
    content.append({"type": "text", "text": TAX_ANALYSIS_PROMPT})

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    analysis = response.content[0].text

    # Seed history with a text-only summary so follow-up questions have full context
    # without re-sending the binary document data.
    names = ", ".join(Path(p).name for p in file_paths)
    history = [
        {
            "role": "user",
            "content": (
                f"I have uploaded {len(file_paths)} tax document(s): {names}. "
                "Please analyze them and estimate my refund or amount owed."
            ),
        },
        {"role": "assistant", "content": analysis},
    ]

    return analysis, history


def run_agent(user_message: str, conversation_history: list[dict]) -> tuple[str, list[dict]]:
    """
    Send a follow-up message to the tax agent and return the response.

    Args:
        user_message: The user's input message.
        conversation_history: List of prior messages in the conversation.

    Returns:
        A tuple of (assistant_response, updated_conversation_history).
    """
    conversation_history.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=conversation_history,
    )

    assistant_message = response.content[0].text
    conversation_history.append({"role": "assistant", "content": assistant_message})
    return assistant_message, conversation_history


def main():
    print("Tax Return Agent")
    print("=" * 50)
    print("Commands:")
    print("  upload <path>  Upload a tax document (PDF, JPG, PNG, etc.)")
    print("  analyze        Analyze all uploaded documents")
    print("  clear          Clear uploaded documents and start over")
    print("  quit           Exit")
    print()

    uploaded_files: list[str] = []
    history: list[dict] = []
    analyzed = False

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if user_input.lower().startswith("upload "):
            path = user_input[7:].strip()
            if not Path(path).exists():
                print(f"File not found: {path}\n")
                continue
            uploaded_files.append(path)
            print(f"Document added: {Path(path).name} ({len(uploaded_files)} total)\n")
            continue

        if user_input.lower() == "clear":
            uploaded_files.clear()
            history.clear()
            analyzed = False
            print("Documents cleared.\n")
            continue

        if user_input.lower() == "analyze":
            if not uploaded_files:
                print("No documents uploaded yet. Use 'upload <path>' first.\n")
                continue
            print(f"\nAnalyzing {len(uploaded_files)} document(s), please wait...\n")
            try:
                analysis, history = analyze_documents(uploaded_files)
                print(f"Agent: {analysis}\n")
                analyzed = True
            except Exception as e:
                print(f"Error during analysis: {e}\n")
            continue

        # Regular conversational follow-up
        if not analyzed and uploaded_files:
            print("Tip: Type 'analyze' to analyze your uploaded documents first.\n")

        try:
            response, history = run_agent(user_input, history)
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
