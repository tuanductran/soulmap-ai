"""Reproducible test runs with recorded diagnostic context.

Runs the suite with an explicit pytest-randomly seed and, on failure, records
the seed, worker mode, Python version, and operating system in the GitHub step
summary, then prints a serial reproduction command. Test-ordering and
parallelism failures are only diagnosable when that context survives the run.
"""

from __future__ import annotations

import os
import platform
import secrets
import subprocess
import sys
from pathlib import Path


FOCUSED_TEST_TARGETS = (
    "tests/contract",
    "tests/integration",
    "tests/regression",
    "tests/unit",
)


def build_test_command(
    seed: int,
    workers: str = "auto",
    *,
    scope: str = "full",
) -> list[str]:
    """Build a reproducible pytest command for the selected repository scope."""
    if scope not in {"full", "focused"}:
        raise ValueError(f"Unknown test scope: {scope}")
    targets = [] if scope == "full" else list(FOCUSED_TEST_TARGETS)
    return [
        "uv",
        "run",
        "soulmap",
        "test",
        "-n",
        workers,
        "-q",
        *targets,
        "--",
        f"--randomly-seed={seed}",
    ]


def _summary_path() -> Path | None:
    raw = os.environ.get("GITHUB_STEP_SUMMARY")
    return Path(raw) if raw else None


def _persist_seed(seed: int) -> None:
    env_file = os.environ.get("GITHUB_ENV")
    if env_file:
        with Path(env_file).open("a", encoding="utf-8") as handle:
            handle.write(f"PYTEST_RANDOMLY_SEED={seed}\n")


def _write_failure_summary(
    seed: int,
    workers: str,
    exit_code: int,
    scope: str,
) -> None:
    lines = [
        "## Pytest reproducibility diagnostics",
        "",
        f"- Result: failed with exit code `{exit_code}`",
        f"- Python: `{platform.python_version()}`",
        f"- Operating system: `{platform.platform()}`",
        f"- pytest-xdist workers: `{workers}`",
        f"- Test scope: `{scope}`",
        f"- pytest-randomly seed: `{seed}`",
        "- Serial reproduction:",
        "",
        "  ```bash",
        "  " + " ".join(build_test_command(seed, "0", scope=scope)),
        "  ```",
        "",
        "The serial command preserves the seed while removing xdist parallelism.",
    ]
    summary = _summary_path()
    if summary is not None:
        with summary.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")


def main() -> int:
    scope = os.environ.get("SOULMAP_PYTEST_SCOPE", "full")
    workers = os.environ.get("SOULMAP_PYTEST_WORKERS", "auto")
    seed = int(os.environ.get("PYTEST_RANDOMLY_SEED", secrets.randbits(32)))
    _persist_seed(seed)
    command = build_test_command(seed, workers, scope=scope)
    result = subprocess.run(command, check=False)
    if result.returncode:
        _write_failure_summary(seed, workers, result.returncode, scope)
        serial = build_test_command(seed, "0", scope=scope)
        print(
            "Pytest failed. Reproduce serially with: "
            + " ".join(serial),
            file=sys.stderr,
        )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
