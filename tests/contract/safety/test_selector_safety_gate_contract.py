"""Source-level contract for routing every selector result through the Safety Gate."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SELECTOR_PATH = (
    ROOT / "src" / "soulmap" / "runtime" / "routing" / "framework_selector.py"
)


def _find_function(
    module: ast.Module, name: str
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    """Return a top-level function definition by name."""
    for node in module.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ):
            return node
    raise AssertionError(f"Expected function {name!r} in {SELECTOR_PATH}")


def _call_name(node: ast.expr) -> str | None:
    """Return the simple name of a called function or method."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _contains_call(node: ast.AST, name: str) -> bool:
    """Check whether a syntax subtree contains a call to the named function."""
    return any(
        isinstance(child, ast.Call) and _call_name(child.func) == name
        for child in ast.walk(node)
    )


def _has_gated_assignment_in_return_branch(
    selector: ast.FunctionDef | ast.AsyncFunctionDef, return_node: ast.Return
) -> bool:
    """Require the explicit gated result assignment in the same branch as its return."""
    parents = {
        child: parent
        for parent in ast.walk(selector)
        for child in ast.iter_child_nodes(parent)
    }
    current: ast.AST = return_node
    while current in parents:
        parent = parents[current]
        if isinstance(parent, ast.If):
            for block in (parent.body, parent.orelse):
                contains_return = any(
                    any(descendant is return_node for descendant in ast.walk(statement))
                    for statement in block
                )
                if contains_return:
                    return any(
                        isinstance(statement, ast.Assign)
                        and any(
                            isinstance(target, ast.Name) and target.id == "result"
                            for target in statement.targets
                        )
                        and _contains_call(statement, "_apply_safety_gate")
                        and statement.lineno < return_node.lineno
                        for statement in block
                    )
        current = parent
    return False


def test_every_selector_return_path_delegates_to_the_safety_gate() -> None:
    """Fail if a selector return path bypasses the shared Safety Gate helpers."""
    module = ast.parse(SELECTOR_PATH.read_text(encoding="utf-8"))
    selector = _find_function(module, "select_framework_async")
    finish = _find_function(module, "_finish")
    gate_wrapper = _find_function(module, "_apply_safety_gate")

    assert _contains_call(finish, "_apply_safety_gate")
    assert _contains_call(gate_wrapper, "apply_safety_gate")

    returns = [node for node in ast.walk(selector) if isinstance(node, ast.Return)]
    assert returns, "select_framework_async must expose at least one return path"

    for return_node in returns:
        value = return_node.value
        if isinstance(value, ast.Call) and _call_name(value.func) == "_finish":
            continue

        if (
            isinstance(value, ast.Call)
            and _call_name(value.func) == "_maybe_attach_debug"
            and value.args
            and isinstance(value.args[0], ast.Name)
            and value.args[0].id == "result"
            and _has_gated_assignment_in_return_branch(selector, return_node)
        ):
            continue

        raise AssertionError(
            "select_framework_async has a return path that does not delegate "
            f"to the Safety Gate (line {return_node.lineno})"
        )
