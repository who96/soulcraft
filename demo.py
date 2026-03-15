#!/usr/bin/env python3
"""SoulCraft Demo — load a compiled soul.md and chat with it.

Usage:
    python demo.py                              # interactive, defaults to Linus
    python demo.py --soul warren-buffett        # use Buffett soul
    python demo.py --soul linus-torvalds --query "Review this code: ..."
    python demo.py --team code-review --query "Review this code: ..."

Requirements:
    pip install openai   (or any OpenAI-compatible client)

    Set OPENAI_API_KEY or OPENAI_BASE_URL env vars as needed.
    Works with any OpenAI-compatible API (OpenAI, Ollama, vLLM, etc.)
"""

import argparse
import sys
from pathlib import Path

SOULS_DIR = Path(__file__).resolve().parent / "souls"
TEAMS_DIR = Path(__file__).resolve().parent / "teams"


def load_soul_md(soul_id: str) -> str:
    soul_path = SOULS_DIR / soul_id / "soul.md"
    if not soul_path.exists():
        available = [p.parent.name for p in SOULS_DIR.glob("*/soul.md")]
        print(f"ERROR: Soul '{soul_id}' not found.", file=sys.stderr)
        print(f"Available souls: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)
    return soul_path.read_text()


def load_team_souls(team_id: str) -> list[tuple[str, str]]:
    """Load team-tuned soul.md files for a team.

    Returns list of (soul_id, soul_md_content) in pipeline order.
    """
    import yaml

    team_path = TEAMS_DIR / team_id / "team.yaml"
    if not team_path.exists():
        available = [p.parent.name for p in TEAMS_DIR.glob("*/team.yaml")]
        print(f"ERROR: Team '{team_id}' not found.", file=sys.stderr)
        print(f"Available teams: {', '.join(available)}", file=sys.stderr)
        sys.exit(1)

    build_dir = TEAMS_DIR / team_id / "build"
    if not build_dir.exists():
        print(f"ERROR: Team '{team_id}' not compiled. Run:", file=sys.stderr)
        print(f"    python -m compiler.team_compile teams/{team_id}/team.yaml", file=sys.stderr)
        sys.exit(1)

    with open(team_path) as f:
        team = yaml.safe_load(f)

    souls = []
    for entry in team["souls"]:
        ref = entry["soul_ref"]
        md_path = build_dir / ref / "soul.md"
        if not md_path.exists():
            print(f"ERROR: Team-tuned soul '{ref}' not found at {md_path}", file=sys.stderr)
            print(f"    Recompile: python -m compiler.team_compile teams/{team_id}/team.yaml",
                  file=sys.stderr)
            sys.exit(1)
        souls.append((ref, md_path.read_text()))
    return souls


def build_handoff_prompt(user_query: str, prior_outputs: list[tuple[str, str]]) -> str:
    """Build user prompt with handoff from prior souls.

    prior_outputs: list of (soul_id, response_text) from earlier pipeline stages.
    """
    if not prior_outputs:
        return user_query

    parts = []
    for soul_id, output in prior_outputs:
        parts.append(f"===SOULCRAFT_HANDOFF_V1 soul={soul_id}===")
        parts.append(output)
        parts.append("===END_HANDOFF===")
        parts.append("")

    parts.append(user_query)
    return "\n".join(parts)


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


def run_team_demo_offline(team_id: str, team_souls: list[tuple[str, str]],
                          user_message: str):
    """Offline team demo — show pipeline structure and prompts."""
    print("=" * 60)
    print(f"  SoulCraft Team Demo — {team_id} (offline mode)")
    print("=" * 60)
    print()
    print(f"📋 Pipeline: {' → '.join(sid for sid, _ in team_souls)}")
    print(f"💬 Query: {user_message}")
    print()

    for i, (soul_id, soul_md) in enumerate(team_souls, 1):
        print(f"--- Stage {i}/{len(team_souls)}: {soul_id} ---")
        print("📜 System Prompt (team-tuned soul.md):")
        print("-" * 40)
        # Show last 400 chars to see Team Context
        if len(soul_md) > 800:
            print(soul_md[:300] + "\n...\n" + soul_md[-400:])
        else:
            print(soul_md)
        print("-" * 40)
        print()

    print("⚠️  To run live, set OPENAI_API_KEY:")
    print(f"    python demo.py --team {team_id} --query \"{user_message}\"")


def run_team_demo_live(team_id: str, team_souls: list[tuple[str, str]],
                       user_message: str, model: str):
    """Live team demo — sequential conversation with handoff."""
    print(f"🤖 Team '{team_id}' — Sequential Pipeline")
    print(f"📋 Pipeline: {' → '.join(sid for sid, _ in team_souls)}")
    print(f"💬 Query: {user_message}\n")

    prior_outputs = []

    for i, (soul_id, soul_md) in enumerate(team_souls, 1):
        print(f"--- Stage {i}/{len(team_souls)}: {soul_id} ---\n")
        prompt = build_handoff_prompt(user_message, prior_outputs)
        response = chat_with_api(soul_md, prompt, model)
        print(f"🗣️  {soul_id}:\n")
        print(response)
        print()
        prior_outputs.append((soul_id, response))

    print("=" * 60)
    print(f"✅ Team pipeline complete ({len(team_souls)} stages)")


def main():
    parser = argparse.ArgumentParser(
        description="Chat with a SoulCraft soul or team",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python demo.py                                          # Offline demo with Linus
  python demo.py --soul warren-buffett                    # Offline demo with Buffett
  python demo.py --query "Is Bitcoin a good investment?"  # Ask Linus about Bitcoin
  python demo.py --team code-review --query "Review this code: ..."
  python demo.py --team code-review --offline             # Show pipeline structure
""",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--soul",
        help="Soul ID to use (default: linus-torvalds)",
    )
    group.add_argument(
        "--team",
        help="Team ID — runs sequential multi-soul pipeline",
    )

    parser.add_argument(
        "--query",
        default="What do you think about microservices architecture?",
        help="Message to send to the soul/team",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="LLM model to use (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Print prompts and exit without calling API",
    )
    args = parser.parse_args()

    # Team mode
    if args.team:
        team_souls = load_team_souls(args.team)

        if args.offline:
            run_team_demo_offline(args.team, team_souls, args.query)
            return

        try:
            from openai import OpenAI  # noqa: F401
            import os

            if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENAI_BASE_URL"):
                print("No OPENAI_API_KEY or OPENAI_BASE_URL set. Running in offline mode.\n")
                run_team_demo_offline(args.team, team_souls, args.query)
                return

            run_team_demo_live(args.team, team_souls, args.query, args.model)
        except ImportError:
            run_team_demo_offline(args.team, team_souls, args.query)
        return

    # Single soul mode (default)
    soul_id = args.soul or "linus-torvalds"
    system_prompt = load_soul_md(soul_id)

    if args.offline:
        run_demo_offline(system_prompt, soul_id, args.query)
        return

    try:
        from openai import OpenAI  # noqa: F401
        import os

        if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENAI_BASE_URL"):
            print("No OPENAI_API_KEY or OPENAI_BASE_URL set. Running in offline mode.\n")
            run_demo_offline(system_prompt, soul_id, args.query)
            return

        print(f"🤖 Chatting with {soul_id} (model: {args.model})...\n")
        print(f"💬 You: {args.query}\n")

        response = chat_with_api(system_prompt, args.query, args.model)

        print(f"🗣️  {soul_id}:\n")
        print(response)
        print()

    except ImportError:
        run_demo_offline(system_prompt, soul_id, args.query)


if __name__ == "__main__":
    main()
