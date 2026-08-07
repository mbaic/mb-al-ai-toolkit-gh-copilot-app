# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Check the repository name first, every session

**Recorded name: `mbaic/mb-al-ai-toolkit-gh-copilot-app`.** This is the production name; the repository was renamed off an earlier `-wip` suffix on 2026-08-07.

The name is embedded in install commands, manifest URLs, and prose, so a stale copy is a real defect. At the start of every session, before doing anything else:

```bash
git remote get-url origin
grep -rn 'mb-al-ai-toolkit-gh-copilot-app' --include='*.md' --include='*.json' . | grep -v '^\./\.git'
```

If the remote no longer says `mb-al-ai-toolkit-gh-copilot-app`, the rename has happened — carry out the protocol below before any other work, and update the recorded name in this file.

### Rename protocol

**Do not blanket-substitute the bare string.** Since the repo name and the marketplace name are now the same text, a naive `sed 's|mb-al-ai-toolkit-gh-copilot-app|NEW|g'` rewrites both and silently breaks the install identifier for every existing consumer. As of the last audit the string appears **40 times**, split as:

- **11 repo references — safe to rename.** Always qualified by the owner: `mbaic/<name>` or `github.com/mbaic/<name>`.
- **29 marketplace-name references — must not change.** Always bare: the `name` field in `marketplace.json`, `@mb-al-ai-toolkit-gh-copilot-app` install identifiers, `extraKnownMarketplaces` keys, `marketplace browse`/`update` arguments.

So anchor the substitution on the owner prefix:

```bash
grep -rl 'mbaic/mb-al-ai-toolkit-gh-copilot-app' --include='*.md' --include='*.json' . \
  | xargs sed -i 's|mbaic/mb-al-ai-toolkit-gh-copilot-app|mbaic/NEW-REPO-NAME|g'
```

Then confirm the split is still correct — repo references gone, marketplace name untouched:

```bash
grep -rn 'mbaic/mb-al-ai-toolkit-gh-copilot-app' . | grep -v '^\./\.git' || echo "no stale repo references"
python3 -c "import json; assert json.load(open('.github/plugin/marketplace.json'))['name'] == 'mb-al-ai-toolkit-gh-copilot-app'; print('marketplace name intact')"
```

Occurrences by file, as a sanity map:

| File | Repo refs | What they are |
|---|---|---|
| `README.md` | 3 | two `marketplace add` commands, `extraKnownMarketplaces` repo |
| `.github/plugin/marketplace.json` | 2 | `homepage`, `repository` |
| `plugins/mb-al-ai-toolkit/plugin.json` | 2 | `homepage`, `repository` |
| `CLAUDE.md` | 2 | the recorded name above, the declarative-install snippet |
| `CHANGELOG.md` | 1 | the `[0.1.0]` release-tag link |

Also update the layout tree root in `README.md` and the editions table, which name the repo without the owner prefix and so are missed by the anchored `sed`.

### What does NOT change on rename

The **marketplace name** (`mb-al-ai-toolkit-gh-copilot-app`) and the **plugin name** (`mb-al-ai-toolkit`) live in the manifests, not in the repo name. So the install identifier `mb-al-ai-toolkit@mb-al-ai-toolkit-gh-copilot-app` is stable across a rename, and anyone who already installed the plugin keeps working. Only the one-time `marketplace add mbaic/<repo>` registration points at the repository.

Do not "fix" the marketplace name to match a new repo name. Changing it breaks the install identifier for every existing consumer, which a rename otherwise does not.

### The repo name and the marketplace name are now identical

Since the rename, the repository is `mb-al-ai-toolkit-gh-copilot-app` and the marketplace declared in `marketplace.json` is *also* `mb-al-ai-toolkit-gh-copilot-app`. They are two different identifiers that currently happen to hold the same string.

This matters in two directions:

- **A future rename must not assume they move together.** Renaming the repository again changes only the `marketplace add mbaic/<repo>` argument. The marketplace name stays put unless you deliberately change it — and you should not, because it is half of the install identifier every existing consumer uses.
- **A blind `sed` for the shared string will hit both.** After any future rename, re-read `marketplace.json` and confirm its `name` field still says `mb-al-ai-toolkit-gh-copilot-app`. If a substitution changed it, every installed client's `mb-al-ai-toolkit@mb-al-ai-toolkit-gh-copilot-app` identifier breaks.

Before the rename these were different strings and the docs warned that conflating them was the common install failure. That warning no longer applies as written — do not reintroduce it.

### GitHub's redirect

GitHub keeps a redirect from the old repository path after a rename, so `marketplace add mbaic/<old-name>` may keep appearing to work. Do not rely on it: it masks stale references during testing, and it does not survive the old name being claimed by another repository. Treat a passing test that still uses the old name as untested.

## What this repository is

A **self-hosted GitHub Copilot plugin marketplace**. It ships no application code — every file is either a JSON manifest or Markdown that Copilot loads at runtime. There is no build, no test suite, and no linter. "Correctness" here means: the manifests parse, they agree with each other, and every command and identifier in the docs actually exists.

Two layers, and both must stay in sync:

- `.github/plugin/marketplace.json` — the marketplace manifest. Declares marketplace `name` (`mb-al-ai-toolkit-gh-copilot-app`) and a `plugins[]` array. Each entry's `source` is a path **relative to the repository root**, which is why plugins live under `plugins/<plugin-name>/`.
- `plugins/mb-al-ai-toolkit/plugin.json` — the plugin manifest, plus `agents/` and `skills/` beside it.

The marketplace **name** comes from `marketplace.json`, not from the repository name — they are independent identifiers that currently hold the same string (`mb-al-ai-toolkit-gh-copilot-app`). Users run `marketplace add mbaic/mb-al-ai-toolkit-gh-copilot-app` (the repo) and then `plugin install mb-al-ai-toolkit@mb-al-ai-toolkit-gh-copilot-app` (the manifest name). Keep them in step deliberately, not by accident: see the rename protocol above before changing either.

## Relationship to sibling repositories

`mb-al-ai-toolkit-cli` is the **upstream reference** — the same agent and skills packaged as a flat Copilot CLI plugin, installed manually rather than via a marketplace. It is read-only from here. `mb-al-ai-toolkit-cc` is the Claude Code edition.

The agent and skills in this repo were ported from the CLI edition and are otherwise byte-identical to it, **except** for deliberate corrections (see the tool-vocabulary trap below) and client-neutral wording in `al-fast`. When syncing changes from upstream, diff against the reference but do not blindly restore its `search` tool references — they are a known defect there.

## Verification

There is no test command. Run these checks after touching any manifest or frontmatter:

```bash
# Manifests parse
python3 -c "import json; json.load(open('.github/plugin/marketplace.json'))"
python3 -c "import json; json.load(open('plugins/mb-al-ai-toolkit/plugin.json'))"

# Cross-manifest consistency: name, version, description, and a resolvable source
python3 -c "
import json, os
m = json.load(open('.github/plugin/marketplace.json'))
p = json.load(open('plugins/mb-al-ai-toolkit/plugin.json'))
e = m['plugins'][0]
assert e['name'] == p['name'], 'name drift'
assert e['version'] == p['version'], 'version drift'
assert os.path.isdir(e['source']), 'source does not resolve'
print('manifests consistent')
"

# Frontmatter limits: description <= 1024 chars, name <= 64 chars
for f in plugins/mb-al-ai-toolkit/skills/*/SKILL.md plugins/mb-al-ai-toolkit/agents/*.agent.md; do
  awk '/^description:/{sub(/^description: */,""); print length($0), FILENAME}' "$f"
done

# No invalid tool names anywhere
grep -rn '`search`' plugins/ && echo "INVALID TOOL NAME PRESENT" || echo "clean"
```

Version bumps must land in **three** places together: `plugin.json`, the matching `marketplace.json` entry, and `CHANGELOG.md`.

## The tool-vocabulary trap

Agent frontmatter `tools:` and any tool named in an agent or skill **body** must come from Copilot's built-in vocabulary. Unrecognized names are **silently ignored** — no error, the capability just vanishes. This already bit this codebase once: the upstream CLI edition used `search`, which is not a real tool, leaving the agent unable to search. It was replaced with `grep` (content search) and `glob` (file-path patterns).

Valid built-ins: `bash`/`powershell` (plus `list_`/`read_`/`stop_`/`write_` variants), `apply_patch`, `create`, `edit`, `view`, `list_agents`, `read_agent`, `task`, `write_agent`, `ask_user`, `glob`, `grep` (alias `rg`), `skill`, `web_fetch`, and `"*"`. MCP tools are referenced as `server-name/tool-name`.

## Authoring rules

- **`description` drives everything.** It is required on every skill and is the *only* signal Copilot uses to decide when to auto-select one. Write it to say *when to use the skill*, not just what it is. Capped at 1024 characters.
- **`agents/` and `skills/` are conventions.** `plugin.json` may omit both fields entirely and they are still discovered. They are declared explicitly here for readability.
- **Skill folders may carry companion files.** `al-sortrecordref` keeps worked examples in `REFERENCE.md` beside `SKILL.md`, keeping the skill body short while detail stays reachable.
- **Only `name` is required in `plugin.json`.** `category` is free text with no enum.
- **Agents and skills resolve first-found-wins, deduped by name.** A project-level or personal agent silently shadows a plugin's. A plugin can never override local config.

## Documentation discipline

The READMEs are the deliverable as much as the manifests, and their accuracy has already been the main source of defects. Do not invent Copilot commands or flags.

- Real: `copilot plugin marketplace add|list|browse|update|remove`, `copilot plugin install|uninstall|list|update|enable|disable`, in-session `/plugin ...`, `/agent`, `/skills list|info|load`.
- **Not real:** `copilot plugin search`, `copilot plugin validate`, `@plugin-name` chat invocation. GitHub publishes no official manifest validator or Action.
- The Copilot **desktop app's** exact GUI menu path is not documented anywhere verifiable. Describe the app flow generically; do not assert click paths.

When adding a claim about Copilot behavior, verify it against the `github/docs` repository source (`content/copilot/reference/copilot-cli-reference/`) rather than from memory — `docs.github.com` is often blocked by network egress policy, but the repo is cloneable.

## Cache behavior

Pushing to this repository changes nothing on an installed client. Components are cached at install time and Copilot does not poll. Consumers need `copilot plugin marketplace update <marketplace-name>` followed by `copilot plugin update <plugin-name>`.

## Declarative install shape

For `.github/copilot/settings.json` in a *consuming* repository, the discriminator inside the source object is `source`, **not** `type`:

```json
{
  "extraKnownMarketplaces": {
    "mb-al-ai-toolkit-gh-copilot-app": {
      "source": { "source": "github", "repo": "mbaic/mb-al-ai-toolkit-gh-copilot-app" }
    }
  },
  "enabledPlugins": { "mb-al-ai-toolkit@mb-al-ai-toolkit-gh-copilot-app": true }
}
```

Repository-level settings are read by both the Copilot CLI and Cloud Agent. A repo-level `autoUpdate: true` is accepted but ignored — that opt-in is only honored in user settings.
