# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This repo **is** a Claude Code plugin marketplace named `vitor-plugins` (published at
https://github.com/VitorDiToro/claude-plugins). It is not application code — it is a catalog of
plugins, each of which currently ships one or more skills. There is no build step, no test runner,
and no dependencies; the "code" is Markdown skills plus JSON manifests that Claude Code reads.

## Architecture

Three nested manifest layers, each with its **own independent version number**:

| Layer       | File                                                    | Version field      | Versions… |
|-------------|---------------------------------------------------------|--------------------|-----------|
| Marketplace | `.claude-plugin/marketplace.json`                       | `metadata.version` | the catalog of plugins |
| Plugin      | `<plugin>/.claude-plugin/plugin.json`                   | `version`          | the package |
| Skill       | `<plugin>/skills/<skill>/SKILL.md`                      | `metadata.version` (frontmatter) | the skill's content |

- The marketplace `plugins[]` array points to each plugin via a relative `source` (e.g. `./commit-helper`).
- A skill is a `SKILL.md` whose frontmatter requires `name` and `description`; everything under
  `metadata` (version, updated) is a free-form convention this repo adopts, not part of the spec.
- Each skill keeps a sibling `CHANGELOG.md`. History lives there, **not** in `SKILL.md`, so the
  skill body stays lean (the changelog is never loaded into Claude's context).

Current plugins: `commit-helper` (generates Conventional Commits v1.0.0 messages from staged changes).

## Releasing a change to a skill

Plugin and skill version numbers move **together** (same number). The marketplace version only
moves when the catalog itself changes (a plugin is added/removed). When editing a skill's behavior:

1. `SKILL.md` — bump `metadata.version` and update `metadata.updated`.
2. `<plugin>/.claude-plugin/plugin.json` — bump `version` to the **same** number.
3. `<plugin>/skills/<skill>/CHANGELOG.md` — add a new entry at the top.
4. `README.md` — update the version in the plugins table if it's user-visible.
5. Commit and push. Installed copies update via `/plugin marketplace update vitor-plugins`.

Only touch `marketplace.json` (`metadata.version` + the `plugins[]` array) when adding or removing
a plugin from the catalog.

## Conventions

- **Language split** (deliberate, do not normalize to one language): repo prose, READMEs, and
  handoff notes are in **Portuguese**; skill bodies (`SKILL.md`) and the commit messages this repo
  produces are in **English**, matching git history. The `commit-helper` skill itself encodes this:
  commit messages in English, user-facing prompts/warnings in Portuguese.
- **Commits** follow Conventional Commits v1.0.0 (this is dogfooding the `commit-helper` skill).
- **Skill quality bar:** skills here are reviewed against the `superpowers:writing-skills` skill.
  Behavioral changes (changing what a skill instructs Claude to do) warrant the subagent pressure
  test from that skill; bookkeeping changes (version metadata, examples) do not.

## Testing a skill locally before publishing

Point a marketplace at the local checkout instead of GitHub:

```
/plugin marketplace add /home/vitor/git/claude-plugins
/plugin install commit-helper@vitor-plugins
```

## Gotchas

- `handoff-*.md` files are git-ignored on purpose (personal session dumps; the repo is public).
  Read them for recovered context but never commit them.
