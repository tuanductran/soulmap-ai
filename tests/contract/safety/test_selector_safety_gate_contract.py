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


def _is_gated_result_assignment(statement: ast.stmt) -> bool:
    """Accept only a direct result binding whose complete RHS is the gate call."""
    return (
        isinstance(statement, ast.Assign)
        and len(statement.targets) == 1
        and isinstance(statement.targets[0], ast.Name)
        and statement.targets[0].id == "result"
        and isinstance(statement.value, ast.Call)
        and _call_name(statement.value.func) == "_apply_safety_gate"
    )


def _is_allowed_scope_metadata_write(statement: ast.stmt) -> bool:
    """Allow the selector's non-policy scope metadata to be attached after gating."""
    if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
        return False
    target = statement.targets[0]
    return (
        isinstance(target, ast.Subscript)
        and isinstance(target.value, ast.Name)
        and target.value.id == "result"
        and isinstance(target.slice, ast.Constant)
        and target.slice.value == "scope"
    )


def _has_gated_assignment_in_return_branch(
    selector: ast.FunctionDef | ast.AsyncFunctionDef, return_node: ast.Return
) -> bool:
    """Require the result passed to debug attachment to be gated immediately before use."""
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
                if current not in block:
                    continue
                if current is not return_node or return_node not in block:
                    return False
                index = block.index(return_node)
                if index == 0:
                    return False
                previous = block[index - 1]
                if _is_allowed_scope_metadata_write(previous):
                    return index >= 2 and _is_gated_result_assignment(block[index - 2])
                return _is_gated_result_assignment(previous)
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


def _return_for(
    source: str,
) -> tuple[ast.FunctionDef | ast.AsyncFunctionDef, ast.Return]:
    module = ast.parse(source)
    selector = _find_function(module, "selector")
    return selector, next(
        node for node in ast.walk(selector) if isinstance(node, ast.Return)
    )


def test_nested_result_overwrite_must_also_pass_through_the_safety_gate() -> None:
    """A nested branch cannot replace a gated result with an ungated value."""
    selector, return_node = _return_for(
        """
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        if nested_condition:
            result = value
        return _maybe_attach_debug(result)
"""
    )
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_destructuring_result_rebind_must_pass_through_the_safety_gate() -> None:
    """Tuple/list unpacking cannot replace result with an ungated value."""
    selector, return_node = _return_for(
        """
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        result, metadata = raw_pair
        return _maybe_attach_debug(result)
"""
    )
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_subscript_result_mutation_is_not_a_variable_rebind() -> None:
    """The existing scope metadata write is allowed after gating."""
    selector, return_node = _return_for(
        """
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        result["scope"] = scope
        return _maybe_attach_debug(result)
"""
    )
    assert _has_gated_assignment_in_return_branch(selector, return_node)


def test_nested_gated_result_assignment_is_not_assumed_to_cover_outer_return() -> None:
    """A gate call in a nested branch cannot prove the outer return is gated."""
    selector, return_node = _return_for(
        """
async def selector():
    if condition:
        if nested_condition:
            result = _apply_safety_gate(value)
        return _maybe_attach_debug(result)
"""
    )
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_conditional_rhs_must_gate_every_result_value() -> None:
    """A conditional expression with one raw arm is not a gated assignment."""
    selector, return_node = _return_for(
        """
async def selector():
    if condition:
        result = raw if unsafe else _apply_safety_gate(value)
        return _maybe_attach_debug(result)
"""
    )
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_walrus_rebinding_before_return_is_rejected() -> None:
    """A walrus assignment cannot replace the previously gated result."""
    selector, return_node = _return_for(
        """
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        if (result := raw):
            pass
        return _maybe_attach_debug(result)
"""
    )
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_post_gate_policy_field_mutation_is_rejected() -> None:
    """Safety-relevant result fields cannot be overwritten after gating."""
    selector, return_node = _return_for(
        """
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        result["primary_framework"] = raw["primary_framework"]
        return _maybe_attach_debug(result)
"""
    )
    assert not _has_gated_assignment_in_return_branch(selector, return_node)
