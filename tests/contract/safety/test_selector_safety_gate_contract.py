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


def _assigns_result(statement: ast.stmt) -> bool:
    """Return whether a direct statement reassigns the selector result."""
    if isinstance(statement, ast.Assign):
        targets = statement.targets
    elif isinstance(statement, (ast.AnnAssign, ast.AugAssign)):
        targets = [statement.target]
    else:
        return False
    return any(
        isinstance(name, ast.Name) and name.id == "result"
        for target in targets
        for name in ast.walk(target)
    )


def _has_gated_assignment_in_return_branch(
    selector: ast.FunctionDef | ast.AsyncFunctionDef, return_node: ast.Return
) -> bool:
    """Require the last direct result assignment in the return branch to be gated."""
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
                if return_node not in block:
                    continue
                preceding = block[: block.index(return_node)]
                assignments = [
                    node
                    for statement in preceding
                    for node in ast.walk(statement)
                    if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign))
                    and _assigns_result(node)
                ]
                # Every write on the path must be gated. Checking only the last
                # direct statement misses nested branches that overwrite result.
                return bool(assignments) and all(
                    _contains_call(assignment, "_apply_safety_gate")
                    for assignment in assignments
                )
        current = parent
    return False


def test_every_selector_return_path_delegates_to_the_safety_gate() -> None:
    """Fail if a selector return path does not delegate to the shared Safety Gate."""
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



def test_nested_result_overwrite_must_also_pass_through_the_safety_gate() -> None:
    """A nested branch cannot replace a gated result with an ungated value."""
    module = ast.parse(
        """
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        if nested_condition:
            result = value
        return _maybe_attach_debug(result)
"""
    )
    selector = _find_function(module, "selector")
    return_node = next(
        node for node in ast.walk(selector) if isinstance(node, ast.Return)
    )

    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_nested_gated_result_assignment_remains_valid() -> None:
    """Nested result writes are accepted when each write applies the gate."""
    module = ast.parse(
        """
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        if nested_condition:
            result = _apply_safety_gate(other_value)
        return _maybe_attach_debug(result)
"""
    )
    selector = _find_function(module, "selector")
    return_node = next(
        node for node in ast.walk(selector) if isinstance(node, ast.Return)
    )

    assert _has_gated_assignment_in_return_branch(selector, return_node)
