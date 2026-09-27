from soulmap.devtools.support.repo import REPO_ROOT
from soulmap.runtime.knowledge.runtime_registry import (
    runtime_section,
    runtime_skill_path,
)


def test_runtime_registry_resolves_known_domain_source() -> None:
    path = runtime_skill_path("grief-companion")
    assert path == REPO_ROOT / "skills/frameworks/grief-companion.md"
    assert (
        runtime_section("grief-companion", "contract") == "Runtime detection contract"
    )
    assert runtime_skill_path("shadow-patterns") != runtime_skill_path("self-compassion")


def test_detector_modules_do_not_embed_skill_source_paths() -> None:
    detector_root = REPO_ROOT / "src/soulmap/runtime/detectors"
    violations: list[str] = []

    for path in sorted(detector_root.glob("*_detector.py")):
        content = path.read_text(encoding="utf-8")
        if 'default_skill_path("skills/' in content:
            violations.append(str(path.relative_to(REPO_ROOT)))

    assert not violations, "\n".join(violations)
