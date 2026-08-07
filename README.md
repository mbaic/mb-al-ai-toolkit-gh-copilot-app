# MB AL AI Toolkit — GitHub Copilot App Marketplace

A custom **plugin marketplace** for the GitHub Copilot app, publishing AL development tooling for Microsoft Dynamics 365 Business Central Per-Tenant Extensions.

> **Demo / showcase project.** This repository demonstrates how to package AL development tooling — a specialist agent plus coding-standard and workflow skills — as a **GitHub Copilot plugin**, and how to distribute it through a **self-hosted marketplace repository** rather than by manual path install. It is not published to any official or public GitHub marketplace; you register it yourself. Use it as a reference template for building your own.

This is the **Copilot app** edition. Two sibling editions package the same AL toolkit for other clients:

| Edition | Repository | Distribution |
|---|---|---|
| Copilot app (this repo) | `mb-al-ai-toolkit-gh-copilot-app-wip` | Custom marketplace |
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

Skills are selected by **description match** — phrase your request naturally and Copilot picks the right one. They are not slash commands. You can still pin one explicitly with `/skills load <name>`.

## Repository layout

```
mb-al-ai-toolkit-gh-copilot-app-wip/
├── .github/
│   └── plugin/
│       └── marketplace.json        # marketplace manifest — what this repo publishes
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
├── README.md
├── CHANGELOG.md
└── LICENSE
```

The marketplace manifest lives at `.github/plugin/marketplace.json`. Each entry's `source` is a path relative to the repository root, which is why plugins sit under `plugins/<plugin-name>/`.

## Requirements

- GitHub Copilot app, or GitHub Copilot CLI — the two share plugin state
- An active GitHub Copilot subscription
- An AL workspace for a Business Central Per-Tenant Extension (PTE)
- For the `al-fast` agent's build cycle: `alc` (AL Compiler) reachable from the shell, or `dotnet` with the AL compiler installed as a tool

## Installation

A plugin served from a custom marketplace is a two-step install: **register the marketplace once**, then **install the plugin from it**.

### Step 1 — Register the marketplace

```bash
copilot plugin marketplace add mbaic/mb-al-ai-toolkit-gh-copilot-app-wip
```

Or from inside a Copilot session:

```text
/plugin marketplace add mbaic/mb-al-ai-toolkit-gh-copilot-app-wip
```

Confirm it registered under the name declared in the manifest:

```bash
copilot plugin marketplace list
copilot plugin marketplace browse mb-al-ai-toolkit-gh-copilot-app
```

> The marketplace **name** (`mb-al-ai-toolkit-gh-copilot-app`) comes from `marketplace.json` and is deliberately not identical to the repository name. You add the repository, but you install against the name.

### Step 2 — Install the plugin

```bash
copilot plugin install mb-al-ai-toolkit@mb-al-ai-toolkit-gh-copilot-app
```

Or in-session:

```text
/plugin install mb-al-ai-toolkit@mb-al-ai-toolkit-gh-copilot-app
```

Registrations and installs are shared across Copilot clients signed in to the same account, so doing this once makes the plugin available in both the app and the CLI.

### Step 3 — Verify

```bash
copilot plugin list
```

Then, inside a session:

```text
/agent
/skills list
```

`al-fast` should appear in the agent picker, and the seven `al-*` skills in the skills list. `/skills info al-review-code` names the plugin it came from.

### Alternative — register and enable declaratively per repository

Instead of having every developer run Step 1 and Step 2 by hand, commit the marketplace registration and the plugin enablement into the AL repository the toolkit is used against, in `.github/copilot/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "mb-al-ai-toolkit-gh-copilot-app": {
      "source": {
        "source": "github",
        "repo": "mbaic/mb-al-ai-toolkit-gh-copilot-app-wip"
      }
    }
  },
  "enabledPlugins": {
    "mb-al-ai-toolkit@mb-al-ai-toolkit-gh-copilot-app": true
  }
}
```

Note the nesting: the outer key is the marketplace name, and the discriminator inside the source object is `source`, not `type`. Repository-level settings are read by both the Copilot CLI and the Copilot Cloud Agent, so anyone who opens the repository picks the plugin up. One caveat — `autoUpdate: true` is accepted on a repository-level entry but ignored; that opt-in is only honored in a user's own settings.

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

Plugin components are **cached at install time**. Copilot does not poll this repository, so a push alone changes nothing on an installed client. After publishing a change here:

```bash
copilot plugin marketplace update mb-al-ai-toolkit-gh-copilot-app   # re-fetch the catalog
copilot plugin update mb-al-ai-toolkit                              # re-fetch the plugin
```

Bump `version` in **both** `plugins/mb-al-ai-toolkit/plugin.json` and the matching entry in `.github/plugin/marketplace.json` on every meaningful change, and record it in [CHANGELOG.md](./CHANGELOG.md).

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Marketplace not found on install | Not registered, or installed against the repo name instead of the manifest name | `copilot plugin marketplace list`, then install against `mb-al-ai-toolkit-gh-copilot-app` |
| Plugin missing after install | `source` path in `marketplace.json` does not match the real folder | Confirm it is repo-root-relative and matches `plugins/mb-al-ai-toolkit` exactly |
| Agent absent from `/agent` | Name collision — a project or personal agent of the same name shadows the plugin's | Agents resolve first-found-wins; rename the local one, or the agent in `agents/*.agent.md` frontmatter |
| Skill never triggers | `description` too vague, or shadowed by a same-named local skill | Skills dedupe by `name`; make the `description` state plainly when to use it |
| Edits here have no effect | Install-time cache | `copilot plugin marketplace update`, then `copilot plugin update` |
| Organization blocks the marketplace | `strictKnownMarketplaces` in enterprise `managed-settings.json` restricts installs to listed marketplaces | Ask an administrator to add this repository; an empty list blocks everything |
| `marketplace remove` fails | Plugins from it are still installed | Uninstall them first, or pass `--force` |

## Authoring notes

Points worth knowing if you fork this as a template:

- **`agents/` and `skills/` are conventions.** `plugin.json` may omit both fields and they are still discovered. They are declared explicitly here for readability.
- **Tool names in agent frontmatter are a fixed vocabulary,** and unrecognized entries are silently ignored — a typo costs the agent a capability with no error. `al-fast` uses `bash`, `view`, `edit`, `grep`, and `glob`.
- **`description` is required on every skill** and is capped at 1024 characters. It is the only thing driving skill selection, so it should say *when to use the skill*, not just what it is.
- **A skill folder can carry companion files.** `al-sortrecordref` keeps its worked examples in `REFERENCE.md` beside `SKILL.md`, keeping the skill body short while the detail stays reachable.

## License

MIT — see [LICENSE](./LICENSE).
