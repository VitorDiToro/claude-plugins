# Changelog

All notable changes to the `commit-helper` skill are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com);
the `version` / `updated` fields in `SKILL.md` frontmatter point to the latest entry.

## 1.1.0 - 2026-06-22

### Added
- Versioning: `metadata.version` and `metadata.updated` in `SKILL.md` frontmatter,
  plus this changelog, for controlled future updates.
- Concrete Conventional Commits example (input → output) demonstrating header, body, and footer.
- Explicit note on the language convention: commit messages in English,
  user-facing prompts/warnings in Portuguese.

## 1.0.0

### Added
- Initial commit-message helper: staged-change validation (`git diff --staged` guard),
  Conventional Commits v1.0.0 composition, present-then-commit flow,
  allowed commit types, and best practices.
