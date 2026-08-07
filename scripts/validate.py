#!/usr/bin/env python3
"""Validate the marketplace manifest, the plugin manifests, and every agent and skill.

This repository ships no application code, so this script is what stands in for a
test suite. It is dependency-free on purpose: it parses the small subset of YAML
that Copilot frontmatter actually uses, so it runs on a bare Python 3 with no pip
install, both locally and in CI.

Usage:
    python3 scripts/validate.py

Exits 0 if everything checks out, 1 otherwise. Errors fail the build; warnings do not.
"""

from __future__ import annotations

import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKETPLACE_MANIFEST = os.path.join(".github", "plugin", "marketplace.json")

# Copilot's built-in tool vocabulary. Names outside this set are silently ignored
# at runtime, so a typo costs a capability with no error — which is exactly why
# this check exists. MCP tools are referenced as "server-name/tool-name".
VALID_TOOLS = {
    "bash", "powershell",
    "list_bash", "list_powershell",
    "read_bash", "read_powershell",
    "stop_bash", "stop_powershell",
    "write_bash", "write_powershell",
    "apply_patch", "create", "edit", "view",
    "list_agents", "read_agent", "task", "write_agent",
    "ask_user", "glob", "grep", "rg", "skill", "web_fetch",
    "*",
}

# Tool names that look plausible but do not exist. Flagged in prose as well as
# frontmatter, because an agent or skill body that tells the model to use a
# non-existent tool is just as broken as declaring one.
KNOWN_BAD_TOOLS = {"search", "read_file", "write_file", "list_files", "codebase"}

MAX_NAME = 64
MAX_DESCRIPTION = 1024
NAME_PATTERN = re.compile(r"^[a-zA-Z0-9-]+$")

errors: list[str] = []
warnings: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def parse_frontmatter(path: str) -> tuple[dict, str]:
    """Parse the YAML frontmatter subset used by agent and skill files.

    Supports `key: value`, block lists (`- item` on following lines), and inline
    JSON-ish lists (`key: [a, b]`). Returns (frontmatter, body).
    """
    with open(path, encoding="utf-8") as handle:
        text = handle.read()

    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    raw = text[3:end].strip("\n")
    body = text[end + 4:]

    data: dict = {}
    current_key: str | None = None

    for line in raw.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        stripped = line.strip()

        if stripped.startswith("- ") and current_key:
            # `key:` with no inline value parses to None; a following block list
            # must replace that None, not be dropped by setdefault.
            if not isinstance(data.get(current_key), list):
                data[current_key] = []
            data[current_key].append(stripped[2:].strip().strip("\"'"))
            continue

        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", stripped)
        if not match:
            continue

        key, value = match.group(1), match.group(2).strip()
        current_key = key

        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip("\"'") for v in value[1:-1].split(",")]
            data[key] = [v for v in items if v]
        elif value:
            data[key] = value.strip("\"'")
        else:
            data[key] = None

    return data, body


def check_name(value: str, label: str) -> None:
    if len(value) > MAX_NAME:
        error(f"{label}: name is {len(value)} chars, limit is {MAX_NAME}")
    if not NAME_PATTERN.match(value):
        error(f"{label}: name {value!r} must contain only letters, numbers, and hyphens")


def check_description(value: str, label: str) -> None:
    if len(value) > MAX_DESCRIPTION:
        error(f"{label}: description is {len(value)} chars, limit is {MAX_DESCRIPTION}")


def load_json(path: str, label: str):
    if not os.path.isfile(path):
        error(f"{label}: missing file {path}")
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        error(f"{label}: invalid JSON — {exc}")
        return None


def check_tools(tools, label: str) -> None:
    if tools is None:
        return
    if isinstance(tools, str):
        tools = [t.strip() for t in tools.split(",") if t.strip()]
    if not isinstance(tools, list):
        error(f"{label}: tools must be a list or comma-separated string")
        return
    for tool in tools:
        if "/" in tool:  # MCP server tool, e.g. "github/list_issues"
            continue
        if tool in VALID_TOOLS:
            continue
        hint = " (not a real tool name — it will be silently ignored)" if tool in KNOWN_BAD_TOOLS else ""
        error(f"{label}: unknown tool {tool!r}{hint}")


def check_body_for_bad_tools(body: str, label: str) -> None:
    """Flag backticked references to non-existent tools in prose."""
    for bad in sorted(KNOWN_BAD_TOOLS):
        if re.search(rf"`{re.escape(bad)}`", body):
            error(
                f"{label}: body references `{bad}`, which is not a Copilot tool name. "
                f"Use a real tool (grep, glob, view, edit, bash) or reword."
            )


def validate_agent(path: str, rel: str) -> str | None:
    front, body = parse_frontmatter(path)
    if not front:
        error(f"{rel}: missing or unparseable YAML frontmatter")
        return None

    description = front.get("description")
    if not description:
        error(f"{rel}: 'description' is required in agent frontmatter")
    else:
        check_description(description, rel)

    name = front.get("name")
    if name:
        check_name(name, rel)

    check_tools(front.get("tools"), rel)
    check_body_for_bad_tools(body, rel)
    return name or os.path.basename(path).split(".")[0]


def validate_skill(path: str, rel: str) -> str | None:
    front, body = parse_frontmatter(path)
    if not front:
        error(f"{rel}: missing or unparseable YAML frontmatter")
        return None

    name = front.get("name")
    if not name:
        error(f"{rel}: 'name' is required in skill frontmatter")
    else:
        check_name(name, rel)
        folder = os.path.basename(os.path.dirname(path))
        if name != folder:
            warn(f"{rel}: skill name {name!r} does not match its folder {folder!r}")

    description = front.get("description")
    if not description:
        error(f"{rel}: 'description' is required — it is the only signal Copilot uses to select a skill")
    else:
        check_description(description, rel)

    check_body_for_bad_tools(body, rel)
    return name


def validate_plugin(plugin_dir: str, entry: dict) -> None:
    rel_dir = os.path.relpath(plugin_dir, REPO_ROOT)
    manifest_path = os.path.join(plugin_dir, "plugin.json")
    plugin = load_json(manifest_path, f"{rel_dir}/plugin.json")
    if plugin is None:
        return

    name = plugin.get("name")
    if not name:
        error(f"{rel_dir}/plugin.json: 'name' is required")
    else:
        check_name(name, f"{rel_dir}/plugin.json")
        if entry.get("name") and entry["name"] != name:
            error(
                f"name drift: marketplace entry says {entry['name']!r}, "
                f"{rel_dir}/plugin.json says {name!r}"
            )

    if plugin.get("description"):
        check_description(plugin["description"], f"{rel_dir}/plugin.json")

    if entry.get("version") and plugin.get("version"):
        if entry["version"] != plugin["version"]:
            error(
                f"version drift: marketplace entry says {entry['version']!r}, "
                f"{rel_dir}/plugin.json says {plugin['version']!r}. "
                f"Bump both together, and record it in CHANGELOG.md."
            )

    # Agents — path may be overridden, defaults to agents/
    agents_dir = os.path.join(plugin_dir, str(plugin.get("agents") or "agents").rstrip("/"))
    agent_names: list[str] = []
    if os.path.isdir(agents_dir):
        for filename in sorted(os.listdir(agents_dir)):
            if filename.endswith(".md"):
                agent_path = os.path.join(agents_dir, filename)
                found = validate_agent(agent_path, os.path.relpath(agent_path, REPO_ROOT))
                if found:
                    agent_names.append(found)

    # Skills — each is a folder containing SKILL.md
    skills_dir = os.path.join(plugin_dir, str(plugin.get("skills") or "skills").rstrip("/"))
    skill_names: list[str] = []
    if os.path.isdir(skills_dir):
        for folder in sorted(os.listdir(skills_dir)):
            skill_path = os.path.join(skills_dir, folder, "SKILL.md")
            if os.path.isdir(os.path.join(skills_dir, folder)):
                if not os.path.isfile(skill_path):
                    error(f"{rel_dir}/{os.path.basename(skills_dir)}/{folder}: missing SKILL.md")
                    continue
                found = validate_skill(skill_path, os.path.relpath(skill_path, REPO_ROOT))
                if found:
                    skill_names.append(found)

    for label, names in (("agent", agent_names), ("skill", skill_names)):
        duplicates = {n for n in names if names.count(n) > 1}
        for dup in sorted(duplicates):
            error(f"{rel_dir}: duplicate {label} name {dup!r} — they dedupe by name, so one shadows the other")

    print(f"  {name}: {len(agent_names)} agent(s), {len(skill_names)} skill(s)")


def main() -> int:
    os.chdir(REPO_ROOT)
    print("Validating marketplace...")

    marketplace = load_json(MARKETPLACE_MANIFEST, MARKETPLACE_MANIFEST)
    if marketplace is None:
        print_report()
        return 1

    market_name = marketplace.get("name")
    if not market_name:
        error(f"{MARKETPLACE_MANIFEST}: 'name' is required")
    else:
        check_name(market_name, MARKETPLACE_MANIFEST)

    if not marketplace.get("owner"):
        error(f"{MARKETPLACE_MANIFEST}: 'owner' is required")

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        error(f"{MARKETPLACE_MANIFEST}: 'plugins' must be a non-empty array")
        print_report()
        return 1 if errors else 0

    print(f"  marketplace: {market_name} ({len(plugins)} plugin(s))")

    seen: set[str] = set()
    for index, entry in enumerate(plugins):
        label = f"{MARKETPLACE_MANIFEST} plugins[{index}]"

        if not entry.get("name"):
            error(f"{label}: 'name' is required")
        elif entry["name"] in seen:
            error(f"{label}: duplicate plugin name {entry['name']!r}")
        else:
            seen.add(entry["name"])

        if entry.get("description"):
            check_description(entry["description"], label)

        source = entry.get("source")
        if not source:
            error(f"{label}: 'source' is required")
            continue
        if not isinstance(source, str):
            warn(f"{label}: non-string source not validated by this script")
            continue

        plugin_dir = os.path.normpath(os.path.join(REPO_ROOT, source))
        if not os.path.isdir(plugin_dir):
            error(f"{label}: source {source!r} does not resolve to a directory")
            continue

        validate_plugin(plugin_dir, entry)

    print_report()
    return 1 if errors else 0


def print_report() -> None:
    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}")
    print()
    if errors:
        print(f"FAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
    else:
        print(f"OK — no errors, {len(warnings)} warning(s)")


if __name__ == "__main__":
    sys.exit(main())
