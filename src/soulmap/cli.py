"""The ``soulmap`` command-line entry point.

Dispatches every developer command (format, lint, test, build, the evaluation
runs, and the repository checkers) to its implementation module, so
contributors and CI share one command surface.
"""

from __future__ import annotations

import argparse
import subprocess
from collections.abc import Callable

from soulmap.devtools.audit import knowledge as audit_knowledge
from soulmap.devtools.checks import (
    check_api_docs,
    check_freshness,
    check_markdown_case,
    check_markdown_links,
)
from soulmap.devtools.cli import bootstrap_venv
from soulmap.devtools.evals import (
    eval_groups,
    eval_markdown_contracts,
    eval_responses,
)
from soulmap.devtools.packaging import build_skill, library
from soulmap.devtools.quality import format as format_tool
from soulmap.devtools.quality import lint as lint_tool
from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.devtools.support.run import python_module
from soulmap.runtime.experimental import soulmap_demo
from soulmap.runtime.guards import markdown_contract

CommandHandler = Callable[[list[str]], int]


def _run_pytest(args: list[str]) -> int:
    pytest_args = args or ["-q"]
    try:
        python_module("pytest", *pytest_args, cwd=REPO_ROOT)
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    return 0


def _command_table() -> dict[str, CommandHandler]:
    return {
        "audit-knowledge": audit_knowledge.main,
        "bootstrap": bootstrap_venv.main,
        "build": build_skill.main,
        "check-api-docs": check_api_docs.main,
        "check-case": check_markdown_case.main,
        "check-freshness": check_freshness.main,
        "check-links": check_markdown_links.main,
        "demo": soulmap_demo.main,
        "eval-groups": eval_groups.main,
        "eval-markdown-contracts": eval_markdown_contracts.main,
        "eval-responses": eval_responses.main,
        "format": format_tool.main,
        "lint": lint_tool.main,
        "library-manifest": library.main,
        "markdown-contract": markdown_contract.main,
        "test": _run_pytest,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser.

    Returns:
        A parser accepting a command name and the remaining arguments, which
        are forwarded verbatim to that command's own parser.
    """
    parser = argparse.ArgumentParser(
        prog="soulmap",
        description="SoulMap developer and runtime command-line tools.",
    )
    parser.add_argument("command", choices=sorted(_command_table()))
    parser.add_argument("args", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Dispatch a command and return its exit code.

    A leading ``--`` in the forwarded arguments is dropped, so both
    ``soulmap lint --skip-tests`` and ``soulmap lint -- --skip-tests`` reach
    the command the same way.

    Args:
        argv: Command-line arguments, or None to read from ``sys.argv``.

    Returns:
        The dispatched command's exit code.
    """
    parser = build_parser()
    parsed = parser.parse_args(argv)
    command = _command_table()[parsed.command]
    forwarded_args = parsed.args
    if forwarded_args[:1] == ["--"]:
        forwarded_args = forwarded_args[1:]
    return command(forwarded_args)


if __name__ == "__main__":
    raise SystemExit(main())
