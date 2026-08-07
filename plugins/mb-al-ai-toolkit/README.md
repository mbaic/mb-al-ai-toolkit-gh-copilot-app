# MB AL AI Toolkit

A custom agent and skills for AL development in Microsoft Dynamics 365 Business Central, packaged as a GitHub Copilot app plugin.

## What you get

| Component | Name | What it does |
|---|---|---|
| Agent | `al-fast` | Speed-optimized autonomous AL development for rapid edits and builds |
| Skill | `al-docs-code` | Generate business-focused documentation for AL code with translations |
| Skill | `al-review-code` | Review AL code for quality, security, performance, and maintainability |
| Skill | `al-refactor-code` | Refactor AL code improving quality without expanding scope |
| Skill | `al-unit-tests` | Generate unit tests using Given-When-Then and BC libraries |
| Skill | `al-best-practices` | AL language standards, performance rules, and code quality checklist |
| Skill | `al-general-dev` | Development principles for BC Per-Tenant Extension projects |
| Skill | `al-sortrecordref` | Expert guidance on dynamic record sorting using RecordRef |

Skills are auto-selected by **description match** — phrase your request naturally and Copilot will pick the matching skill. The `al-sortrecordref` skill includes a `REFERENCE.md` companion for deep-dive guidance.

## Install

This plugin is served by the custom marketplace in this repository, not by a public GitHub marketplace. The marketplace must be registered once before the plugin can be installed — see the [root README](../../README.md) for that step and for the declarative, repo-level alternative.

Once the marketplace is registered, install by qualified identifier:

```bash
copilot plugin install mb-al-ai-toolkit@mb-al-ai-toolkit-gh-copilot-app
```

The GitHub Copilot app and the Copilot CLI share plugin state, so installing through either client makes the plugin available in both.

**Verify:**

```bash
copilot plugin list
```

Inside a session, confirm the components loaded:

```text
/agent
/skills list
```

You should see `al-fast` in the agent picker and the seven `al-*` skills in the skills list.

## Usage

**Agent** — pick `al-fast` from the agent picker for fast, autonomous AL edits:

```text
/agent al-fast
> add a posting validation that blocks negative quantities in app/src/Sales
```

**Skills** — phrase the request naturally and Copilot selects the matching skill:

```text
review the AL code in app/src/Sales/SalesPostingMgt.Codeunit.al
write unit tests for app/src/Posting
document the procedure CalculateBalance in app/src/Customer/CustomerCalc.Codeunit.al
refactor app/src/Pricing
```

Or load a skill explicitly when you want to force the match:

```text
/skills load al-sortrecordref
> how do I sort a generic RecordRef by Document Date descending?
```

`al-sortrecordref` keeps its worked examples in a companion `REFERENCE.md` next to `SKILL.md`, which the skill draws on for detailed patterns.

## Layout

```
mb-al-ai-toolkit/
├── plugin.json
├── agents/
│   └── al-fast.agent.md
├── skills/
│   ├── al-best-practices/SKILL.md
│   ├── al-general-dev/SKILL.md
│   ├── al-docs-code/SKILL.md
│   ├── al-review-code/SKILL.md
│   ├── al-refactor-code/SKILL.md
│   ├── al-unit-tests/SKILL.md
│   └── al-sortrecordref/
│       ├── SKILL.md
│       └── REFERENCE.md
└── README.md
```

## Requirements

- GitHub Copilot app with an active Copilot subscription
- AL workspace for a Business Central Per-Tenant Extension
- For `al-fast`'s build cycle: `alc` (AL Compiler) reachable from the shell, or `dotnet` with the AL compiler installed as a tool

## License

MIT — see [LICENSE](../../LICENSE).
