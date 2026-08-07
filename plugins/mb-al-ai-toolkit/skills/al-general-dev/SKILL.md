---
name: al-general-dev
description: General development principles for Business Central Per-Tenant Extension (PTE) projects — YAGNI, KISS, DRY, Always Works™, code organization by feature, naming, comments, error handling, and testing/validation guidance. Use for any work inside a BC PTE codebase, especially when scoping new code or reviewing organization-level decisions.
---

# General Development Guidelines

## PTE Context

This is a Per-Tenant Extension for a **single customer**. Focus on:
- Solving actual requirements, not hypothetical future needs
- Simple, maintainable solutions over clever abstractions
- Code readable by medium-senior developers

## Core Principles

### YAGNI (You Aren't Gonna Need It)
Build only what's required RIGHT NOW. Avoid "might need later" or "just in case" features.

### KISS (Keep It Simple)
Choose simple, obvious implementations over clever solutions. Simple code is easier to maintain.

### DRY (Don't Repeat Yourself)
Single source of truth. Extract duplicate code only after 3+ identical occurrences.

### Always Works™
- Code must be production-ready
- Test the exact feature changed
- Zero warnings/errors before commit
- "Should work" ≠ "does work"

## Code Organization

- **By Feature**: Organize code by business feature, not object type
- **Folder Structure**: `src/Feature/Subfeature/ObjectName.ObjectType.al`
- **Modularity**: Write reusable procedures, avoid monolithic code blocks

## Best Practices

- **Consistency First**: Follow existing patterns in the codebase
- **No Copy-Paste**: If solving the same problem, create a shared helper procedure
- **Documentation**: Use comments for non-obvious logic; code should be self-explanatory
- **Dependencies**: Minimize external dependencies, keep code self-contained

## Code Quality

- **Cognitive Complexity**: Refactor procedures with complexity >= 15
- **Variables**: Use meaningful names (PascalCase for variables, UPPERCASE for constants)
- **Comments**: Explain WHY, not WHAT; code shows WHAT
- **File Management**: Never overwrite existing files; add new files instead

## Testing & Validation

- **Test Files**: Separate test code from application code
- **File Naming**: Use consistent naming: `<ObjectName>.<ObjectType>.al`
- **Separation**: App project contains logic; Test project references App as dependency

## Error Handling

- **Labels**: All user-facing messages must use label variables, never hardcoded text
- **Try Functions**: Use only for read/validation/parsing logic with no database writes — they catch runtime errors and return `false`, but do not roll back any partial writes
- **Error Messages**: Provide meaningful context to users
- **Logging**: Add custom logging only when explicitly requested
