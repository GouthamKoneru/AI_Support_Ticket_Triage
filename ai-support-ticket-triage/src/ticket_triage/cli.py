"""Command-line interface."""
import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .core import process_tickets


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Classify support tickets into JSON records")
    parser.add_argument("--input", type=Path, default=Path(os.getenv("TICKETS_DIR", "tickets")))
    parser.add_argument("--output", type=Path, default=Path(os.getenv("TRIAGED_DIR", "triaged")))
    parser.add_argument("--model", default=os.getenv("MODEL_NAME", "deepseek-v4-flash"))
    args = parser.parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY is missing (set it in the environment or .env)")
    with OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.getenv("OPENAI_BASE_URL") or None, timeout=60.0, max_retries=2) as client:
        try:
            success, failures = process_tickets(client, args.model, args.input, args.output)
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
    print(f"Completed: {success} succeeded, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
