# Implementation Guide: Custom Marketplace and Two Plugins for the GitHub Copilot App

**Scope:** Create one GitHub repository that acts as a Copilot plugin marketplace, and ship two production-ready plugins for Business Central AL development: an AL code review toolkit and an AL test automation toolkit.

**Audience:** An engineer or an LLM coding agent implementing this from scratch, with no prior context beyond this file.

**Assumptions stated explicitly:**
- You have a GitHub account and permission to create a repository.
- You have the GitHub Copilot app installed and signed in.
- The Copilot app's Plugins screen currently requires the `plugin@marketplace` install format. If a future app version restores direct repository installs, steps 6 and 7 in Part 3 become optional but the repository structure below still works.
- The AL-Go for GitHub template is already set up in the target Business Central repositories that these plugins will be used against. This guide does not set up AL-Go itself.

---

## Part 1: Repository structure

Create a new repository, for example `bc-copilot-marketplace`. Final structure:

```
bc-copilot-marketplace/
├── README.md
├── .github/
│   └── plugin/
│       └── marketplace.json
└── plugins/
    ├── al-code-review-toolkit/
    │   ├── plugin.json
    │   ├── README.md
    │   ├── agents/
    │   │   └── bc-al-reviewer.agent.md
    │   └── skills/
    │       ├── al-code-review/
    │       │   └── SKILL.md
    │       └── al-performance-check/
    │           └── SKILL.md
    └── al-test-automation-toolkit/
        ├── plugin.json
        ├── README.md
        ├── agents/
        │   └── bc-al-test-engineer.agent.md
        ├── skills/
        │   └── al-test-generation/
        │       └── SKILL.md
        └── .mcp.json
```

---

## Part 2: File contents

Create every file below with the exact content shown. Do not change field names in the JSON files; the Copilot plugin and marketplace loaders expect these exact keys.

### 2.1 `.github/plugin/marketplace.json`

```json
{
  "name": "bc-copilot-marketplace",
  "owner": {
    "name": "Your Business Central Team",
    "email": "bc-tooling@yourcompany.com"
  },
  "metadata": {
    "description": "Business Central AL plugins for the GitHub Copilot app: code review and test automation.",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "al-code-review-toolkit",
      "description": "AL-aware code review agent and skills for Business Central pull requests.",
      "version": "1.0.0",
      "source": "./plugins/al-code-review-toolkit"
    },
    {
      "name": "al-test-automation-toolkit",
      "description": "AL test codeunit generation agent, skill, and read-only AL-Go pipeline visibility via MCP.",
      "version": "1.0.0",
      "source": "./plugins/al-test-automation-toolkit"
    }
  ]
}
```

### 2.2 Plugin 1: `plugins/al-code-review-toolkit/plugin.json`

```json
{
  "name": "al-code-review-toolkit",
  "description": "AL-aware code review agent and skills for Business Central pull requests.",
  "version": "1.0.0",
  "author": {
    "name": "Your Business Central Team"
  },
  "license": "MIT",
  "keywords": ["business-central", "al", "code-review", "copilot"],
  "agents": "agents/",
  "skills": "skills/"
}
```

### 2.3 Plugin 1: `plugins/al-code-review-toolkit/agents/bc-al-reviewer.agent.md`

```markdown
---
name: bc-al-reviewer
description: Reviews Business Central AL code changes for correctness, performance, upgrade safety, and AL-Go readiness.
tools: ["view", "search"]
---

You are a Business Central AL solution architect. You review AL code changes before merge.

Rules:
1. Read the full diff before you comment. Do not review a change in isolation from its surrounding codeunit or page.
2. Check every data access statement. Look for missing `SetLoadFields`, unfiltered `FindSet` loops, and unnecessary `CalcFields` inside loops.
3. Check every new or changed table field. Confirm it has a caption, a correct data type, and a data classification.
4. Check every new event subscriber. Confirm it does not change posting behavior without an explicit business reason stated in the pull request description.
5. Check permission sets. Confirm new objects are covered.
6. Check upgrade code. If a table structure changes, confirm an upgrade codeunit exists or state clearly that one is missing.
7. Check for AL-Go readiness. Confirm the change includes or updates a test codeunit when it changes business logic.
8. State your findings as a numbered list, ordered from highest risk to lowest risk. For each finding, state the file, the line or object, the risk, and a suggested fix.
9. Do not approve or reject the pull request. State findings only. A human reviewer makes the merge decision.
10. If you are not sure whether an AL API or pattern is current, say so explicitly instead of guessing.
```

### 2.4 Plugin 1: `plugins/al-code-review-toolkit/skills/al-code-review/SKILL.md`

```markdown
---
name: al-code-review
description: Detailed checklist for reviewing Business Central AL code changes. Load this skill when reviewing an AL pull request or diff.
---

Use this checklist when you review AL code.

## Data access
- Check `SetLoadFields` on records that only read a few fields.
- Check filters exist before `FindSet`, `FindFirst`, or `FindLast`.
- Check `CalcFields` calls are outside loops where possible.
- Check FlowFields are not written to directly.

## Objects and structure
- Check object IDs are inside the assigned range for the app.
- Check table and field captions exist and use correct casing.
- Check new tables have a primary key that matches the business requirement.
- Check enums are used instead of options for new fields.

## Events and extensibility
- Check event subscribers have a clear, single purpose.
- Check subscribers to posting codeunits do not introduce side effects that change posted amounts without a stated business reason.
- Check publishers are added instead of direct code changes to base application objects, where possible.

## Permissions
- Check a permission set exists for every new object.
- Check the permission set is included in the app's permission set list.

## Tests
- Check a test codeunit exists for new or changed business logic.
- Check test codeunits use `[Test]` attributes and follow the Given-When-Then naming pattern in the test method name.
- Check tests use library codeunits for test data setup instead of duplicated setup code.

## Upgrade
- Check an upgrade codeunit exists when a table structure changes in a way that affects existing data.
- Check upgrade code is idempotent. It must be safe to run more than once.

## Labels and text
- Check user-facing text uses labels, not hardcoded strings.
- Check labels have a comment that explains context, when the text is ambiguous.
```

### 2.5 Plugin 1: `plugins/al-code-review-toolkit/skills/al-performance-check/SKILL.md`

```markdown
---
name: al-performance-check
description: Checklist for finding performance problems in Business Central AL code. Load this skill when the review agent needs a deeper performance pass.
---

Use this checklist to find performance problems in AL code.

## Loops and queries
- Flag any `CalcFields` call inside a loop. Suggest moving it outside the loop or using a query object instead.
- Flag any `FindSet` without a filter on a table that can hold a large number of records.
- Flag repeated calls to the same lookup inside a loop. Suggest caching the result in a variable before the loop.

## Temporary tables
- Check temporary tables are used for calculations that do not need to persist.
- Check temporary tables are cleared between unrelated uses in the same procedure.

## Reports and pages
- Flag report data items that filter after `OnPreDataItem` instead of using a request page filter.
- Flag page `SourceTableView` filters that are missing when the underlying table can be large.

## Background and batch work
- Check long-running batch logic runs in a job queue entry, not directly in a user session.
- Check commit points exist in long batch loops to avoid holding locks for an extended time.

## Output format
State each performance finding with: the object and procedure name, the specific pattern found, the expected impact, and a suggested fix. Order findings from highest expected impact to lowest.
```

### 2.6 Plugin 2: `plugins/al-test-automation-toolkit/plugin.json`

```json
{
  "name": "al-test-automation-toolkit",
  "description": "AL test codeunit generation agent, skill, and read-only AL-Go pipeline visibility via MCP.",
  "version": "1.0.0",
  "author": {
    "name": "Your Business Central Team"
  },
  "license": "MIT",
  "keywords": ["business-central", "al", "testing", "al-go", "copilot"],
  "agents": "agents/",
  "skills": "skills/",
  "mcpServers": ".mcp.json"
}
```

### 2.7 Plugin 2: `plugins/al-test-automation-toolkit/agents/bc-al-test-engineer.agent.md`

```markdown
---
name: bc-al-test-engineer
description: Generates Business Central AL test codeunits for business logic changes, and checks AL-Go pipeline status for existing pull requests.
tools: ["view", "edit", "search"]
---

You are a Business Central AL test engineer. You write AL test codeunits and you check pipeline status.

Rules:
1. Before you write a test, identify the exact business rule under test in one sentence.
2. Name test methods using the pattern: `[Scenario]_[ExpectedResult]`. For example: `PostSalesInvoiceWithNegativeQuantity_ThrowsError`.
3. Use library codeunits for test data setup. Do not duplicate setup logic that already exists in a library codeunit in the same app.
4. Every test codeunit must have `Subtype = Test` and every test method must have the `[Test]` attribute.
5. Use `Assert.AreEqual`, `Assert.IsTrue`, or the closest matching Assert method. State the expected value and the actual value in the assertion message.
6. Cover at least one positive case and one negative case for every business rule under test, unless the rule under test cannot fail.
7. If a GitHub MCP server is available, use it only to read AL-Go workflow run status for the relevant pull request. Do not use it to trigger workflows or to write to the repository.
8. State clearly which parts of the generated test still need a human to verify against real Business Central data, if any.
9. Do not claim a test passes. You do not execute AL code. State that the test still needs to run through the AL-Go pipeline before it is trusted.
```

### 2.8 Plugin 2: `plugins/al-test-automation-toolkit/skills/al-test-generation/SKILL.md`

```markdown
---
name: al-test-generation
description: Detailed pattern for writing Business Central AL test codeunits. Load this skill when generating or reviewing AL tests.
---

Follow this pattern when you write an AL test codeunit.

## Structure

```al
codeunit 50100 "Sales Posting Tests"
{
    Subtype = Test;

    [Test]
    procedure PostSalesInvoiceWithNegativeQuantity_ThrowsError()
    var
        SalesHeader: Record "Sales Header";
        SalesLine: Record "Sales Line";
        LibrarySales: Codeunit "Library - Sales";
        Assert: Codeunit Assert;
    begin
        // [GIVEN] A sales invoice with a negative quantity line
        LibrarySales.CreateSalesInvoice(SalesHeader);
        LibrarySales.CreateSalesLine(SalesLine, SalesHeader, SalesLine.Type::Item, '', -1);

        // [WHEN] The invoice is posted
        asserterror LibrarySales.PostSalesDocument(SalesHeader, true, true);

        // [THEN] Posting fails with a quantity error
        Assert.ExpectedError('Quantity must not be negative');
    end;
}
```

## Rules
- Use `[GIVEN]`, `[WHEN]`, `[THEN]` comments inside every test method body.
- Use library codeunits from the base test framework, for example `Library - Sales`, `Library - Inventory`, `Library - ERM`, instead of manual record creation.
- Use `asserterror` for negative test cases, and confirm the error text with `Assert.ExpectedError`.
- Keep one business scenario per test method. Do not combine unrelated assertions in a single test.
- Give the test codeunit a name that matches the area under test, for example "Sales Posting Tests", not a generic name like "Test1".
- Assign the test codeunit an ID inside the app's reserved test object range.

## Output
When generating a test, output the full AL codeunit, ready to save into the app's Test folder. State the file name to use, following the pattern `<Area><Purpose>.Test.al`.
```

### 2.9 Plugin 2: `plugins/al-test-automation-toolkit/.mcp.json`

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/readonly",
      "tools": ["*"],
      "headers": {
        "X-MCP-Toolsets": "actions,pull_requests,repos"
      }
    }
  }
}
```

This configuration uses the GitHub-hosted read-only MCP endpoint. It exposes only Actions, Pull Requests, and Repos toolsets, and it cannot write to the repository. This matches the read-only boundary described in the accompanying blog post: the agent can check AL-Go workflow status but cannot trigger runs, merge pull requests, or push changes.

---

## Part 3: Step-by-step setup

### Step 1: Create and populate the repository

```bash
mkdir bc-copilot-marketplace && cd bc-copilot-marketplace
git init
mkdir -p .github/plugin
mkdir -p plugins/al-code-review-toolkit/agents
mkdir -p plugins/al-code-review-toolkit/skills/al-code-review
mkdir -p plugins/al-code-review-toolkit/skills/al-performance-check
mkdir -p plugins/al-test-automation-toolkit/agents
mkdir -p plugins/al-test-automation-toolkit/skills/al-test-generation
```

Create every file listed in Part 2 in its corresponding path. Then:

```bash
git add .
git commit -m "Add BC Copilot marketplace with two AL plugins"
git branch -M main
git remote add origin https://github.com/YOUR-ORG/bc-copilot-marketplace.git
git push -u origin main
```

### Step 2: Register the marketplace

Option A, using Copilot CLI, run once by any team member with access:

```bash
copilot plugin marketplace add YOUR-ORG/bc-copilot-marketplace
```

Option B, using the GitHub Copilot app:

1. Open **Settings → Plugins**.
2. Select **Add marketplace**.
3. Enter `YOUR-ORG/bc-copilot-marketplace`.
4. Confirm the marketplace name shown matches `bc-copilot-marketplace`.

Marketplace registrations are shared across Copilot clients signed in with the same account, so registering through either path makes the marketplace available everywhere.

### Step 3: Install both plugins

In the GitHub Copilot app, **Settings → Plugins → Install**:

```
al-code-review-toolkit@bc-copilot-marketplace
al-test-automation-toolkit@bc-copilot-marketplace
```

Or from the CLI, which uses the same shared plugin state:

```bash
copilot plugin install al-code-review-toolkit@bc-copilot-marketplace
copilot plugin install al-test-automation-toolkit@bc-copilot-marketplace
```

### Step 4: Verify installation

In the app:
- **Settings → Custom Agents**: confirm `bc-al-reviewer` and `bc-al-test-engineer` are listed.
- **Settings → Skills**: confirm `al-code-review`, `al-performance-check`, and `al-test-generation` are listed.
- **Settings → MCP Servers**: confirm the `github` read-only server from the test automation plugin is listed.

From the CLI:

```bash
copilot plugin list
```

### Step 5: Test each plugin

**Code review agent:**
1. Open a session against your Business Central AL repository.
2. Run `/agent` and select `bc-al-reviewer`.
3. Ask: "Review the AL changes in this branch against main."
4. Confirm the agent produces a numbered, risk-ordered list of findings, and does not state an approve or reject decision.

**Test automation agent:**
1. Open a session against the same repository.
2. Run `/agent` and select `bc-al-test-engineer`.
3. Ask: "Generate an AL test codeunit for the sales invoice posting validation in [specific codeunit name]."
4. Confirm the agent produces a full AL test codeunit following the Given-When-Then pattern, and states that the test still needs to run through AL-Go before it is trusted.
5. Ask: "Check the AL-Go pipeline status for pull request #[number]."
6. Confirm the agent reads pipeline status through the read-only MCP server and does not attempt to trigger a workflow.

### Step 6: Update a plugin after changes

```bash
git add .
git commit -m "Update al-code-review-toolkit checklist"
git push
copilot plugin update al-code-review-toolkit
```

Reinstall or update from the app's Plugins screen if you are not using the CLI. The app caches plugin content at install time and does not poll the repository automatically.

---

## Part 4: Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Marketplace not found when installing | Marketplace not registered, or wrong name | Confirm `copilot plugin marketplace list` shows `bc-copilot-marketplace` before installing |
| Plugin not listed after install | Wrong `source` path in `marketplace.json` | Confirm the path is relative to the repository root and matches the actual folder name exactly |
| Agent does not appear in `/agent` | Name collision with a project or personal agent | Rename the agent in `agents/*.agent.md` front matter, using a distinct prefix such as `bc-al-` |
| Skill never loads | `SKILL.md` missing or description too vague | Confirm the file is at `skills/<name>/SKILL.md` and the `description` field states clearly when to use it |
| MCP server missing from app settings | `.mcp.json` not referenced in `plugin.json` | Confirm `plugin.json` has `"mcpServers": ".mcp.json"` |
| Edits to plugin files have no effect | Local or app plugin cache | Reinstall or update the plugin after every push |
| Organization blocks the marketplace | `strictKnownMarketplaces` set in `managed-settings.json` | Ask an organization admin to add the repository to the allowed marketplaces list |

---

## Part 5: Production readiness checklist

Before treating this marketplace as a team standard, confirm:

- [ ] Repository has branch protection on `main`, so plugin changes go through pull request review like any other code change.
- [ ] Both plugin `version` fields are updated on every meaningful change, and the change is noted in each plugin's `README.md`.
- [ ] The MCP server in the test automation plugin remains scoped to read-only toolsets. Any future write scope needs a separate review and an explicit approval-based pattern, not a silent scope change.
- [ ] Every generated AL test and every code review finding still goes through the standard AL-Go pipeline and human pull request review before merge. Neither plugin bypasses this.
- [ ] If the organization uses `managed-settings.json`, the marketplace repository is on the allowed list, and this has been confirmed with an organization administrator.
