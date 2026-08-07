# Changelog

All notable changes to this marketplace and the plugins it publishes are recorded here.
This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-08-07

Initial release of the `mb-al-ai-toolkit-gh-copilot-app` marketplace, publishing one plugin.

### Added

- **Marketplace manifest** at `.github/plugin/marketplace.json`, publishing a single plugin from `plugins/mb-al-ai-toolkit`.
- **`mb-al-ai-toolkit` plugin** — the AL development toolkit for Microsoft Dynamics 365 Business Central Per-Tenant Extensions, ported from the
  [`mb-al-ai-toolkit-cli`](https://github.com/mbaic/mb-al-ai-toolkit-cli) Copilot CLI edition:
  - 1 agent: `al-fast` (speed-optimized autonomous AL development)
  - 7 skills: `al-docs-code`, `al-review-code`, `al-refactor-code`, `al-unit-tests`,
    `al-best-practices`, `al-general-dev`, `al-sortrecordref`

### Changed

- Repository restructured from a flat single-plugin layout into a marketplace layout
  (`.github/plugin/marketplace.json` + `plugins/<plugin-name>/`), so the plugin installs
  through the GitHub Copilot app's `plugin@marketplace` flow rather than by manual path install.
- `al-fast` build-cycle guidance made client-neutral — it no longer assumes a Copilot CLI terminal
  session, since the same agent now runs in the Copilot app.

### Fixed

- Replaced the non-existent `search` tool with `grep` and `glob` in the `al-fast` agent's `tools`
  frontmatter and body, and in the four skills that referenced it (`al-docs-code`, `al-review-code`,
  `al-refactor-code`, `al-unit-tests`). `search` is not part of Copilot's built-in tool vocabulary;
  unrecognized tool names are silently ignored, so the agent was shipping without a code-search
  capability and the skills were pointing at a tool that would never resolve.

[0.1.0]: https://github.com/mbaic/mb-al-ai-toolkit-gh-copilot-app-wip/releases/tag/v0.1.0
