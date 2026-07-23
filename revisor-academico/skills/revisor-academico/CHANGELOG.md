# Changelog

All notable changes to the `revisor-academico` skill are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com);
the `metadata.version` / `metadata.updated` fields in `SKILL.md` frontmatter point to the latest entry.

## 1.3.0 - 2026-07-22

### Added
- Optional "Conformidade com requisitos externos" checklist category (prefix `REQ`, file
  `07_conformidade_requisitos.md`): when the user provides an external assignment brief, rubric,
  or norm in the invocation itself (pasted text or a referenced file), the skill extracts a
  structured requirement list once (step 1) and shares it with both reviewers and the
  consolidator — same "compute once, share" pattern as the file list and pattern profile. Judging
  whether the document satisfies each requirement remains independent per-reviewer work.
- With no external requirement provided, behavior is unchanged from 1.2.1 — this is purely
  additive.

### Changed
- External requirements now explicitly take priority over the "don't impose rigid rules against
  the document's own coherent internal pattern" guardrail when the two conflict.

## 1.2.1 - 2026-07-22

### Added
- `scripts/perfil-padrao.sh` — extracts a "perfil de padrão do documento" (7 objective facts:
  float specifiers, acronym mechanism, citation style, label prefix convention, table style,
  language config, quote style) from a LaTeX project via cheap `grep`/`sed` scans, no semantic
  reading.

### Changed
- `## Processo` step 1 now runs this script once and shares its output with both reviewers and
  the consolidator (steps 2-3), instead of each independently (and potentially inconsistently)
  rediscovering the same objective facts. Semantic judgments (tone, italics-for-foreign-terms,
  technical domain, argumentative rigor) are explicitly excluded from the profile and remain
  independent per-reviewer, where redundancy across the 2 reviewers still has value.

## 1.2.0 - 2026-07-22

### Changed
- Replaced the single-pass review process with a default 2-reviewer + 1-consolidator flow:
  Revisor 1 (`sonnet`, effort `xhigh`) and Revisor 2 (`opus`, effort `xhigh`) independently
  review the whole document in parallel, writing raw findings to scratch files; a consolidator
  (`opus`, effort `max`) unions their findings, resolves severity conflicts to the higher value,
  re-reads the source only for findings the two reviewers contradict each other on, and writes
  the final output.
- Added `Agent` to `allowed-tools` to support the new subagent dispatch.
- "Visão geral" now documents this as two independent reviews consolidated — a probabilistic
  mitigation of false negatives, not a guarantee of full coverage.
- The final report temporarily includes both reviewers' scratch-file paths, for inspection while
  this flow is validated in real use (planned for removal in a future release).

Motivated by `resultados/comparacao_v1.0.0_vs_v1.1.0.md`, which showed two independent runs over
the same document catching partially different real issues, even within a checklist section
that hadn't changed between the compared versions.

## 1.1.1 - 2026-07-22

### Changed
- Converted the 5 top-level "Checklist de revisão" categories (LaTeX / estrutura, Gramática e
  ortografia, Terminologia e consistência, Estrutura e rigor acadêmico, Conteúdo técnico) from
  bold text to `###` headings, for consistent Markdown structure and easier navigation.
  Subcategories remain in bold.
- Expanded "Gramática e ortografia" from a single dense bullet into 6 subcategories: Crase,
  Concordância verbal e nominal, Regência verbal e nominal, Ortografia e acentuação, Pontuação
  e espaçamento, Digitação e resíduos de edição.

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
