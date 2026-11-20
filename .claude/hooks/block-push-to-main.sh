#!/usr/bin/env bash
# Pre-tool hook intent: block any git push that targets main directly.
# This is defense in depth; GitHub branch protection remains authoritative.

set -euo pipefail

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    print("")
    raise SystemExit(0)

tool_input = data.get("tool_input", {})
if isinstance(tool_input, dict) and isinstance(tool_input.get("command"), str):
    print(tool_input["command"])
    raise SystemExit(0)

tool_name = data.get("toolName")
tool_args = data.get("toolArgs")
if tool_name == "bash" and isinstance(tool_args, str):
    try:
        parsed = json.loads(tool_args)
    except Exception:
        print(tool_args)
    else:
        print(parsed.get("command", "") if isinstance(parsed, dict) else "")
else:
    print("")
' 2>/dev/null || echo "")

# Parse shell command segments instead of searching raw text. This avoids
# treating arguments to printf/echo/etc. as executable Git commands.
COMMAND="$COMMAND" python3 - <<'PY'
import os
import re
import shlex
import subprocess
import sys

command = os.environ.get("COMMAND", "")
project_root = (
    os.environ.get("CODEX_PROJECT_DIR")
    or os.environ.get("CLAUDE_PROJECT_DIR")
    or os.getcwd()
)
separators = {";", "&&", "||", "|", "&", "(", ")"}
shell_keywords = {"then", "do", "else", "elif", "!"}
wrappers = {"command", "builtin", "exec", "nohup", "time"}
assignment = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
value_options = {
    "--receive-pack", "--exec", "--push-option", "-o",
    "--recurse-submodules", "--signed",
}
global_value_options = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

def segments(tokens):
    current = []
    for token in tokens:
        if token in separators or (token and set(token) <= {";", "&", "|"}):
            if current:
                yield current
                current = []
        else:
            current.append(token)
    if current:
        yield current

def command_tokens(segment):
    index = 0
    while index < len(segment):
        token = segment[index]
        if token in shell_keywords:
            index += 1
            continue
        if assignment.match(token):
            index += 1
            continue
        if token in wrappers:
            index += 1
            continue
        if token == "env":
            index += 1
            while index < len(segment) and (
                assignment.match(segment[index])
                or segment[index] in {"-i", "--ignore-environment", "-0"}
            ):
                index += 1
            continue
        break
    return segment[index:]

def expand_repo_path(raw_path):
    expanded = os.path.expanduser(os.path.expandvars(raw_path))
    # Do not pass unresolved shell variables or command substitutions to git.
    if "$" in expanded or "`" in expanded:
        return project_root
    if not os.path.isabs(expanded):
        expanded = os.path.join(project_root, expanded)
    return os.path.realpath(expanded)

def is_main_refspec(refspec):
    value = refspec.lstrip("+")
    destination = value.rsplit(":", 1)[1] if ":" in value else value
    destination = destination.lstrip("+")
    if destination in {"main", "refs/heads/main"}:
        return True
    # A wildcard destination can include refs/heads/main; fail closed.
    return "*" in destination or "?" in destination

try:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
    lexer.whitespace_split = True
    tokens = list(lexer)
except ValueError:
    # Malformed shell quoting: do not guess that a push is safe.
    if re.search(r"(?<![A-Za-z0-9_./-])git\s+push\b", command):
        print("Blocked: unable to safely parse a possible git push command.", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(0)

for segment in segments(tokens):
    parts = command_tokens(segment)
    if not parts or os.path.basename(parts[0]) != "git":
        continue

    index = 1
    repo_path = project_root
    while index < len(parts):
        token = parts[index]
        if token == "-C" and index + 1 < len(parts):
            repo_path = expand_repo_path(parts[index + 1])
            index += 2
        elif token in global_value_options and index + 1 < len(parts):
            if token in {"--git-dir", "--work-tree"}:
                # Relative Git directory/worktree options are resolved by Git;
                # branch checks below still use the selected project root.
                pass
            index += 2
        elif token.startswith(("--git-dir=", "--work-tree=", "--namespace=", "--exec-path=")):
            index += 1
        elif token.startswith("-"):
            index += 1
        else:
            break

    if index >= len(parts) or parts[index] != "push":
        continue

    args = parts[index + 1:]
    if "--all" in args or "--mirror" in args:
        print("Blocked: git push --all/--mirror can publish the protected 'main' branch.", file=sys.stderr)
        raise SystemExit(2)

    positional = []
    skip_value = False
    for arg in args:
        if skip_value:
            skip_value = False
            continue
        option_name = arg.split("=", 1)[0]
        if option_name in value_options and "=" not in arg:
            skip_value = True
        elif arg.startswith("-"):
            continue
        else:
            positional.append(arg)

    # First positional token is the remote; remaining tokens are refspecs.
    refspecs = positional[1:] if positional else []
    if any(is_main_refspec(refspec) for refspec in refspecs):
        print("Blocked: direct push to 'main' is not allowed.", file=sys.stderr)
        print("Create a feature branch and push that instead.", file=sys.stderr)
        raise SystemExit(2)

    if not refspecs:
        current = subprocess.run(
            ["git", "-C", repo_path, "branch", "--show-current"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
        upstream = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{push}"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
        if current == "main" or upstream in {"main", "refs/heads/main"} or upstream.endswith("/main"):
            print("Blocked: this implicit push would publish from or target the protected 'main' branch.", file=sys.stderr)
            print("Switch to a feature branch and push that instead.", file=sys.stderr)
            raise SystemExit(2)

raise SystemExit(0)
PY
