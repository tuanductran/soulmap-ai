"""File-based HTML template rendering for the public SoulMap website."""

from __future__ import annotations

from pathlib import Path
from string import Template

TEMPLATE_ROOT = Path(__file__).with_name("templates")
_TEMPLATE_CACHE: dict[str, tuple[int, int, Template]] = {}


def render_template(name: str, **context: object) -> str:
    """Render a checked-in template with strict substitution and mtime reloads."""
    root = TEMPLATE_ROOT.resolve()
    path = (root / name).resolve()
    if root not in path.parents or not path.is_file():
        raise FileNotFoundError(f"template not found: {name}")
    stat = path.stat()
    cached = _TEMPLATE_CACHE.get(name)
    if cached is None or cached[:2] != (stat.st_mtime_ns, stat.st_size):
        template = Template(path.read_text(encoding="utf-8"))
        _TEMPLATE_CACHE[name] = (stat.st_mtime_ns, stat.st_size, template)
    else:
        template = cached[2]
    return template.substitute({key: str(value) for key, value in context.items()})
