# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Check the repository name first, every session

**Recorded name: `mbaic/mb-al-ai-toolkit-gh-copilot-app`.** This is the production name; the repository was renamed off an earlier `-wip` suffix on 2026-08-07.

The name is embedded in install commands, manifest URLs, and prose, so a stale copy is a real defect. At the start of every session, before doing anything else:

```bash
git remote get-url origin
grep -rn 'mb-al-ai-toolkit-gh-copilot-app' --include='*.md' --include='*.json' --exclude-dir=.git .
```

> Use `--exclude-dir=.git`, never `grep -v '^\./\.git'`. `.git` is a literal prefix of `.github`, so the filter form also silently drops `.github/plugin/marketplace.json` — the one file where a bad substitution does the most damage.

If the remote no longer says `mb-al-ai-toolkit-gh-copilot-app`, the rename has happened — carry out the protocol below before any other work, and update the recorded name in this file.

### Rename protocol

**Do not blanket-substitute the bare string.** Since the repo name and the marketplace name are now the same text, a naive `sed 's|mb-al-ai-toolkit-gh-copilot-app|NEW|g'` rewrites both and silently breaks the install identifier for every existing consumer.

Recompute before trusting any number here — these drift with every edit:

```bash
# repo references (safe to rename) — always owner-qualified
grep -rho 'mbaic/mb-al-ai-toolkit-gh-copilot-app' --include='*.md' --include='*.json' --exclude-dir=.git . | wc -l
# every occurrence of the string, repo and marketplace alike
grep -rho 'mb-al-ai-toolkit-gh-copilot-app' --include='*.md' --include='*.json' --exclude-dir=.git . | wc -l
```

At the last audit: **50 occurrences total — 19 owner-qualified repo references, 31 bare marketplace-name references.**

- **Repo references — safe to rename.** Always qualified: `mbaic/<name>` or `github.com/mbaic/<name>`.
- **Marketplace-name references — must not change.** Always bare: the `name` field in `marketplace.json`, `@mb-al-ai-toolkit-gh-copilot-app` install identifiers, `extraKnownMarketplaces` keys, `marketplace browse`/`update` arguments.

So anchor the substitution on the owner prefix:

```bash
grep -rl 'mbaic/mb-al-ai-toolkit-gh-copilot-app' --include='*.md' --include='*.json' --exclude-dir=.git . \
  | xargs sed -i 's|mbaic/mb-al-ai-toolkit-gh-copilot-app|mbaic/NEW-REPO-NAME|g'
```

Then confirm the split is still correct — repo references gone, marketplace name untouched:

```bash
grep -rn 'mbaic/mb-al-ai-toolkit-gh-copilot-app' --exclude-dir=.git . || echo "no stale repo references"
python3 -c "import json; assert json.load(open('.github/plugin/marketplace.json'))['name'] == 'mb-al-ai-toolkit-gh-copilot-app'; print('marketplace name intact')"
```

Owner-qualified references by file, as a sanity map (19 total at last audit):

| File | Repo refs | What they are |
|---|---|---|
| `CLAUDE.md` | 7 | the recorded name, this protocol's examples, the declarative snippet |
| `README.md` | 6 | `marketplace add` commands, deep link, `extraKnownMarketplaces` repo, prose |
| `.github/plugin/marketplace.json` | 2 | `homepage`, `repository` |
| `plugins/mb-al-ai-toolkit/plugin.json` | 2 | `homepage`, `repository` |
| `plugins/mb-al-ai-toolkit/README.md` | 1 | the app **Add marketplace** source |
| `CHANGELOG.md` | 1 | the `[0.1.0]` release-tag link |

A release tag link in `CHANGELOG.md` points at `releases/tag/v<version>`. Keep tags and changelog entries in step — a link to a tag that was never pushed is a 404.

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

## Current state

As of 2026-08-07 this repository is **public**, renamed to its production name, and the 0.1.0 content is complete and verified.

- The marketplace and its single plugin were **installed end to end in the GitHub Copilot app** by following the README — Settings → Plugins → Add marketplace → Install. The documented flow is confirmed working, not just structurally valid.
- `main` carries the finished work. CI (`Validate manifests`) runs on every relevant push and has passed.
- **No release has been cut yet.** There are no tags. `CHANGELOG.md` links to `releases/tag/v0.1.0`, which 404s until the Release workflow is run for `0.1.0`. Cutting that release is the outstanding task.

Known follow-up outside this repo: the upstream `mb-al-ai-toolkit-cli` still declares the non-existent `search` tool that was corrected here. It has not been fixed there.

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

This is the test suite. Run it after touching any manifest, agent, or skill:

```bash
python3 scripts/validate.py
```

It exits non-zero on failure and checks: both manifests parse; the marketplace entry and `plugin.json` agree on name and version; `source` resolves to a real directory; every skill folder has a `SKILL.md`; `name` and `description` are present and within the 64/1024-character limits; agent `tools:` entries are all real Copilot tool names; agent and skill *bodies* do not reference non-existent tools; and no two agents or skills share a name.

The same script runs in CI via `.github/workflows/validate.yml` on any push or PR touching `plugins/`, `.github/plugin/`, or the script itself. It is deliberately dependency-free — plain Python 3, no `pip install` — including its own small YAML frontmatter parser, so it runs anywhere without setup.

**If you extend the validator, test that it actually fails.** A check that never fires is worse than no check. Copy the repo to a scratch directory, break the thing on purpose, and confirm a non-zero exit. The `tools:` check was written, appeared to pass, and was in fact silently dropping every block list until exactly that exercise caught it.

Version bumps must land in **three** places together: `plugin.json`, the matching `marketplace.json` entry, and `CHANGELOG.md`. The validator enforces the first two; the changelog is on you.

## Releasing

Releases are cut by the **Release** workflow, not by hand: Actions → Release → Run workflow → enter the version (e.g. `0.2.0`). It validates the manifests, checks both of them declare that version, checks `CHANGELOG.md` has a section for it, refuses to overwrite an existing tag, then creates the annotated tag and a GitHub Release using that changelog section as the notes. There is a `draft` option if you want to review before publishing.

So the release checklist is just: bump `plugin.json` and the `marketplace.json` entry, write the `CHANGELOG.md` section, merge, then run the workflow. Every guard is there so a tag means "this state was coherent" rather than "someone ran the job".

**Do not try to `git push` a tag from a Claude Code sandbox.** The session's git proxy accepts `refs/heads/*` and returns a bare `403` for tag refs — no GitHub headers on the response, while branch pushes to the same URL succeed. It is not a repository setting and not something to debug against GitHub. That restriction is exactly why the release workflow exists: Actions runs on GitHub's side, outside the proxy.

`scripts/release_notes.py <version>` extracts a changelog section and is runnable locally to preview what a release would say.

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

When adding a claim about Copilot behavior, verify it against the `github/docs` repository source rather than from memory — `docs.github.com` is often blocked by network egress policy, but the repo is shallow-cloneable. The CLI reference lives under `content/copilot/reference/copilot-cli-reference/`; the app's under `content/copilot/reference/github-copilot-app-reference/` and `content/copilot/how-tos/github-copilot-app/`. `github.blog` is also egress-blocked; `raw.githubusercontent.com/github/app/main/changelog.md` is not, and is useful for app feature history.

## The app and the CLI are different surfaces

This repository targets the **Copilot app**, but most plugin documentation online describes the **CLI**. They are not interchangeable, and conflating them has already produced errors in this README.

- **The app has no `/plugin` command family at all.** Plugin management is GUI-only: **Settings → Plugins → Add marketplace** (a `source` field taking `OWNER/REPO` or a Git URL) → confirm the **Add plugin marketplace?** dialog → expand the marketplace → **Install**. The deep link `ghapp://plugins/marketplace/add?source=OWNER/REPO` pre-fills that form but still requires confirmation. Never document `/plugin install` as an app instruction.
- **The app does support** `/agent` (agent picker, plus a **Default agent** picker) and `/skills` (including `/skills reload`). Skills are also listed under **Settings → Skills**.
- **`enabledPlugins` / `extraKnownMarketplaces` in `.github/copilot/settings.json` are documented for the CLI and the Copilot cloud agent — not for the app.** Do not present that file as an app install path. Enterprise `managed-settings.json` keys, including `strictKnownMarketplaces`, *are* documented as applying to the app.
- Skills and MCP servers configured for repositories or the CLI *are* automatically available in the app. Plugin installation is the part that is not shared.
- Supported app platforms: macOS, Windows, and Linux.

Still unverified, so do not assert: the app's personal (non-enterprise) on-disk settings path, and whether the plugins feature carries its own preview/GA label distinct from the app's.

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
