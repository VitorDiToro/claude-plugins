# Changelog

All notable changes to the `revisor-academico` skill are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com);
the `metadata.version` / `metadata.updated` fields in `SKILL.md` frontmatter point to the latest entry.

## 1.1.0 - 2026-07-22

### Changed
- Expanded the "Terminologia e consistência", "Estrutura e rigor
  acadêmico", and "Conteúdo técnico" checklist items from single dense
  bullets into grouped subcategories, mirroring the earlier
  "LaTeX / estrutura" treatment.
- Added 3 guardrails to "Erros comuns a evitar" around judgment
  calibration: prefer flagging over silently omitting a real issue
  (false negatives are worse than false positives), don't treat an
  assertive claim as automatically wrong, and don't apply an "excessive
  occurrence" bar to checklist items that are objective on a single
  occurrence (e.g. a re-expanded acronym).

## 1.0.1 - 2026-07-22

### Changed
- Expanded the "LaTeX / estrutura" checklist item from a flat 5-bullet list
  into 6 grouped subcategories: Referências cruzadas e rótulos, Listas
  automáticas, Floats (consistência e legendas), Bibliografia e citações,
  Hyperref e links, Idioma e configuração técnica.
- Scoped to checks doable by static `.tex` reading only — no compilation
  step required, since reviewed documents are authored in Overleaf.
- Added explicit guidance to flag every use of `[H]` as an attention point,
  since it can strongly affect the final PDF layout.

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
