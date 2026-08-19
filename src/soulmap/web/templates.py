"""File-based HTML template rendering for the public SoulMap website."""

from __future__ import annotations

from pathlib import Path
from string import Template

TEMPLATE_ROOT = Path(__file__).with_name("templates")
_TEMPLATE_CACHE: dict[str, Template] = {}


def render_template(name: str, **context: object) -> str:
    """Render a checked-in HTML template with strict placeholder substitution."""
    template = _TEMPLATE_CACHE.get(name)
    if template is None:
        root = TEMPLATE_ROOT.resolve()
        path = (root / name).resolve()
        if root not in path.parents or not path.is_file():
            raise FileNotFoundError(f"template not found: {name}")
        template = Template(path.read_text(encoding="utf-8"))
        _TEMPLATE_CACHE[name] = template
    return template.substitute({key: str(value) for key, value in context.items()})
