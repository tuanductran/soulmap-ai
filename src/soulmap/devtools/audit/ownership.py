"""Audit knowledge ownership across runtime consumers and domain routers."""

from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path

from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge.runtime_registry import _registry

_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)")
_CANONICAL_RE = re.compile(
    r"^##\s+Canonical sources\s*$(?P<body>.*?)(?=^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)
_SOURCE_RE = re.compile(r'\bruntime_skill_path\(\s*"([^"]+)"\s*\)')
_DIRECT_RE = re.compile(r'default_skill_path\(\s*"skills/([^"]+)"\s*\)')


@dataclass(frozen=True, slots=True)
class OwnershipFinding:
    kind: str
    path: Path
    detail: str


def _runtime_findings(root: Path) -> tuple[OwnershipFinding, ...]:
    registry = _registry()
    findings: list[OwnershipFinding] = []
    runtime_root = root / "src/soulmap/runtime"

    for path in sorted(runtime_root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if path.name == "pattern_source.py":
            continue
        for match in _DIRECT_RE.finditer(text):
            findings.append(
                OwnershipFinding(
                    "direct-source-path",
                    path,
                    f"skills/{match.group(1)}",
                )
            )
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id != "runtime_skill_path":
                continue
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
    return tuple(findings)


def _domain_findings(root: Path) -> tuple[OwnershipFinding, ...]:
    domains_root = root / "skills/domains"
    findings: list[OwnershipFinding] = []
    memberships: dict[str, list[Path]] = {}

    for router in sorted(domains_root.glob("*/SKILL.md")):
        text = router.read_text(encoding="utf-8")
        match = _CANONICAL_RE.search(text)
        if match is None:
            findings.append(
                OwnershipFinding("missing-canonical-sources", router, "Canonical sources")
            )
            continue
        for target in _LINK_RE.findall(match.group("body")):
            if target.startswith(("http://", "https://")):
                continue
            resolved = (router.parent / target).resolve()
            try:
                relative = resolved.relative_to(root).as_posix()
            except ValueError:
                findings.append(
                    OwnershipFinding("domain-path-escape", router, target)
                )
                continue
            if not resolved.is_file():
                findings.append(
                    OwnershipFinding("missing-domain-source", router, relative)
                )
                continue
            if not relative.startswith("skills/") or not relative.endswith(".md"):
                findings.append(
                    OwnershipFinding("non-knowledge-domain-source", router, relative)
                )
                continue
            memberships.setdefault(relative, []).append(router)

    # Shared membership is intentional and therefore diagnostic, not a failure.
    for source, routers in sorted(memberships.items()):
        if len(routers) > 1:
            findings.append(
                OwnershipFinding(
                    "shared-domain-source",
                    root / source,
                    ", ".join(
                        p.relative_to(root).as_posix() for p in routers
                    ),
                )
            )
    return tuple(findings)


def audit(root: Path) -> tuple[OwnershipFinding, ...]:
    """Return deterministic ownership findings for the repository."""
    return _runtime_findings(root) + _domain_findings(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="soulmap audit-knowledge-ownership")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    findings = audit(args.root.resolve())
    errors = tuple(
        item for item in findings if item.kind != "shared-domain-source"
    )
    print("Knowledge ownership audit")
    print(f"findings: {len(findings)}")
    for item in findings:
        print(
            f"[{'INFO' if item.kind == 'shared-domain-source' else 'ERROR'}] "
            f"{item.kind}: {item.path.relative_to(args.root.resolve())} -> {item.detail}"
        )
    if errors:
        return 1
    print("PASS knowledge ownership boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
