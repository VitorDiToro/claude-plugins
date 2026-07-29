# Changelog

All notable changes to the `revisor-academico` skill are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com);
the `metadata.version` / `metadata.updated` fields in `SKILL.md` frontmatter point to the latest entry.

## 2.0.0 - 2026-07-29

> **⚠️ BREAKING — leia antes de atualizar da v1.7.0.** Dois contratos de execução mudaram:
>
> 1. **Execução: paralela → sequencial de modelo fixo.** A revisão deixa de despachar 2
>    revisores em paralelo (`sonnet` + `opus`) + consolidador e passa a rodar como **uma única
>    conversa sequencial** dentro do prompt cache, com **modelo e effort fixos: Opus 4.8 ·
>    xhigh**, do início ao fim. Trocar modelo/effort no meio, `/compact`, ou negar uma tool
>    invalidam o cache e recomputam a conversa — ver "Invariantes de cache" no `SKILL.md`.
> 2. **Novo pré-requisito bloqueante: `hunspell` + dicionário `pt_BR`.** Sem eles a Fase 0
>    **aborta** (no mesmo nível de `python3`, que já era obrigatório). Especialmente no Windows,
>    instale-os **antes** de revisar — senão a revisão para logo no início.
>
> O **contrato de saída é preservado integralmente** (pasta `revisao/`, `00_INDICE.md`, um
> arquivo por categoria, formato de item, severidades 🔴/🟠/🟡 + `AV`). O que muda é *como* a
> revisão é produzida, não o formato do resultado.

### Changed
- **Fluxo reescrito para operar dentro do prompt cache do Claude Code**, sequencial: uma
  conversa, 7 passes especializados de mandato disjunto + auditoria A cacheada, substituindo os
  2 revisores paralelos + consolidador. O documento é lido a preço cheio **uma vez** (o dossiê),
  depois relido a ~10% via cache. **Consolidador removido** — com mandatos disjuntos não há o
  que unir, casar por local, nem renumerar entre passes.
- Numeração de ID mista e explícita: arquivos de escritor único (01/02/03/06) numeram com ID
  final no próprio turno; as categorias de julgamento (04/05, e 07 quando existe) e o transversal
  `08` recebem candidatos sem ID e são **finalizados uma vez** (ordena → dedup → numera), com
  dedup em **dois modos** (localização + identidade do requisito/elemento).
- `SKILL.md` enxugado (~9k → ~3k tokens): checklist e contrato de saída extraídos para
  `references/` (`checklist-revisao.md` com TAGs de passe-dono; `contrato-saida.md`). O §4
  (calibração) do `guia-mestre.md` migrou para o `pattern_profile.py` — a classificação normativa
  agora vem pronta no §3 do dossiê e **não deve ser recalculada** pelo agente.

### Added
- `latex_corpus.anchor()` / `project_relative()` — contrato executável de ancoragem
  (`arquivo:linha` 1-based, relativo à raiz, forward slashes), com cobertura de testes
  (`test_latex_corpus.py`, stdlib `unittest`).
- `latex_corpus.find_manifest_files()` — descoberta **manifesto-aware** (segue `\documentclass`
  + `\input`/`\include`, comentários respeitados, recursiva, cycle-safe, com fallback glob-all).
  Coexiste com `find_tex_files` (glob-all, **inalterada**): a camada de sinais e o corpus passam
  a ignorar rascunhos `.tex` não referenciados, enquanto o perfil/classificação continuam vendo
  o projeto inteiro; os arquivos órfãos viram sinal no §1 do dossiê.
- Fase 0 determinística (camada de scripts + `build_dossier.py`) que monta um dossiê único, com
  verificação bloqueante de `python3` e `hunspell`/`pt_BR`; ortografia via `hunspell -d pt_BR`.
- "Invariantes de cache" e "Orçamento de contexto" documentados no `SKILL.md`; medição de cache
  via `current_usage`.

### Deferred
- **Auditoria B** (subagente num segundo modelo, auditando só as categorias de julgamento) fica
  totalmente especificada e **deferida**, com gatilho medido por `current_usage` (folga de quota
  + buracos visíveis na auditoria A). Ver o spec de design v2.0.

## 1.7.0 - 2026-07-28

### Added
- Nova categoria de saída **Warning** (`08_avisos.md`, prefixo `AV`): divergências de
  padrão sem nenhuma fonte normativa que as resolva, ou pontos que um revisor sinaliza
  por incerteza — não são erros, ficam à parte da severidade 🔴/🟠/🟡, para conferência
  humana.
- Arquivos de referência normativa em `references/` (`guia-mestre.md`,
  `padrao-nbr10719.md`, `padrao-inatel.md`, renomeados de `modelos_ref/`): hierarquia de
  precedência de fontes (norma institucional explícita > Inatel > NBR 10719:2015 > PUC
  Minas > NBR 10719:1989 > padrão interno do documento) e algoritmo de decisão por
  aspecto, usados para classificar erro (severidade normal) vs. Warning (nível 6 —
  nenhuma fonte trata do aspecto, documento consistente).
- Sinais de calibração de padrão institucional (Histórico de Atualizações, Conclusão,
  Considerações finais, Resumo, Glossário, Folha de rosto, `printonlyused`) em
  `scripts/pattern_profile.py`, para reconhecer automaticamente se o documento segue
  Inatel ou NBR 10719/PUC — computado uma única vez, compartilhado pelos 2 revisores e
  pelo consolidador.
- Seleção explícita de padrão pelo usuário no próprio pedido ("revise seguindo o padrão
  Inatel", "revise pela NBR 10719", "revise pela ABNT") — pula a calibração automática.

### Changed
- A postura "ABNT de forma não estrita" deixa de ser o comportamento padrão único: a
  skill agora tenta reconhecer um padrão normativo nomeado antes de recorrer ao padrão
  interno do documento; o padrão interno continua sendo o fallback quando nenhum padrão
  conhecido é identificado.
- O bullet "Elementos ABNT esperados" é substituído por uma checagem estrutural mais
  precisa, dirigida pelos arquivos de `references/`, quando um padrão é reconhecido.

## 1.6.0 - 2026-07-24

### Added
- Sinal de **frases repetidas ou quase-repetidas** (boilerplate) e de **frases mais longas**
  (indício de prolixidade) na camada de sinais objetivos, ancorados a `arquivo:linha`. O item de
  "vício de linguagem" passa a ter respaldo de script real (não só frequência de palavra), o item de
  "prolixidade" ganha um sinal de apoio, e o item de "redundância entre seções" referencia o sinal
  de boilerplate.

### Changed
- Camada de sinais objetivos reescrita de bash para **Python 3 (apenas biblioteca padrão, sem
  dependências)**, sobre um módulo de corpus compartilhado (`latex_corpus.py`): `perfil-padrao.sh` →
  `pattern_profile.py` (paridade de saída verificada) e `frequencia-lexical.sh` → `text_analysis.py`.
  Motivação dupla: consertar o travamento (abaixo) e a **portabilidade para Windows** (os scripts
  `.sh` não rodam no Windows sem Git Bash/WSL; `python3` roda nos dois). Requer `python3` no ambiente.

### Fixed
- `frequencia-lexical.sh` travava em documentos de tamanho real (filtro de subsunção O(n²) sobre
  dezenas de milhares de n-gramas; não terminava em 90s). A versão Python aplica a subsunção só entre
  os candidatos do top-N e conclui em segundos.

## 1.5.0 - 2026-07-23

### Added
- 4 new checklist items, spanning existing categories (no new output file/prefix): a
  "Referência bibliográfica sem campo essencial" bullet under "Bibliografia e citações" (`R`);
  a "seção/capítulo desproporcional" bullet under "Organização e fluxo" (`E`), backed by a new
  "Tamanho por arquivo" (raw word count) section in `scripts/perfil-padrao.sh`; and two new
  "Gramática e ortografia" (`G`) subsections, "Prolixidade e frases excessivamente longas" and
  "Homônimos e parônimos confundidos pelo contexto" — both reviewer judgment, no script.

## 1.4.0 - 2026-07-22

### Added
- "Repetição excessiva de palavras ou expressões (vício de linguagem)" checklist item under
  "Gramática e ortografia": a new standalone script, `scripts/frequencia-lexical.sh`, computes
  word-frequency and 2-4-word expression-frequency counts (with a subsumption filter that drops
  a shorter n-gram when a longer one fully and exactly explains all of its occurrences) via
  cheap structural scanning, no semantic reading. Its output is shared with both reviewers and
  the consolidator the same way as the existing pattern profile — computed once in step 1.
  Judging whether a high-frequency word/expression is a language vice (vs. a legitimate,
  recurring domain term) remains independent per-reviewer work.

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
