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


def _is_direct_call(node: ast.expr, name: str) -> bool:
    """Require a direct local function call, not an attribute with the same name."""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == name
    )


def _contains_direct_call(node: ast.AST, name: str) -> bool:
    """Check whether a syntax subtree contains a direct call to the named function."""
    return any(
        _is_direct_call(child, name)
        for child in ast.walk(node)
        if isinstance(child, ast.expr)
    )


def _is_gated_result_assignment(statement: ast.stmt) -> bool:
    """Accept only a direct result binding whose entire RHS is the local gate call."""
    return (
        isinstance(statement, ast.Assign)
        and len(statement.targets) == 1
        and isinstance(statement.targets[0], ast.Name)
        and statement.targets[0].id == "result"
        and _is_direct_call(statement.value, "_apply_safety_gate")
    )


def _is_allowed_scope_metadata_write(statement: ast.stmt) -> bool:
    """Allow only the exact, side-effect-free scope metadata assignment."""
    if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
        return False
    target = statement.targets[0]
    return (
        isinstance(target, ast.Subscript)
        and isinstance(target.value, ast.Name)
        and target.value.id == "result"
        and isinstance(target.slice, ast.Constant)
        and target.slice.value == "scope"
        and isinstance(statement.value, ast.Name)
        and statement.value.id == "scope"
    )


def _has_gated_assignment_in_return_branch(
    selector: ast.FunctionDef | ast.AsyncFunctionDef, return_node: ast.Return
) -> bool:
    """Tie each debug return to its immediately preceding gate assignment."""
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

    assert _contains_direct_call(finish, "_apply_safety_gate")
    assert _contains_direct_call(gate_wrapper, "apply_safety_gate")

    returns = [node for node in ast.walk(selector) if isinstance(node, ast.Return)]
    assert returns, "select_framework_async must expose at least one return path"

    for return_node in returns:
        value = return_node.value
        if _is_direct_call(value, "_finish"):
            continue
        if (
            _is_direct_call(value, "_maybe_attach_debug")
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


def test_nested_result_overwrite_is_not_accepted() -> None:
    selector, return_node = _return_for("""
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        if nested_condition:
            result = value
        return _maybe_attach_debug(result)
""")
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_destructuring_result_rebind_is_not_accepted() -> None:
    selector, return_node = _return_for("""
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        result, metadata = raw_pair
        return _maybe_attach_debug(result)
""")
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_subscript_scope_metadata_write_is_allowed() -> None:
    selector, return_node = _return_for("""
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        result["scope"] = scope
        return _maybe_attach_debug(result)
""")
    assert _has_gated_assignment_in_return_branch(selector, return_node)


def test_nested_gate_assignment_does_not_cover_outer_return() -> None:
    selector, return_node = _return_for("""
async def selector():
    if condition:
        if nested_condition:
            result = _apply_safety_gate(value)
        return _maybe_attach_debug(result)
""")
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_conditional_rhs_with_ungated_arm_is_not_accepted() -> None:
    selector, return_node = _return_for("""
async def selector():
    if condition:
        result = raw if unsafe else _apply_safety_gate(value)
        return _maybe_attach_debug(result)
""")
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_walrus_rebinding_before_return_is_not_accepted() -> None:
    selector, return_node = _return_for("""
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        if (result := raw):
            pass
        return _maybe_attach_debug(result)
""")
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_post_gate_policy_field_mutation_is_not_accepted() -> None:
    selector, return_node = _return_for("""
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        result["primary_framework"] = raw["primary_framework"]
        return _maybe_attach_debug(result)
""")
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_scope_write_with_side_effects_is_not_allowed() -> None:
    selector, return_node = _return_for("""
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        result["scope"] = (result.update(primary_framework=raw), scope)[1]
        return _maybe_attach_debug(result)
""")
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_scope_write_with_walrus_is_not_allowed() -> None:
    selector, return_node = _return_for("""
async def selector():
    if condition:
        result = _apply_safety_gate(value)
        result["scope"] = (result := raw)
        return _maybe_attach_debug(result)
""")
    assert not _has_gated_assignment_in_return_branch(selector, return_node)


def test_attribute_named_safety_gate_is_not_a_local_gate_call() -> None:
    selector, return_node = _return_for("""
async def selector():
    if condition:
        result = helper._apply_safety_gate(value)
        return _maybe_attach_debug(result)
""")
    assert not _has_gated_assignment_in_return_branch(selector, return_node)
