import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a knowledgeable tax return assistant. You help users:
- Understand what documents and forms they need to file their tax return
- Identify deductions and credits they may be eligible for
- Walk through income reporting (W-2, 1099, capital gains, etc.)
- Explain tax concepts in plain language
- Estimate tax liability or refund amounts based on provided information

Always clarify that you provide general guidance and that users should consult a
licensed tax professional (CPA or enrolled agent) for personalized advice.
You do not store or transmit any personal financial data."""


def run_agent(user_message: str, conversation_history: list[dict]) -> tuple[str, list[dict]]:
    """
    Send a message to the tax agent and return the response.

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
    print("=" * 40)
    print("Ask me anything about your tax return. Type 'quit' to exit.\n")

    history = []
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        response, history = run_agent(user_input, history)
        print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    main()
