"""Audit knowledge ownership across runtime consumers."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.source_registry import _registry


@dataclass(frozen=True, slots=True)
class OwnershipFinding:
    """One knowledge ownership audit finding."""

    kind: str
    path: Path
    detail: str


def _runtime_findings(root: Path) -> tuple[OwnershipFinding, ...]:
    registry = _registry(root)
    findings: list[OwnershipFinding] = []
    used_sources: set[str] = set()
    runtime_root = root / "src/soulmap/runtime"

    for path in sorted(runtime_root.rglob("*.py")):
        if path.name in {
            "pattern_source.py",
            "runtime_registry.py",
            "source_registry.py",
        }:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id == "runtime_skill_path":
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Constant):
                    findings.append(
                        OwnershipFinding(
                            "non-literal-source",
                            path,
                            "runtime_skill_path() requires a literal source identifier",
                        )
                    )
                    continue
                source = node.args[0].value
                if not isinstance(source, str) or source not in registry:
                    findings.append(
                        OwnershipFinding(
                            "unregistered-source",
                            path,
                            str(source),
                        )
                    )
                else:
                    used_sources.add(source)
            elif node.func.id == "default_skill_path":
                if (
                    len(node.args) == 1
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)
                    and node.args[0].value.startswith("skills/")
                ):
                    findings.append(
                        OwnershipFinding(
                            "direct-source-path",
                            path,
                            node.args[0].value,
                        )
                    )

    for source in sorted(set(registry) - used_sources):
        findings.append(
            OwnershipFinding(
                "unconsumed-registry-source",
                root / "src/soulmap/runtime/source_registry.py",
                source,
            )
        )
    return tuple(findings)



def audit(root: Path) -> tuple[OwnershipFinding, ...]:
    """Return deterministic ownership findings for the repository."""
    return _runtime_findings(root)


def main(argv: list[str] | None = None) -> int:
    """Run the knowledge ownership audit command."""
    parser = argparse.ArgumentParser(prog="soulmap audit-knowledge-ownership")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    findings = audit(args.root.resolve())
    errors = findings
    print("Knowledge ownership audit")
    print(f"findings: {len(findings)}")
    for item in findings:
        print(
            f"[ERROR] {item.kind}: "
            f"{item.path.relative_to(args.root.resolve())} -> {item.detail}"
        )
    if errors:
        return 1
    print("PASS knowledge ownership boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
