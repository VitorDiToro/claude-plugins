# Development guide

This repository **is** a Claude Code plugin marketplace (`vitor-plugins`): a catalog of plugins,
each shipping one or more skills. There is no build step, runtime, or dependencies — the "code" is
Markdown skills plus JSON manifests that Claude Code reads.

## Repository structure

```
claude-plugins/                          # the repo IS the marketplace
├── .claude-plugin/marketplace.json      # catalog of plugins (marketplace version)
├── README.md                            # user-facing, bilingual (EN + PT-BR)
├── CLAUDE.md                            # AI-agent guidance (essentials + links here)
├── docs/
│   ├── development.md                   # this file
│   └── <plugin>.md                      # per-plugin deep dive
└── <plugin>/                            # one folder per plugin
    ├── .claude-plugin/plugin.json       # plugin version
    └── skills/<skill>/
        ├── SKILL.md                     # skill version (metadata.version)
        └── CHANGELOG.md                 # per-skill history
```

## Versioning: three independent layers

| Layer       | File                                  | Field                            | Versions          |
|-------------|---------------------------------------|----------------------------------|-------------------|
| Marketplace | `.claude-plugin/marketplace.json`     | `metadata.version`               | the catalog       |
| Plugin      | `<plugin>/.claude-plugin/plugin.json` | `version`                        | the package       |
| Skill       | `<plugin>/skills/<skill>/SKILL.md`    | `metadata.version` (frontmatter) | the skill content |

Plugin and skill move together (same number). The marketplace version moves **only** when the
catalog changes (a plugin is added or removed). Per-skill history lives in a sibling `CHANGELOG.md`,
kept out of `SKILL.md` so the skill body stays lean and isn't loaded into context.

A skill's frontmatter requires only `name` and `description`; everything under `metadata`
(`version`, `updated`) is a free-form convention this repo adopts, not part of the skill spec.

## Releasing a change to a skill

1. `SKILL.md` — bump `metadata.version` and update `metadata.updated`.
2. `<plugin>/.claude-plugin/plugin.json` — bump `version` to the **same** number.
3. `<plugin>/skills/<skill>/CHANGELOG.md` — add a new entry at the top.
4. `README.md` — update the version in the plugins table (**both** language sections).
5. Commit and push. Installed copies update via `/plugin marketplace update vitor-plugins`.

Touch `marketplace.json` (`metadata.version` + the `plugins[]` array) **only** when adding or
removing a plugin from the catalog.

## Testing a plugin locally

Point a marketplace at the local checkout instead of GitHub:

```
/plugin marketplace add /home/vitor/git/claude-plugins
/plugin install <plugin>@vitor-plugins
```

## Adding a new plugin

1. Create `<plugin>/.claude-plugin/plugin.json` and `<plugin>/skills/<skill>/SKILL.md`
   (+ `CHANGELOG.md`), mirroring an existing plugin.
2. Add an entry to `marketplace.json` `plugins[]` (`"source": "./<plugin>"`) and bump the
   marketplace `metadata.version`.
3. Add a row to the README plugins table (**both** language sections), linking to `docs/<plugin>.md`.
4. Write `docs/<plugin>.md`.

## Conventions

- **Skill language behavior:** a skill's commit messages stay in **English**; what a skill says to
  the user follows the **user's conversation language**. Do not hard-code a single user-facing
  language. (See `commit-helper`.)
- **Repo docs language:** `README.md` is **bilingual** (English first, then Português); this dev
  guide is **English**; per-plugin docs are **bilingual by default**. Exception: a skill whose
  subject is intrinsically a single language may be documented in that language — e.g.
  `desrobotizar` is **pt-BR only**.
- **Commits:** Conventional Commits v1.0.0 (this repo dogfoods `commit-helper`); commit messages in
  English.
- **Skill quality bar:** skills are reviewed against the `superpowers:writing-skills` skill.
  Behavioral or discovery changes warrant its subagent pressure/discovery test; bookkeeping changes
  (version metadata, examples) do not.
- **Skill `description`:** the frontmatter `description` states **when to use** the skill (triggers
  and symptoms), not a catalogue of what it does — keep it lean for discovery.
