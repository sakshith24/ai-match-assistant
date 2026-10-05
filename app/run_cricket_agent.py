import os
import sys
from typing import List, Dict, Any

# Ensure module routing resolves correctly from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent.cricket_agent import run_cricket_agent


def main():
    """
    CLI loop for interacting with the AI Cricket Match Assistant.
    """
    if os.getenv("OPENAI_API_KEY") is None:
        print("ERROR: OPENAI_API_KEY environment variable not set.")
        print("Please set it before running. Example: export OPENAI_API_KEY='your_key_here'")
        return

    if os.getenv("RAPIDAPI_KEY") is None or os.getenv("RAPIDAPI_HOST") is None:
        print("WARNING: RAPIDAPI_KEY or RAPIDAPI_HOST environment variables not set.")
        print("API tools requiring these keys may not function correctly.")
        if os.getenv("RAPIDAPI_KEY") is None:
            os.environ["RAPIDAPI_KEY"] = "dummy_rapidapi_key"
        if os.getenv("RAPIDAPI_HOST") is None:
            os.environ["RAPIDAPI_HOST"] = "dummy_rapidapi_host"

    print("=" * 60)
    print("AI Cricket Match Assistant")
    print("=" * 60)
    print("Ask a cricket question. Type 'exit' to quit.")
    print("-" * 60)

    conversation_history: List[Dict[str, Any]] = []

    while True:
        user_input = input("> ")
        if user_input.lower().strip() == "exit":
            print("Goodbye!")
            break

        if not user_input.strip():
            continue

        # Pass user message into the loop
        conversation_history.append({"role": "user", "content": user_input})

        agent_response = run_cricket_agent(user_input, conversation_history)

        # Store response in history
        conversation_history.append({"role": "assistant", "content": agent_response})

        print("\nAI:")
        print(agent_response)
        print("-" * 60)


if __name__ == "__main__":
    main()