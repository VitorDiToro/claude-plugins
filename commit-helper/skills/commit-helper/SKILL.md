---
name: commit-helper
description: Use when writing a commit message, committing staged changes, or asked for a Conventional Commits message. Keywords - git commit, conventional commits, commit message, staged changes.
metadata:
  version: 1.1.0
  updated: "2026-06-22"
---

# Generating Commit Messages

Write commit messages in **English** (matching this repository's history),
following the Conventional Commits v1.0.0 specification. Keep the language split:
**commit messages in English**, but **user-facing prompts and warnings in Portuguese** —
do not normalize either side to a single language.

## Instructions

1. **Capture and validate staged changes:** Run `git diff --staged` and capture its output.
   - If the output is **empty**, **stop immediately** and inform the user:
     > ⚠️ Nenhuma alteração em stage encontrada. Use `git add <arquivo>` para preparar as mudanças antes de gerar a mensagem de commit.
   - If the output is **non-empty**, use it directly to inspect the changes — no second `git` call needed.

2. **Compose the message** following Conventional Commits v1.0.0:
   - **Header:** `<type>[optional scope]: <description>` — aim for ≤50 characters, hard limit 72.
   - **Body** (optional): explain *what* and *why*, wrapped at 72 characters.
   - **Footer** (optional): issue references (e.g., `Fixes #123`) or `BREAKING CHANGE:`.

3. **Present, then commit:**
   - **Default:** show the proposed message and **wait for the user's OK** before committing.
   - **Direct commit:** if the user explicitly asked to commit directly, skip the confirmation and commit immediately.

   Single-line message:
   ```bash
   git commit -m "<header>"
   ```
   Message with body/footer — use a heredoc so lines wrap correctly:
   ```bash
   git commit -F - <<'EOF'
   <header>

   <body>

   <footer>
   EOF
   ```
   Confirm success by showing the output of the `git commit` command.

## Allowed Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes that affect the build system or external dependencies
- `ci`: Changes to our CI configuration files and scripts
- `chore`: Other changes that don't modify src or test files

## Best practices

- **Imperative mood:** use imperative, present tense in the description (e.g., "add", not "added" or "adds").
- **Formatting:** do not capitalize the first letter of the description and do not end it with a period.
- **Body:** explain *what* and *why*, not *how*. Separate header and body with a blank line.
- **Breaking changes:** append `!` after the type/scope (e.g., `feat(api)!:`) or add `BREAKING CHANGE:` in the footer.

## Example

Staged change: added a login endpoint and JWT validation middleware.

```
feat(auth): implement JWT-based authentication

Add the login endpoint and token validation middleware so protected
routes reject requests without a valid token.

Refs #42
```

Note: imperative mood, no trailing period, body explains *what/why* wrapped at 72,
and the footer references the issue.

---

Version history: see [CHANGELOG.md](CHANGELOG.md).
