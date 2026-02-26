# Tax Return Agent

An AI-powered agent that helps you navigate your tax return using Claude.

## Features

- Conversational guidance through tax return preparation
- Explains forms, deductions, and credits in plain language
- Covers W-2, 1099, capital gains, and more
- Maintains conversation history for context-aware responses

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jjdimpel/tax-return-agent.git
   cd tax-return-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your Anthropic API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   export ANTHROPIC_API_KEY=your_key_here
   ```

4. Run the agent:
   ```bash
   python -m src.agent.agent
   ```

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/
```

## Disclaimer

This agent provides general tax guidance only. Always consult a licensed tax
professional (CPA or enrolled agent) for advice specific to your situation.
