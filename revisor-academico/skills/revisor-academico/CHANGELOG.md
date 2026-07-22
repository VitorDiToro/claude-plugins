# Changelog

All notable changes to the `revisor-academico` skill are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com);
the `metadata.version` / `metadata.updated` fields in `SKILL.md` frontmatter point to the latest entry.

## 1.0.0 - 2026-07-22

### Added
- Initial release. Editorial review of academic LaTeX reports following (non-strict) ABNT.
- Output contract: a `revisao/` folder with a mandatory `00_INDICE.md` (disclaimer, timestamp,
  "how to use", file table, executive summary) plus one Markdown file per problem category.
- Items carry a severity marker (🔴 critical / 🟠 important / 🟡 minor), are sorted by severity
  within each file, and get a unique ID (category prefix + index, e.g. `C1`, `G2`, `TC1`).
- Per-item template: severity, title, `Local` (`file:line`), `Trecho`, `Problema`, `Sugestão`.
- Strict no-edit rule: the skill never modifies the source `.tex` files — it only reports findings.
- Built with `superpowers:writing-skills` (RED/GREEN/REFACTOR): baseline showed agents deliver
  review inline in chat without the structured files; the skill enforces the output contract,
  verified with a subagent test on a planted-issue LaTeX sample.
