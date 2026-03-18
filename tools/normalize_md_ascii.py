from __future__ import annotations

import argparse
from pathlib import Path

from tools._markdown import iter_markdown_files
from tools._repo import REPO_ROOT

REPLACEMENTS: dict[str, str] = {
    "\u2019": "'",  # RIGHT SINGLE QUOTATION MARK
    "\u2018": "'",  # LEFT SINGLE QUOTATION MARK
    "\u201c": '"',  # LEFT DOUBLE QUOTATION MARK
    "\u201d": '"',  # RIGHT DOUBLE QUOTATION MARK
    "\u2014": "-",  # EM DASH
    "\u2013": "-",  # EN DASH
    "\u2026": "...",  # HORIZONTAL ELLIPSIS
    "\u00a0": " ",  # NO-BREAK SPACE
}


def normalize_text(text: str) -> str:
    for src, dst in REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Normalize Markdown typography to ASCII for portability."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write changes, only report if any file would change.",
    )
    args = parser.parse_args(argv)

    changed: list[Path] = []
    for path in iter_markdown_files(REPO_ROOT):
        original = path.read_text(encoding="utf-8")
        normalized = normalize_text(original)
        if normalized != original:
            changed.append(path)
            if not args.check:
                path.write_text(normalized, encoding="utf-8")

    if args.check:
        if changed:
            for path in changed:
                print(path.relative_to(REPO_ROOT))
            return 1
        return 0

    if changed:
        print(f"OK: normalized {len(changed)} file(s).")
    else:
        print("OK: no changes needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
