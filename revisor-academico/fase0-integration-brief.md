# Brief de integração — Fase 0 do `revisor-academico` v2.0

**Para o agente que constrói os scripts da Fase 0.** Este é o **contrato único e autoritativo**
para construir os cinco scripts que faltam + o `build_dossier.py`. Ele **agrega por referência**:
o que já tem dono num arquivo aponta para lá (não recopia); o que ainda não tinha casa em disco
é escrito aqui.

> **Fontes com dono único — leia-as, não as duplique aqui:**
> - **Manifesto / descoberta** (`find_manifest_files`, parser, casos de teste, e a correção
>   `find_tex_files` intocada) → **`spec-manifesto.md`** (autoritativo).
> - **Ancoragem** (`anchor()` / `project_relative()`) → **`skills/revisor-academico/scripts/latex_corpus.py`**
>   (contrato executável; importe-o, nunca formate `arquivo:linha` à mão).
>
> Este Brief é a fonte única para *construir* a Fase 0. O design spec em
> `docs/superpowers/specs/` é registro de design (e é gitignored) — não é contrato.

---

## 1. Confirmação antes de começar (a Task 2 corrigida)

Confirme que você está construindo sobre a **redação corrigida** (spec-manifesto.md §0), não a
antiga. Se estiver na antiga, corrija **agora**, antes de escrever os cinco scripts:

- `find_manifest_files(dir)` é uma **função nova**, manifesto-aware. NÃO existe `find_all_tex_files`.
- `find_tex_files(dir)` fica **intocada e glob-all** — é consumida por `pattern_profile.py`
  (§2/§3), que precisa ver o projeto **inteiro** (senão perde um marcador institucional atrás de
  um `\include` comentado). Não a aliase para o manifesto.
- Os scripts de candidato que já existem (`foreign_terms.py`, `bib_check.py`) **trocam** a
  descoberta de `find_tex_files` para `find_manifest_files(...).files` — **uma linha em cada** —
  para não gerar candidato sobre rascunho órfão.
- `find_manifest_files` retorna `Manifest(files, unresolved, resolved_ok)` — ver spec-manifesto.md §1.

## 2. Regras duras (não-negociáveis)

1. **Toda leitura e ancoragem passa por `latex_corpus`.** Nenhum `open()` próprio; nenhuma
   contagem de linha própria; nenhuma string `arquivo:linha` formatada à mão. Use
   `latex_corpus.read_text`, `strip_comment`, `find_manifest_files` (candidatos §5) e
   `anchor(path, line, root)` (a única forma de produzir uma localização). `root` = o `<dir>` de
   entrada. Verificável por `grep`: um `open(` fora de `latex_corpus`, ou um `:%d` de localização
   à mão, está fora do contrato.
2. **Sinais, não vereditos.** Cada script emite **candidatos localizados**, nunca severidade
   (🔴/🟠/🟡) nem categoria `AV` nem "é erro". Não filtre um candidato por achar que é exceção
   legítima — localize-o e deixe o passe de revisão decidir (ex.: `foreign_terms` só filtra a
   `WHITELIST` de nomes próprios inequívocos). Onde a heurística é aproximada, **diga na saída**.
3. **stdlib apenas.** Sem `pip install`, sem dependência de shell. (`bib_check.py` parseia `.bib`
   à mão de propósito.)
4. **UTF-8 explícito.** No `__main__`, `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
   antes de qualquer `print` — stdout canalizado no Windows assume cp1252 e quebra.
5. **Código e comentários em inglês; saída ao usuário em português.**
6. **Determinismo.** Ordene tudo que for iterado do filesystem; nada de depender da ordem de
   `os.walk` ou de `dict` não-ordenado na saída. (A descoberta de `latex_corpus` já é ordenada.)
7. **Nunca levante em entrada malformada.** Um `.tex`/`.bib` quebrado degrada com o máximo de
   sinal possível, não com traceback (ex.: `bib_check` pula entrada malformada em vez de abortar).

## 3. Pré-requisitos bloqueantes

Dois pré-requisitos de sistema, ambos verificados **no `build_dossier.py`** como primeiro passo
(§7), antes de escrever qualquer coisa. Nenhum é degradável.

| Pré-requisito | Se ausente |
|---|---|
| `python3` (stdlib) | bloqueia (implícito — o pipeline é Python) |
| `hunspell` **+ dicionário `pt_BR`** | bloqueia: `exit 3` + mensagem acionável por plataforma |

A verificação de `hunspell` **não** é `command -v hunspell` — confirme que `pt_BR` é **carregável**
(via `hunspell -D` procurando `pt_BR`), porque o binário sem o dicionário certo produz falsos
positivos em massa. O `spell_check.py` sempre invoca `hunspell -d pt_BR` explícito — nunca o
dicionário padrão. Mensagem de bloqueio traz o comando de instalação por plataforma
(Debian/Ubuntu, Fedora, macOS, Windows).

## 4. Contrato de assinatura (CLI) de cada script

Idêntico ao de `pattern_profile.py`/`text_analysis.py`, para o `build_dossier.py` orquestrar
uniformemente:

```
python3 <script>.py <diretório-do-projeto-latex>
```

- Argumento único: a raiz do projeto (também o `root` de `anchor()`).
- Sem argumento → stderr + `exit 2`; diretório inexistente → stderr + `exit 1`.
- Pré-requisito bloqueante ausente → stderr acionável + `exit 3`.
- **Saída de sinais → stdout**, em Markdown, começando por um `## <título>` de nível 2.
- **Diagnóstico e erro → stderr**, nunca stdout (senão polui o dossiê).

## 5. Os scripts

Sete scripts de candidato (§5 do dossiê). Cada um descobre via **`find_manifest_files(...).files`**
(candidatos sobre o corpus incluído, não sobre órfãos). Nenhum dos dois abaixo é script de
candidato §5, e eles **não** têm a mesma descoberta:
- **`pattern_profile.py`** (§2/§3) fica em **`find_tex_files` (glob-all)** — precisa ver o projeto
  inteiro (senão perde um marcador institucional atrás de um `\include` comentado). Não mudar.
- **`text_analysis.py`** (§4) opera sobre o **manifesto** — porque seus insumos
  `iter_sentences`/`tokenize_words` (em `latex_corpus`) já foram trocados para o manifesto;
  `text_analysis.py` em si não muda a chamada. Revalide sua saída (agora sobre o incluído).

| Script | Estado | Cobre (candidatos) |
|---|---|---|
| `foreign_terms.py` | escrito — **conformar** (discovery + `anchor()`) via plano T1 | anglicismos sem `\textit`, com whitelist de marcas/nomes próprios |
| `crossref_check.py` | **a construir** | `\ref`/`\label` trocados, órfãos, duplicados, com acento; `\cite{chave}` sem entrada no `.bib`; entrada `.bib` nunca citada; apêndice citado e inexistente |
| `bib_check.py` | escrito — **conformar** (discovery + `anchor()`) + `\cite`-sem-entrada, via plano T2 | campo essencial ausente por tipo; DOI ausente **condicional** (só quando outras entradas do mesmo tipo têm DOI); formato implausível (ano, páginas, URL); `\cite` sem entrada no `.bib` |
| `float_check.py` | **a construir** | imagem ausente/caminho quebrado; mesma imagem em figuras distintas; tabela sem `\caption`/`\label`; `tabular` extenso candidato a `longtable`; `\hline`+`booktabs` misturados — com localização |
| `acronym_check.py` | **a construir** | sigla usada antes da expansão; sigla reexpandida; expansão manual; gênero inconsistente |
| `lexicon_check.py` | **a construir** | superlativos/coloquialismos; crase em padrões conhecidos (`à cada`); separador decimal inconsistente; grafias divergentes do mesmo termo |
| `spell_check.py` | **a construir** | ortografia via `hunspell -d pt_BR -t` (ver §3) |

O detalhamento de cada item (o que é erro vs. legítimo) vive no `references/checklist-revisao.md`
do lado skill e é **julgamento do passe**, não do script — o script só localiza o candidato.

## 6. Layout do `dossie.md` (ordem de montagem — contrato)

O `build_dossier.py` concatena nesta ordem fixa; os passes de revisão e a auditoria dependem
dela para localizar cada bloco. Você é dono do **conteúdo** de cada bloco; a **ordem** e os
**cabeçalhos de nível 1** são contrato.

```
# Dossiê de revisão — <nome do projeto>

## §1 Manifesto de arquivos
   - lista incluída = find_manifest_files(dir).files
   - ARQUIVOS ÓRFÃOS (sinal) = find_tex_files(dir) − find_manifest_files(dir).files
   - INCLUDES NÃO RESOLVIDOS = manifest.unresolved  (sinal: typo ou construção não entendida)
   - se manifest.resolved_ok == False: dizer que não houve main claro (diff de órfão não confiável)
## §2 Perfil de padrão              (stdout de pattern_profile.py — glob-all)
## §3 Classificação normativa       (INATEL | NBR10719/PUC | híbrido | nenhum — pattern_profile.py, glob-all)
## §4 Análise textual               (stdout de text_analysis.py)
## §5 Candidatos objetivos          (os 7 scripts, NESTA ordem, cada um sob seu próprio ##:
                                      foreign_terms, crossref_check, bib_check, float_check,
                                      acronym_check, lexicon_check, spell_check)
## §6 Corpus normalizado            (prosa ancorada, de latex_corpus.iter_sentences — manifesto)
## §7 Requisitos externos           (só existe se o usuário forneceu enunciado/rubric: o texto BRUTO;
                                      a extração da lista estruturada é do passe 7, não da Fase 0)
```

Regras de montagem: cada `##` de nível 2 vindo de um script entra **sob** o `## §5`, preservado
como o script emitiu (build_dossier posiciona, não reescreve). Um script sem achado ainda emite
seu `##` + uma linha "(nenhum ...)". Toda âncora, de qualquer origem, é uma string de `anchor()`.

## 7. `build_dossier.py` — orquestração + contrato de stdout

Ordem de execução:

1. **Verificação de pré-requisitos bloqueantes** (§3), ANTES de escrever qualquer coisa. Se
   faltar, `exit 3` + mensagem acionável — nenhum dossiê é escrito.
2. Resolve o manifesto uma vez (`find_manifest_files`) e o glob-all (`find_tex_files`); computa o
   §1 (manifesto + diff de órfãos + `unresolved` + `resolved_ok`).
3. Roda os scripts de sinal e monta o `dossie.md` **em disco**, na ordem §1–§7 (§6).

**Contrato de stdout (crítico — é a razão de o item 1 existir):**

> O `build_dossier.py` **escreve o `dossie.md` em disco** e emite no stdout **apenas uma linha de
> status** (o caminho resolvido do dossiê + código de saída / mensagem de abort). **NUNCA o
> conteúdo do dossiê.**

Por quê: a skill invoca o `build_dossier.py` via `Bash` e **não captura o conteúdo**; ela carrega
o dossiê por um **único `Read`** na Fase 1. Se o `build_dossier.py` despejasse o dossiê no stdout,
o resultado do `Bash` carregaria o dossiê a **preço cheio uma segunda vez** (além do `Read`),
dobrando o custo do item mais caro da revisão e anulando o ganho de cache — o motivo de toda a
arquitetura v2.0. Este é o invariante 8.9 do lado skill.

## 8. Teste de integração — o `dossie.md` de referência

Torne a integração **verificável, não acordada**: monte um projeto-fixture LaTeX pequeno (2–3
`.tex`, 1 `.bib`), versionado, com casos conhecidos de cada checagem (incl. um capítulo órfão
comentado no `main.tex`). Gere o `dossie.md` uma vez, revise à mão, e **congele-o como
referência**. O teste roda o pipeline sobre o fixture e compara com a referência **nas âncoras e
na ordem de seções** (não no texto exato de cada achado — o fraseado é seu e evolui).

Sugestão de comparação: extraia todas as âncoras `\b[\w./-]+:\d+\b` do dossiê e compare o
conjunto, mais a sequência de cabeçalhos `#`/`##`.

> **Nota de validação (não-negociável no merge):** o fixture é smoke test barato; o **portão de
> merge é o pipeline real** — `build_dossier` + os 5 scripts + a skill rodando ponta-a-ponta
> contra o **relatório real** e produzindo uma revisão completa + um `dossie.md` real para revisar
> antes do merge. Fixture e pipeline real medem coisas diferentes; ambos ficam.

## 9. Checklist "pronto para integrar" (por script)

- [ ] Importa `latex_corpus`; nenhum `open()` próprio; nenhuma âncora formatada à mão.
- [ ] Descobre via `latex_corpus.find_manifest_files(dir).files`; toda localização via `anchor(path, line, dir)`.
- [ ] stdlib apenas; `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` no `__main__`.
- [ ] Emite candidatos, não vereditos; heurística aproximada declarada na saída.
- [ ] Saída em stdout (Markdown, sob um `##`); diagnóstico em stderr.
- [ ] CLI: `python3 script.py <dir>`; exits 2/1/3 conforme §4.
- [ ] Não levanta em `.tex`/`.bib` malformado; determinístico.
- [ ] Casos representados no fixture e no `dossie.md` de referência (§8).
