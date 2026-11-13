"""Validate that every input ticket has a valid JSON output."""
import argparse
import json
from pathlib import Path

from .core import parse_classification


def validate(input_dir: Path, output_dir: Path) -> bool:
    tickets = sorted(input_dir.glob("*.txt"))
    if not tickets:
        print("No input tickets found")
        return False
    good = True
    for ticket in tickets:
        output = output_dir / f"{ticket.stem}.json"
        try:
            parse_classification(json.dumps(json.loads(output.read_text(encoding="utf-8"))))
            print(f"PASS {output.name}")
        except (OSError, ValueError, TypeError) as exc:
            print(f"FAIL {output.name}: {exc}")
            good = False
    print(f"Checked {len(tickets)} tickets")
    return good


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ticket JSON outputs")
    parser.add_argument("--input", type=Path, default=Path("tickets"))
    parser.add_argument("--output", type=Path, default=Path("triaged"))
    args = parser.parse_args()
    return 0 if validate(args.input, args.output) else 1


if __name__ == "__main__":
    raise SystemExit(main())
