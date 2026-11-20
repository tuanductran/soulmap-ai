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
separators = {";", "&&", "||", "|", "&", "(", ")", "{", "}"}
shell_keywords = {
    "if", "then", "do", "else", "elif", "while", "until",
    "for", "case", "select", "!",
}
wrappers = {"command", "builtin", "exec", "nohup", "time"}
assignment = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
value_options = {
    "--receive-pack", "--exec", "--push-option", "-o",
    "--recurse-submodules",
}
global_value_options = {
    "-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path",
}


def strip_shell_comments(source):
    """Remove shell comments but preserve their terminating newlines."""
    output = []
    quote = None
    escaped = False
    at_word_start = True
    index = 0
    while index < len(source):
        char = source[index]
        if escaped:
            output.append(char)
            escaped = False
            at_word_start = False
            index += 1
            continue
        if char == "\\" and quote != "'":
            output.append(char)
            escaped = True
            index += 1
            continue
        if quote:
            output.append(char)
            if char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            output.append(char)
            at_word_start = False
            index += 1
            continue
        if char == "#" and at_word_start:
            while index < len(source) and source[index] != "\n":
                index += 1
            if index < len(source):
                output.append("\n")
                index += 1
            at_word_start = True
            continue
        output.append(char)
        at_word_start = char.isspace() or char in ";&|(){}"
        index += 1
    return "".join(output)


def split_segments(tokens):
    current = []
    for token in tokens:
        if token in separators:
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
        if token in shell_keywords or assignment.match(token):
            index += 1
            continue
        if token in wrappers:
            index += 1
            continue
        if token == "sudo":
            index += 1
            while index < len(segment) and segment[index].startswith("-"):
                if segment[index] in {
                    "-u", "--user", "-g", "--group",
                    "-h", "--host", "-p", "--prompt",
                }:
                    index += 2
                else:
                    index += 1
            continue
        if token == "env":
            index += 1
            while index < len(segment):
                item = segment[index]
                if assignment.match(item) or item in {"-i", "--ignore-environment", "-0"}:
                    index += 1
                elif item in {"-u", "--unset", "-C", "--chdir"}:
                    index += 2
                else:
                    break
            continue
        break
    return segment[index:]


def expand_repo_path(raw_path):
    expanded = os.path.expanduser(os.path.expandvars(raw_path))
    if "$" in expanded or chr(96) in expanded:
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
    return "*" in destination or "?" in destination


def parse_push_arguments(args):
    """Return positional arguments and dangerous push modes, respecting option values."""
    positional = []
    dangerous_modes = set()
    index = 0
    options_ended = False
    while index < len(args):
        arg = args[index]
        if options_ended:
            positional.append(arg)
            index += 1
            continue
        if arg == "--":
            options_ended = True
            index += 1
            continue
        if arg in {"--all", "--branches", "--mirror", "--prune"}:
            dangerous_modes.add(arg)
            index += 1
            continue
        option_name = arg.split("=", 1)[0]
        if option_name in value_options:
            index += 2 if "=" not in arg else 1
            continue
        if arg.startswith("-"):
            index += 1
            continue
        positional.append(arg)
        index += 1
    return positional, dangerous_modes


def tokenize_shell(source):
    normalized = source.replace("\\\n", " ")
    normalized = strip_shell_comments(normalized).replace("\n", " ; ")
    lexer = shlex.shlex(normalized, posix=True, punctuation_chars=";&|(){}")
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


try:
    tokens = tokenize_shell(command)
except ValueError:
    if re.search(r"(?<![A-Za-z0-9_./-])git\s+push\b", command):
        print("Blocked: unable to safely parse a possible git push command.", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(0)

pending_segments = list(split_segments(tokens))
while pending_segments:
    segment = pending_segments.pop(0)
    parts = command_tokens(segment)
    if not parts:
        continue

    executable = os.path.basename(parts[0])
    if executable in {"bash", "sh", "dash", "zsh", "ksh"}:
        for option_index, option in enumerate(parts[1:], start=1):
            if option == "-c" or (
                option.startswith("-") and not option.startswith("--") and "c" in option[1:]
            ):
                if option_index + 1 < len(parts):
                    nested_command = parts[option_index + 1]
                    try:
                        pending_segments[0:0] = list(
                            split_segments(tokenize_shell(nested_command))
                        )
                    except ValueError:
                        if re.search(r"(?<![A-Za-z0-9_./-])git\s+push\b", nested_command):
                            print("Blocked: unable to safely parse a nested shell command.", file=sys.stderr)
                            raise SystemExit(2)
                break
        continue

    if executable == "eval":
        nested_command = " ".join(parts[1:])
        try:
            pending_segments[0:0] = list(
                split_segments(tokenize_shell(nested_command))
            )
        except ValueError:
            if re.search(r"(?<![A-Za-z0-9_./-])git\s+push\b", nested_command):
                print("Blocked: unable to safely parse an eval command.", file=sys.stderr)
                raise SystemExit(2)
        continue

    if executable != "git":
        continue

    index = 1
    repo_path = project_root
    repo_context_unknown = False
    while index < len(parts):
        token = parts[index]
        if token == "-C" and index + 1 < len(parts):
            repo_path = expand_repo_path(parts[index + 1])
            index += 2
        elif token in global_value_options and index + 1 < len(parts):
            if token in {"--git-dir", "--work-tree"}:
                repo_context_unknown = True
            index += 2
        elif token.startswith(("--git-dir=", "--work-tree=")):
            repo_context_unknown = True
            index += 1
        elif token.startswith(("--namespace=", "--exec-path=")):
            index += 1
        elif token.startswith("-"):
            index += 1
        else:
            break

    if index >= len(parts) or parts[index] != "push":
        continue

    positional, dangerous_modes = parse_push_arguments(parts[index + 1:])
    if dangerous_modes:
        modes = ", ".join(sorted(dangerous_modes))
        print(
            f"Blocked: push mode {modes} can publish or delete the protected 'main' branch.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    refspecs = positional[1:] if positional else []
    if any(is_main_refspec(refspec) for refspec in refspecs):
        print("Blocked: direct push to 'main' is not allowed.", file=sys.stderr)
        print("Create a feature branch and push that instead.", file=sys.stderr)
        raise SystemExit(2)

    if not refspecs:
        if repo_context_unknown:
            print(
                "Blocked: cannot verify the target repository for an implicit push.",
                file=sys.stderr,
            )
            raise SystemExit(2)

        def git_output(*git_args):
            return subprocess.run(
                ["git", "-C", repo_path, *git_args],
                capture_output=True, text=True, check=False,
            ).stdout.strip()

        current = git_output("branch", "--show-current")
        upstream = git_output(
            "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{push}"
        )
        remote = positional[0] if positional else (
            git_output("config", "--get", f"branch.{current}.pushRemote")
            or git_output("config", "--get", "remote.pushDefault")
            or git_output("config", "--get", f"branch.{current}.remote")
        )
        remote_mirror = (
            git_output("config", "--bool", f"remote.{remote}.mirror")
            if remote else ""
        )
        configured_push = (
            subprocess.run(
                ["git", "-C", repo_path, "config", "--get-all", f"remote.{remote}.push"],
                capture_output=True, text=True, check=False,
            ).stdout.splitlines()
            if remote else []
        )
        push_default = git_output("config", "--get", "push.default")
        local_main = subprocess.run(
            ["git", "-C", repo_path, "show-ref", "--verify", "--quiet", "refs/heads/main"],
            capture_output=True, check=False,
        ).returncode == 0
        if (
            current == "main"
            or upstream in {"main", "refs/heads/main"}
            or upstream.endswith("/main")
            or remote_mirror == "true"
            or any(is_main_refspec(spec) for spec in configured_push)
            or (push_default in {"matching", "mirror"} and local_main)
        ):
            print(
                "Blocked: this implicit push would publish from or target the protected 'main' branch.",
                file=sys.stderr,
            )
            print("Switch to a feature branch and push that instead.", file=sys.stderr)
            raise SystemExit(2)

raise SystemExit(0)
PY
