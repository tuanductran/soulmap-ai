"""Drift checker for docs/engineering/API.md against the Python source it describes.

``docs/engineering/API.md`` is hand-written, not generated: it explains SoulMap's
local CLI/JSON contracts in prose, with policy notes and historical corrections
an automated tool cannot reconstruct. This module never writes to that file. It
only checks two narrow, mechanical claims the doc makes about the source, so a
maintainer who changes the source and forgets the doc gets a loud failure
instead of silent drift:

1. Every ``python -m <module>`` command the doc references still exists and
   still has a ``__main__`` entrypoint. This catches a documented module being
   renamed, moved, or having its CLI entrypoint removed.
2. Every ``primary_framework`` value ``framework_selector.py`` can emit is
   listed in the doc's documented output enum, and vice versa. This catches a
   new or removed framework landing in the router without a matching doc
   update, which is exactly the kind of change this file exists to describe.

Deliberately not checked: whether every module with a ``__main__`` block gets
its own doc section. ``API.md`` already covers the detector modules under
``src/soulmap/runtime/detectors/`` with one blanket paragraph plus a single
example, by design, and several internal modules (``scope_classifier.py``,
``stage_detector.py``, ``conversation_synthesizer.py``, ``markdown_contract.py``,
``soulmap_demo.py``) are intentionally documented elsewhere or not documented
individually at all. A literal "every entrypoint needs its own section" rule
would flag all of that pre-existing, correct structure as broken.
"""

from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path

_API_DOC_RELATIVE_PATH = Path("docs/engineering/API.md")
_FRAMEWORK_SELECTOR_RELATIVE_PATH = Path(
    "src/soulmap/runtime/routing/framework_selector.py"
)
_SIMPLE_SELECTION_HELPER = "_simple_selection"
_PRIMARY_FRAMEWORK_KEY = "primary_framework"

_MODULE_REFERENCE_RE = re.compile(r"python -m ([A-Za-z0-9_.]+)")
_DOCUMENTED_ENUM_RE = re.compile(r'"primary_framework":\s*"([^"]+)"')


@dataclass(frozen=True, slots=True)
class Issue:
    """One drift finding.

    Attributes:
        path: File the finding is about (always the doc, since this checker
            never faults the source for the doc being out of date).
        message: Human-readable description of exactly what drifted.
    """

    path: Path
    message: str


def _has_main_block(tree: ast.Module) -> bool:
    """Report whether a parsed module has a top-level ``__main__`` guard."""
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "__name__"
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value == "__main__"
        ):
            return True
    return False


def _documented_module_references(doc_text: str) -> list[str]:
    """Extract every ``python -m <dotted.module>`` reference from the doc."""
    return _MODULE_REFERENCE_RE.findall(doc_text)


def _check_module_references(repo_root: Path, doc_text: str) -> list[Issue]:
    issues: list[Issue] = []
    for dotted in _documented_module_references(doc_text):
        if not dotted.startswith("soulmap."):
            continue
        source_path = repo_root / "src" / Path(*dotted.split(".")).with_suffix(".py")
        if not source_path.exists():
            issues.append(
                Issue(
                    _API_DOC_RELATIVE_PATH,
                    f"references 'python -m {dotted}', but "
                    f"src/{source_path.relative_to(repo_root / 'src')} does not exist. "
                    "The module was likely renamed or removed; update the doc.",
                )
            )
            continue

        tree = ast.parse(
            source_path.read_text(encoding="utf-8"), filename=str(source_path)
        )
        if not _has_main_block(tree):
            issues.append(
                Issue(
                    _API_DOC_RELATIVE_PATH,
                    f"references 'python -m {dotted}' as a CLI entrypoint, but "
                    f"{dotted} no longer has an `if __name__ == '__main__':` block. "
                    "The entrypoint was likely removed; update the doc.",
                )
            )
    return issues


def _documented_primary_framework_values(doc_text: str) -> set[str]:
    match = _DOCUMENTED_ENUM_RE.search(doc_text)
    if not match:
        return set()
    return {value.strip() for value in match.group(1).split("|") if value.strip()}


def _dict_primary_framework_value(node: ast.Dict) -> str | None:
    for key, value in zip(node.keys, node.values, strict=True):
        if (
            isinstance(key, ast.Constant)
            and key.value == _PRIMARY_FRAMEWORK_KEY
            and isinstance(value, ast.Constant)
            and isinstance(value.value, str)
        ):
            return value.value
    return None


def _call_primary_framework_value(node: ast.Call) -> str | None:
    if not (
        isinstance(node.func, ast.Name) and node.func.id == _SIMPLE_SELECTION_HELPER
    ):
        return None
    if not node.args:
        return None
    first_arg = node.args[0]
    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
        return first_arg.value
    return None


def _source_primary_framework_values(repo_root: Path) -> set[str]:
    """Statically collect every ``primary_framework`` value the selector can emit.

    Covers both shapes the selector uses: a literal
    ``{"primary_framework": "X", ...}`` dict, and the shared
    ``_simple_selection("X", ...)`` helper for single-signal Mirror
    frameworks. Never imports the module, only parses it.
    """
    source_path = repo_root / _FRAMEWORK_SELECTOR_RELATIVE_PATH
    if not source_path.exists():
        return set()

    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    values: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            value = _dict_primary_framework_value(node)
        elif isinstance(node, ast.Call):
            value = _call_primary_framework_value(node)
        else:
            continue
        if value is not None:
            values.add(value)
    return values


def _check_primary_framework_enum(repo_root: Path, doc_text: str) -> list[Issue]:
    documented = _documented_primary_framework_values(doc_text)
    source = _source_primary_framework_values(repo_root)
    if not source:
        # framework_selector.py is missing or unparsable in a way that yields no
        # values at all; the module-reference check above already reports a
        # missing file, so do not also report a confusing empty-set mismatch.
        return []

    issues: list[Issue] = []
    missing_from_doc = sorted(source - documented)
    if missing_from_doc:
        issues.append(
            Issue(
                _API_DOC_RELATIVE_PATH,
                "framework_selector.py can emit primary_framework value(s) "
                f"{missing_from_doc} that are not listed in the documented "
                "output enum. Add them to the 'Output' JSON example.",
            )
        )
    stale_in_doc = sorted(documented - source)
    if stale_in_doc:
        issues.append(
            Issue(
                _API_DOC_RELATIVE_PATH,
                f"the documented output enum lists primary_framework value(s) "
                f"{stale_in_doc} that framework_selector.py no longer emits. "
                "Remove them from the 'Output' JSON example.",
            )
        )
    return issues


def check_repo(repo_root: Path) -> list[Issue]:
    """Check ``docs/engineering/API.md`` for drift against the Python source.

    Args:
        repo_root: Repository root.

    Returns:
        Every drift finding. Empty when the doc's mechanical claims about the
        source still hold.
    """
    doc_path = repo_root / _API_DOC_RELATIVE_PATH
    if not doc_path.exists():
        return [
            Issue(
                _API_DOC_RELATIVE_PATH,
                "does not exist. SoulMap's local CLI/JSON contracts are meant "
                "to be documented there; see docs/engineering/repo-contract.md.",
            )
        ]

    doc_text = doc_path.read_text(encoding="utf-8")
    return [
        *_check_module_references(repo_root, doc_text),
        *_check_primary_framework_enum(repo_root, doc_text),
    ]


def main(argv: list[str] | None = None) -> int:
    """Run the API-documentation drift check from the command line.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        0 when the doc's mechanical claims hold, 1 when any drift is found.
    """
    parser = argparse.ArgumentParser(prog="soulmap check-api-docs")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(),
        help="Repo root (default: current directory).",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve()
    issues = check_repo(repo_root)
    if not issues:
        return 0

    for issue in issues:
        print(f"{issue.path}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
