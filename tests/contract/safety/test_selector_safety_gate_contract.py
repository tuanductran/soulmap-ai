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


def _is_gated_result_assignment(statement: ast.stmt) -> bool:
    """Accept only a direct result binding whose entire RHS is the local gate call."""
    return (
        isinstance(statement, ast.Assign)
        and len(statement.targets) == 1
        and isinstance(statement.targets[0], ast.Name)
        and statement.targets[0].id == "result"
        and _is_direct_call(statement.value, "_apply_safety_gate")
    )


def _is_direct_call_assignment(
    statement: ast.stmt, target_name: str, call_name: str
) -> bool:
    """Require a single-name assignment from one direct local function call."""
    return (
        isinstance(statement, ast.Assign)
        and len(statement.targets) == 1
        and isinstance(statement.targets[0], ast.Name)
        and statement.targets[0].id == target_name
        and _is_direct_call(statement.value, call_name)
    )


def _is_name_assignment(statement: ast.stmt, target_name: str, value_name: str) -> bool:
    """Require a simple local-name copy assignment."""
    return (
        isinstance(statement, ast.Assign)
        and len(statement.targets) == 1
        and isinstance(statement.targets[0], ast.Name)
        and statement.targets[0].id == target_name
        and isinstance(statement.value, ast.Name)
        and statement.value.id == value_name
    )


def _has_single_local_binding(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    name: str,
    allowed_target: ast.Name,
) -> bool:
    """Reject rebinding a gate-derived local, including match captures."""
    writes = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Name)
        and node.id == name
        and isinstance(node.ctx, ast.Store)
    ]
    pattern_writes = [
        pattern
        for node in ast.walk(function)
        if isinstance(node, ast.match_case)
        for pattern in ast.walk(node.pattern)
        if isinstance(pattern, (ast.MatchAs, ast.MatchStar, ast.MatchMapping))
        and (
            (isinstance(pattern, ast.MatchAs) and pattern.name == name)
            or (isinstance(pattern, ast.MatchStar) and pattern.name == name)
            or (isinstance(pattern, ast.MatchMapping) and pattern.rest == name)
        )
    ]
    return len(writes) == 1 and writes[0] is allowed_target and not pattern_writes


def _request_inputs_are_not_rebound(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    names: tuple[str, ...],
) -> bool:
    """Reject reassignment or pattern capture of request inputs before gating."""
    for name in names:
        if any(
            isinstance(node, ast.Name)
            and node.id == name
            and isinstance(node.ctx, ast.Store)
            for node in ast.walk(function)
        ):
            return False
        if any(
            (isinstance(pattern, ast.MatchAs) and pattern.name == name)
            or (isinstance(pattern, ast.MatchStar) and pattern.name == name)
            or (isinstance(pattern, ast.MatchMapping) and pattern.rest == name)
            for case in ast.walk(function)
            if isinstance(case, ast.match_case)
            for pattern in ast.walk(case.pattern)
        ):
            return False
    return True


def _gate_call_forwards_inputs(
    statement: ast.stmt, call_name: str, expected_names: tuple[str, ...]
) -> bool:
    """Require the gate call to receive the current request inputs positionally."""
    if not isinstance(statement, ast.Assign) or not isinstance(
        statement.value, ast.Call
    ):
        return False
    call = statement.value
    return (
        _is_direct_call(call, call_name)
        and len(call.args) >= len(expected_names)
        and all(
            isinstance(argument, ast.Name) and argument.id == expected
            for argument, expected in zip(call.args, expected_names, strict=False)
        )
    )


def _root_name(node: ast.expr) -> str | None:
    """Return the root local name for a nested mapping or attribute expression."""
    while isinstance(node, (ast.Subscript, ast.Attribute)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _has_only_allowed_mapping_writes(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    name: str,
    allowed_keys: set[str],
) -> bool:
    """Reject writes that could replace gated policy fields after the gate."""
    mutators = {
        "append",
        "clear",
        "discard",
        "extend",
        "insert",
        "pop",
        "popitem",
        "remove",
        "reverse",
        "setdefault",
        "sort",
        "update",
        "__setitem__",
    }
    for node in ast.walk(function):
        targets: list[ast.expr] = []
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            raw_targets = (
                node.targets if isinstance(node, ast.Assign) else [node.target]
            )
            targets.extend(raw_targets)
        elif isinstance(node, ast.Delete):
            targets.extend(node.targets)
        for target in targets:
            if isinstance(target, ast.Subscript) and _root_name(target) == name:
                key = target.slice
                if not isinstance(key, ast.Constant) or key.value not in allowed_keys:
                    return False
            elif isinstance(target, ast.Attribute) and _root_name(target) == name:
                return False
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and _root_name(node.func.value) == name
            and node.func.attr in mutators
        ):
            if node.func.attr == "update":
                if node.args or any(
                    keyword.arg is None or keyword.arg not in allowed_keys
                    for keyword in node.keywords
                ):
                    return False
            else:
                return False
    return True


def _finish_returns_gated_result(
    finish: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    """Require every _finish return to use its dominating, unrebound gate result."""
    gates = [
        node
        for node in finish.body
        if _is_direct_call_assignment(node, "result", "_apply_safety_gate")
        and _gate_call_forwards_inputs(
            node, "_apply_safety_gate", ("message", "history", "memory", "selection")
        )
        and _request_inputs_are_not_rebound(
            finish, ("message", "history", "memory", "selection")
        )
    ]
    returns = [node for node in ast.walk(finish) if isinstance(node, ast.Return)]
    if len(gates) != 1 or not returns:
        return False
    gate = gates[0]
    if not isinstance(gate, ast.Assign) or not gate.targets:
        return False
    target = gate.targets[0]
    if not isinstance(target, ast.Name):
        return False
    if not _has_single_local_binding(finish, "result", target):
        return False
    if not _has_only_allowed_mapping_writes(finish, "result", {"template"}):
        return False
    return all(
        node.lineno > gate.lineno
        and isinstance(node.value, ast.Call)
        and _is_direct_call(node.value, "_maybe_attach_debug")
        and bool(node.value.args)
        and isinstance(node.value.args[0], ast.Name)
        and node.value.args[0].id == "result"
        for node in returns
    )


def _gate_wrapper_returns_gated_selection(
    gate_wrapper: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    """Require each gate-wrapper return to use its dominating gated selection."""
    gates = [
        node
        for node in gate_wrapper.body
        if _is_direct_call_assignment(node, "result", "apply_safety_gate")
        and _gate_call_forwards_inputs(
            node, "apply_safety_gate", ("message", "history", "memory", "selection")
        )
        and _request_inputs_are_not_rebound(
            gate_wrapper, ("message", "history", "memory", "selection")
        )
    ]
    selected = [
        node
        for node in gate_wrapper.body
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "gated_selection"
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "get"
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "result"
            and len(node.value.args) >= 2
            and isinstance(node.value.args[0], ast.Constant)
            and node.value.args[0].value == "selection"
            and isinstance(node.value.args[1], ast.Name)
            and node.value.args[1].id == "selection"
        )
    ]
    copied = [
        node
        for node in gate_wrapper.body
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "out"
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "dict"
            and bool(node.value.args)
            and isinstance(node.value.args[0], ast.Call)
            and isinstance(node.value.args[0].func, ast.Name)
            and node.value.args[0].func.id == "cast"
            and len(node.value.args[0].args) >= 2
            and isinstance(node.value.args[0].args[1], ast.Name)
            and node.value.args[0].args[1].id == "gated_selection"
        )
    ]
    returns = [node for node in ast.walk(gate_wrapper) if isinstance(node, ast.Return)]
    if len(gates) != 1 or len(selected) != 1 or len(copied) != 1 or not returns:
        return False

    gate, selection, output = gates[0], selected[0], copied[0]
    if not isinstance(gate, ast.Assign) or not gate.targets:
        return False
    if not isinstance(selection, ast.Assign) or not selection.targets:
        return False
    if not isinstance(output, ast.Assign) or not output.targets:
        return False
    gate_target = gate.targets[0]
    selection_target = selection.targets[0]
    output_target = output.targets[0]
    if not (
        isinstance(gate_target, ast.Name)
        and isinstance(selection_target, ast.Name)
        and isinstance(output_target, ast.Name)
    ):
        return False
    if not (
        gate.lineno < selection.lineno < output.lineno
        and _has_single_local_binding(gate_wrapper, "result", gate_target)
        and _has_single_local_binding(gate_wrapper, "gated_selection", selection_target)
        and _has_single_local_binding(gate_wrapper, "out", output_target)
        and _has_only_allowed_mapping_writes(gate_wrapper, "result", set())
        and _has_only_allowed_mapping_writes(gate_wrapper, "gated_selection", set())
        and _has_only_allowed_mapping_writes(
            gate_wrapper, "out", {"safety_status", "safety_reason", "safety_flags"}
        )
    ):
        return False
    return all(
        node.lineno > output.lineno
        and isinstance(node.value, ast.Name)
        and node.value.id == "out"
        for node in returns
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

    assert _finish_returns_gated_result(finish)
    assert _gate_wrapper_returns_gated_selection(gate_wrapper)

    returns = [node for node in ast.walk(selector) if isinstance(node, ast.Return)]
    assert returns, "select_framework_async must expose at least one return path"

    for return_node in returns:
        value = return_node.value
        if isinstance(value, ast.Call):
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


def test_finish_rejects_an_early_ungated_return() -> None:
    module = ast.parse("""
def _finish():
    if early:
        return selection
    result = _apply_safety_gate(selection)
    return _maybe_attach_debug(result, debug_events)
""")
    finish = _find_function(module, "_finish")
    assert not _finish_returns_gated_result(finish)


def test_gate_wrapper_rejects_an_early_ungated_return() -> None:
    module = ast.parse("""
def _apply_safety_gate(selection):
    if early:
        return selection
    result = apply_safety_gate(selection)
    gated_selection = result.get("selection", selection)
    out = dict(cast(dict, gated_selection))
    return out
""")
    gate_wrapper = _find_function(module, "_apply_safety_gate")
    assert not _gate_wrapper_returns_gated_selection(gate_wrapper)


def test_finish_rejects_return_of_rebound_result_before_gate() -> None:
    module = ast.parse("""
def _finish():
    result = selection
    if early:
        return _maybe_attach_debug(result, debug_events)
    result = _apply_safety_gate(selection)
    return _maybe_attach_debug(result, debug_events)
""")
    finish = _find_function(module, "_finish")
    assert not _finish_returns_gated_result(finish)


def test_gate_wrapper_rejects_return_of_rebound_output_before_gate() -> None:
    module = ast.parse("""
def _apply_safety_gate(selection):
    out = selection
    if early:
        return out
    result = apply_safety_gate(selection)
    gated_selection = result.get("selection", selection)
    out = dict(cast(dict, gated_selection))
    return out
""")
    gate_wrapper = _find_function(module, "_apply_safety_gate")
    assert not _gate_wrapper_returns_gated_selection(gate_wrapper)


def test_finish_rejects_gate_call_with_stale_request_inputs() -> None:
    module = ast.parse("""
def _finish(message, history, memory, selection):
    result = _apply_safety_gate("benign", history, memory, selection)
    return _maybe_attach_debug(result, debug_events)
""")
    finish = _find_function(module, "_finish")
    assert not _finish_returns_gated_result(finish)


def test_gate_wrapper_rejects_gate_call_with_stale_request_inputs() -> None:
    module = ast.parse("""
def _apply_safety_gate(message, history, memory, selection):
    result = apply_safety_gate("benign", history, memory, selection)
    gated_selection = result.get("selection", selection)
    out = dict(cast(dict, gated_selection))
    return out
""")
    gate_wrapper = _find_function(module, "_apply_safety_gate")
    assert not _gate_wrapper_returns_gated_selection(gate_wrapper)


def test_finish_rejects_post_gate_policy_mutation() -> None:
    module = ast.parse("""
def _finish(message, history, memory, selection):
    result = _apply_safety_gate(message, history, memory, selection)
    result["primary_framework"] = "MIRROR"
    return _maybe_attach_debug(result, debug_events)
""")
    finish = _find_function(module, "_finish")
    assert not _finish_returns_gated_result(finish)


def test_gate_wrapper_rejects_post_gate_policy_mutation() -> None:
    module = ast.parse("""
def _apply_safety_gate(message, history, memory, selection):
    result = apply_safety_gate(message, history, memory, selection)
    gated_selection = result.get("selection", selection)
    out = dict(cast(dict, gated_selection))
    out["primary_framework"] = "MIRROR"
    return out
""")
    gate_wrapper = _find_function(module, "_apply_safety_gate")
    assert not _gate_wrapper_returns_gated_selection(gate_wrapper)



def test_finish_rejects_reassigned_request_message_before_gate() -> None:
    module = ast.parse("""
def _finish(message, history, memory, selection):
    message = "benign"
    result = _apply_safety_gate(message, history, memory, selection)
    return _maybe_attach_debug(result, debug_events)
""")
    finish = _find_function(module, "_finish")
    assert not _finish_returns_gated_result(finish)


def test_gate_wrapper_rejects_reassigned_request_message_before_gate() -> None:
    module = ast.parse("""
def _apply_safety_gate(message, history, memory, selection):
    message = "benign"
    result = apply_safety_gate(message, history, memory, selection)
    gated_selection = result.get("selection", selection)
    out = dict(cast(dict, gated_selection))
    return out
""")
    gate_wrapper = _find_function(module, "_apply_safety_gate")
    assert not _gate_wrapper_returns_gated_selection(gate_wrapper)


def test_finish_rejects_match_capture_rebinding() -> None:
    module = ast.parse("""
def _finish(message, history, memory, selection):
    result = _apply_safety_gate(message, history, memory, selection)
    match raw:
        case {"selection": result}:
            pass
    return _maybe_attach_debug(result, debug_events)
""")
    finish = _find_function(module, "_finish")
    assert not _finish_returns_gated_result(finish)


def test_gate_wrapper_rejects_match_capture_rebinding() -> None:
    module = ast.parse("""
def _apply_safety_gate(message, history, memory, selection):
    result = apply_safety_gate(message, history, memory, selection)
    gated_selection = result.get("selection", selection)
    out = dict(cast(dict, gated_selection))
    match raw:
        case {"selection": out}:
            pass
    return out
""")
    gate_wrapper = _find_function(module, "_apply_safety_gate")
    assert not _gate_wrapper_returns_gated_selection(gate_wrapper)
