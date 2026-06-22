# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This repo **is** a Claude Code plugin marketplace named `vitor-plugins` (published at
https://github.com/VitorDiToro/claude-plugins). Not application code — a catalog of plugins, each
shipping one or more skills. No build, no tests, no dependencies; the "code" is Markdown skills plus
JSON manifests that Claude Code reads.

## Three independent version layers

| Layer       | File                                  | Field                            |
|-------------|---------------------------------------|----------------------------------|
| Marketplace | `.claude-plugin/marketplace.json`     | `metadata.version`               |
| Plugin      | `<plugin>/.claude-plugin/plugin.json` | `version`                        |
| Skill       | `<plugin>/skills/<skill>/SKILL.md`    | `metadata.version` (frontmatter) |

Plugin and skill move together (same number); the marketplace version moves only when the catalog
(plugins added/removed) changes. Per-skill history lives in a sibling `CHANGELOG.md`, kept out of
`SKILL.md` so the skill body stays lean and isn't loaded into context.

**Full release workflow, local testing, and how to add a plugin: see [docs/development.md](docs/development.md).**

## Key conventions

- **Skill language behavior:** a skill's commit messages stay **English**; what a skill says to the
  user follows the **user's conversation language** (see `commit-helper`). Do not hard-code a single
  user-facing language.
- **Repo docs language:** `README.md` is bilingual (English then Português); `docs/development.md`
  is English; per-plugin docs are bilingual by default (`desrobotizar` is pt-BR only).
- **Commits:** Conventional Commits v1.0.0 (dogfooding `commit-helper`), messages in English.
- **Skill quality bar:** review skills against `superpowers:writing-skills`. Behavioral/discovery
  changes warrant its subagent test; bookkeeping changes (version metadata) do not.
- **Skill `description`:** states *when to use* the skill (triggers), not a catalogue of what it does.

## Gotchas

- `handoff-*.md` are git-ignored on purpose (personal session dumps; the repo is public). Read them
  for context, never commit.
