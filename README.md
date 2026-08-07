# MB AL AI Toolkit — GitHub Copilot App Marketplace

A custom **plugin marketplace** for the GitHub Copilot app, publishing AL development tooling for Microsoft Dynamics 365 Business Central Per-Tenant Extensions.

> **Demo / showcase project.** This repository demonstrates how to package AL development tooling — a specialist agent plus coding-standard and workflow skills — as a **GitHub Copilot plugin**, and how to distribute it through a **self-hosted marketplace repository** rather than by manual path install. It is not published to any official or public GitHub marketplace; you register it yourself. Use it as a reference template for building your own.

This is the **Copilot app** edition. Two sibling editions package the same AL toolkit for other clients:

| Edition | Repository | Distribution |
|---|---|---|
| Copilot app (this repo) | `mb-al-ai-toolkit-gh-copilot-app` | Custom marketplace |
| Copilot CLI | [`mb-al-ai-toolkit-cli`](https://github.com/mbaic/mb-al-ai-toolkit-cli) | Manual install from a clone |
| Claude Code | [`mb-al-ai-toolkit-cc`](https://github.com/mbaic/mb-al-ai-toolkit-cc) | Manual install from a clone |

## What this marketplace publishes

| Plugin | Version | Contents |
|---|---|---|
| [`mb-al-ai-toolkit`](./plugins/mb-al-ai-toolkit) | 0.1.0 | 1 agent, 7 skills for Business Central AL development |

### Inside the plugin

| Component | Name | What it does |
|---|---|---|
| Agent | `al-fast` | Speed-optimized autonomous AL development; selected via `/agent` |
| Skill | `al-docs-code` | Business-focused documentation for AL code, English + Swedish |
| Skill | `al-review-code` | Reviews AL for quality, security, performance, maintainability |
| Skill | `al-refactor-code` | Refactors AL without expanding scope |
| Skill | `al-unit-tests` | Generates Given-When-Then unit tests using BC test libraries |
| Skill | `al-best-practices` | AL style, naming, and performance rules |
| Skill | `al-general-dev` | YAGNI/KISS/DRY principles for PTE codebases |
| Skill | `al-sortrecordref` | Dynamic `RecordRef` sorting reference, with a deep-dive companion |

Skills are selected by **description match** — phrase your request naturally and Copilot picks the right one. They are not slash commands. Use `/skills` to review what is loaded (the CLI additionally supports `/skills load <name>` to pin one explicitly).

## Repository layout

```
mb-al-ai-toolkit-gh-copilot-app/
├── .github/
│   ├── plugin/
│   │   └── marketplace.json        # marketplace manifest — what this repo publishes
│   └── workflows/
│       ├── validate.yml            # CI: runs scripts/validate.py
│       └── release.yml             # manual: tags a version, publishes a Release
├── plugins/
│   └── mb-al-ai-toolkit/
│       ├── plugin.json             # plugin manifest
│       ├── README.md
│       ├── agents/
│       │   └── al-fast.agent.md
│       └── skills/
│           ├── al-best-practices/SKILL.md
│           ├── al-general-dev/SKILL.md
│           ├── al-docs-code/SKILL.md
│           ├── al-review-code/SKILL.md
│           ├── al-refactor-code/SKILL.md
│           ├── al-unit-tests/SKILL.md
│           └── al-sortrecordref/
│               ├── SKILL.md
│               └── REFERENCE.md
├── scripts/
│   ├── validate.py                 # manifest + frontmatter validator
│   └── release_notes.py            # extracts a CHANGELOG section
├── README.md
├── CHANGELOG.md
└── LICENSE
```

The marketplace manifest lives at `.github/plugin/marketplace.json`. Each entry's `source` is a path relative to the repository root, which is why plugins sit under `plugins/<plugin-name>/`.

## Requirements

- The **GitHub Copilot app** (macOS, Windows, or Linux), or the GitHub Copilot CLI
- An active GitHub Copilot subscription
- An AL workspace for a Business Central Per-Tenant Extension (PTE)
- For the `al-fast` agent's build cycle: `alc` (AL Compiler) reachable from the shell, or `dotnet` with the AL compiler installed as a tool

## Installation — GitHub Copilot app

A plugin served from a custom marketplace is always a two-stage install: **add the marketplace once**, then **install the plugin from it**. In the app both stages happen in the same screen.

> Plugin management in the Copilot app is **GUI-only**. Unlike the CLI, the app has no `/plugin` slash commands — do not try to type `/plugin install` into a session.

### Step 1 — Open the Plugins screen

Open the GitHub Copilot app, go to **Settings**, then click **Plugins**.

### Step 2 — Add this marketplace

Choose **Add marketplace**, and enter this repository as the **source**:

```text
mbaic/mb-al-ai-toolkit-gh-copilot-app
```

The source field accepts either an `OWNER/REPO` GitHub reference (as above) or a full Git URL.

When the **Add plugin marketplace?** dialog appears, choose **Allow**.

> **Shortcut.** Opening the deep link below jumps straight to **Settings → Plugins** with the form already filled in. It does not install anything on its own — you still confirm in the app.
>
> ```text
> ghapp://plugins/marketplace/add?source=mbaic/mb-al-ai-toolkit-gh-copilot-app
> ```

### Step 3 — Install the plugin

In the **Plugins** list, expand the newly added **`mb-al-ai-toolkit-gh-copilot-app`** marketplace, find **`mb-al-ai-toolkit`**, and click **Install**.

> You add the **repository** (`mbaic/mb-al-ai-toolkit-gh-copilot-app`), but the plugin is listed under the **marketplace name** declared in `marketplace.json`. Here those two strings are identical, so the distinction is easy to miss — it still matters, because renaming the repository later would change the first and not the second.

### Step 4 — Verify

The Plugins screen should now show `mb-al-ai-toolkit` as installed, with enable/disable, update, and uninstall controls.

Then confirm the components loaded:

- **Agent** — start a session and type `/agent`. `al-fast` should appear in the picker. It is also selectable from the **Default agent** picker.
- **Skills** — open **Settings → Skills**, or type `/skills` in a session. All seven `al-*` skills should be listed. `/skills reload` re-reads them without restarting the app.

## Installation — Copilot CLI

The same marketplace works from the CLI, which *is* command-driven:

```bash
# Step 1 — register the marketplace
copilot plugin marketplace add mbaic/mb-al-ai-toolkit-gh-copilot-app
copilot plugin marketplace list
copilot plugin marketplace browse mb-al-ai-toolkit-gh-copilot-app

# Step 2 — install the plugin
copilot plugin install mb-al-ai-toolkit@mb-al-ai-toolkit-gh-copilot-app

# Step 3 — verify
copilot plugin list
```

In-session, the CLI also accepts `/plugin marketplace add ...` and `/plugin install ...`, plus `/agent` and `/skills list`.

### Enabling declaratively per repository (CLI and Copilot cloud agent)

Instead of each developer adding the marketplace by hand, commit the registration and enablement into the AL repository the toolkit is used against, in `.github/copilot/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "mb-al-ai-toolkit-gh-copilot-app": {
      "source": {
        "source": "github",
        "repo": "mbaic/mb-al-ai-toolkit-gh-copilot-app"
      }
    }
  },
  "enabledPlugins": {
    "mb-al-ai-toolkit@mb-al-ai-toolkit-gh-copilot-app": true
  }
}
```

Note the nesting: the outer key is the marketplace name, and the discriminator inside the source object is `source`, not `type`.

These repository-level keys are documented as read by the **Copilot CLI and the Copilot cloud agent**. The Copilot app's own install path is the GUI flow above — treat this file as a convenience for CLI and cloud-agent users, not as a substitute for Steps 1–3. One caveat: `autoUpdate: true` is accepted on a repository-level entry but ignored; that opt-in is only honored in a user's own settings.

Skills and MCP servers already configured for your repositories or for the Copilot CLI are picked up by the app automatically. Plugin installation is the part that is not shared — do that in the app.

## Usage

**Agent** — select `al-fast` for fast, autonomous AL edits:

```text
/agent al-fast
> add a posting validation that blocks negative quantities in app/src/Sales
```

**Skills** — phrase the request; Copilot picks the match:

```text
review the AL code in app/src/Sales/SalesPostingMgt.Codeunit.al
write unit tests for app/src/Posting
document the procedure CalculateBalance in app/src/Customer/CustomerCalc.Codeunit.al
refactor app/src/Pricing
how do I sort a generic RecordRef by Document Date descending?
```

## Updating

Plugin components are **cached at install time**. Copilot does not poll this repository, so a push alone changes nothing on an installed client.

**In the app:** open **Settings → Plugins** and use the **update** control on `mb-al-ai-toolkit`. The same screen carries enable/disable and uninstall.

**In the CLI:**

```bash
copilot plugin marketplace update mb-al-ai-toolkit-gh-copilot-app   # re-fetch the catalog
copilot plugin update mb-al-ai-toolkit                              # re-fetch the plugin
```

Bump `version` in **both** `plugins/mb-al-ai-toolkit/plugin.json` and the matching entry in `.github/plugin/marketplace.json` on every meaningful change, and record it in [CHANGELOG.md](./CHANGELOG.md).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `/plugin install` does nothing in the app | The app has no `/plugin` command family — plugin management is GUI-only | Use **Settings → Plugins** instead; `/plugin` exists only in the CLI |
| Marketplace missing from the Plugins screen | The **Add plugin marketplace?** dialog was dismissed instead of allowed | Re-run **Add marketplace** with source `mbaic/mb-al-ai-toolkit-gh-copilot-app` and choose **Allow** |
| Plugin missing after install | `source` path in `marketplace.json` does not match the real folder | Confirm it is repo-root-relative and matches `plugins/mb-al-ai-toolkit` exactly |
| Agent absent from `/agent` | Name collision — a project or personal agent of the same name shadows the plugin's | Agents resolve first-found-wins; rename the local one, or the agent in `agents/*.agent.md` frontmatter |
| Skill never triggers | `description` too vague, or shadowed by a same-named local skill | Skills dedupe by `name`; make the `description` state plainly when to use it. `/skills reload` re-reads them |
| Edits here have no effect | Install-time cache | App: **Settings → Plugins** → update. CLI: `copilot plugin marketplace update`, then `copilot plugin update` |
| Adding the marketplace fails on a private repo | The signed-in account lacks read access to the repository | Grant repository access; private-repo marketplaces work but are gated on the user's own permissions |
| Organization blocks the marketplace | `strictKnownMarketplaces` in enterprise `managed-settings.json` restricts installs to listed marketplaces — this applies to the app as well as the CLI | Ask an administrator to add this repository; an empty list blocks everything |
| `marketplace remove` fails (CLI) | Plugins from it are still installed | Uninstall them first, or pass `--force` |

## Validation

This repository ships no application code, so there is nothing to build. What can break is the
manifests disagreeing with each other, or an agent or skill declaring something Copilot silently
ignores. One script checks all of it:

```bash
python3 scripts/validate.py
```

It runs automatically in CI on every push and pull request touching the manifests or the plugin.
It needs no dependencies — plain Python 3.

## Releasing

Releases are cut by the **Release** workflow: **Actions → Release → Run workflow**, then enter the
version (e.g. `0.2.0`). It refuses to tag anything inconsistent — the manifests must validate, both
must declare that version, `CHANGELOG.md` must have a matching section, and the tag must not already
exist — then creates the annotated tag and a GitHub Release using that changelog section as the notes.

So the release checklist is: bump `plugin.json` and the `marketplace.json` entry, write the
`CHANGELOG.md` section, merge to `main`, run the workflow.

To preview the notes a release would carry:

```bash
python3 scripts/release_notes.py 0.1.0
```

## Authoring notes

Points worth knowing if you fork this as a template:

- **`agents/` and `skills/` are conventions.** `plugin.json` may omit both fields and they are still discovered. They are declared explicitly here for readability.
- **Tool names in agent frontmatter are a fixed vocabulary,** and unrecognized entries are silently ignored — a typo costs the agent a capability with no error. `al-fast` uses `bash`, `view`, `edit`, `grep`, and `glob`.
- **`description` is required on every skill** and is capped at 1024 characters. It is the only thing driving skill selection, so it should say *when to use the skill*, not just what it is.
- **A skill folder can carry companion files.** `al-sortrecordref` keeps its worked examples in `REFERENCE.md` beside `SKILL.md`, keeping the skill body short while the detail stays reachable.

## License

MIT — see [LICENSE](./LICENSE).
