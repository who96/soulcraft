#!/usr/bin/env python3
"""SoulCraft Demo — load a compiled soul.md and chat with it.

Usage:
    python demo.py                              # interactive, defaults to Linus
    python demo.py --soul warren-buffett        # use Buffett soul
    python demo.py --soul linus-torvalds --query "Review this code: for i in range(10): for j in range(10): for k in range(10): pass"

Requirements:
    pip install openai   (or any OpenAI-compatible client)

    Set OPENAI_API_KEY or OPENAI_BASE_URL env vars as needed.
    Works with any OpenAI-compatible API (OpenAI, Ollama, vLLM, etc.)
"""

import argparse
import sys
from pathlib import Path

SOULS_DIR = Path(__file__).resolve().parent / "souls"


def load_soul_md(soul_id: str) -> str:
    soul_path = SOULS_DIR / soul_id / "soul.md"
    if not soul_path.exists():
        available = [p.parent.name for p in SOULS_DIR.glob("*/soul.md")]
        print(f"ERROR: Soul '{soul_id}' not found.", file=sys.stderr)
        print(f"Available souls: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)
    return soul_path.read_text()


def chat_with_api(system_prompt: str, user_message: str, model: str) -> str:
    """Send a chat completion request. Returns the assistant's response."""
    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai package not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=2000,
    )
    return response.choices[0].message.content


def run_demo_offline(system_prompt: str, soul_id: str, user_message: str):
    """Offline demo — just print the soul.md and a sample prompt."""
    print("=" * 60)
    print(f"  SoulCraft Demo — {soul_id} (offline mode)")
    print("=" * 60)
    print()
    print("📜 System Prompt (soul.md):")
    print("-" * 40)
    print(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)
    print("-" * 40)
    print()
    print(f"💬 User: {user_message}")
    print()
    print("⚠️  To get a live response, install openai and set OPENAI_API_KEY:")
    print("    pip install openai")
    print("    export OPENAI_API_KEY=sk-...")
    print(f"    python demo.py --soul {soul_id} --query \"{user_message}\"")


def main():
    parser = argparse.ArgumentParser(
        description="Chat with a SoulCraft soul",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python demo.py                                          # Offline demo with Linus
  python demo.py --soul warren-buffett                    # Offline demo with Buffett
  python demo.py --query "Is Bitcoin a good investment?"  # Ask Linus about Bitcoin
  python demo.py --soul warren-buffett --query "Should I buy Tesla?"
""",
    )
    parser.add_argument(
        "--soul",
        default="linus-torvalds",
        help="Soul ID to use (default: linus-torvalds)",
    )
    parser.add_argument(
        "--query",
        default="What do you think about microservices architecture?",
        help="Message to send to the soul",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="LLM model to use (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Print soul.md and exit without calling API",
    )
    args = parser.parse_args()

    system_prompt = load_soul_md(args.soul)

    if args.offline:
        run_demo_offline(system_prompt, args.soul, args.query)
        return

    # Try live API call, fall back to offline
    try:
        from openai import OpenAI  # noqa: F401
        import os

        if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENAI_BASE_URL"):
            print("No OPENAI_API_KEY or OPENAI_BASE_URL set. Running in offline mode.\n")
            run_demo_offline(system_prompt, args.soul, args.query)
            return

        print(f"🤖 Chatting with {args.soul} (model: {args.model})...\n")
        print(f"💬 You: {args.query}\n")

        response = chat_with_api(system_prompt, args.query, args.model)

        print(f"🗣️  {args.soul}:\n")
        print(response)
        print()

    except ImportError:
        run_demo_offline(system_prompt, args.soul, args.query)


if __name__ == "__main__":
    main()
