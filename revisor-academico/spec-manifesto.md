# Especificação — resolução de manifesto no `latex_corpus` (Task 2)

Documento de integração para a Task 2 do plano `revisor-academico` v2.0. Define a descoberta
manifesto-aware que o `latex_corpus` passa a expor, os fixtures de teste derivados de um
`main.tex` real, e — importante — **corrige a redação da decisão 3 da spec**, que descrevia a
Task 2 de forma incompatível com a decisão de sinal-de-órfão tomada depois.

## 0. Correção da decisão 3 (leia primeiro)

A redação anterior da decisão 3 dizia que a Task 2 faria `find_tex_files`/`iter_sentences`
**passarem a honrar o manifesto** — isto é, transformaria as funções de descoberta existentes de
glob-all em manifesto-aware. **Isso está revogado.** Motivo: a decisão de emitir os arquivos
órfãos como sinal no §1 do dossiê (o diff glob-all − manifesto) exige que **as duas descobertas
coexistam** — não há como computar o diff se a glob-all deixou de existir. Além disso, a
classificação normativa (§3) e o perfil estrutural (§2) devem enxergar o projeto **inteiro**,
não só o incluído (confirmado), para não perderem um marcador institucional que viva num arquivo
de borda.

**Redação corrigida da decisão 3:**

> O `latex_corpus` expõe **duas** descobertas, que coexistem:
> - `find_tex_files(dir)` — glob-all, **inalterada** (o comportamento atual de disco). Consumida
>   pelo perfil estrutural (§2, `pattern_profile.py`) e pela classificação normativa (§3).
> - `find_manifest_files(dir)` — **nova**, manifesto-aware: resolve o grafo de inclusão a partir
>   do arquivo principal. Consumida pelo corpus (§6, `iter_sentences`/`tokenize_words` quando
>   operando para candidatos) e pelos scripts de candidato (§5).
>
> O `build_dossier.py` chama ambas e emite `find_tex_files(dir) − find_manifest_files(dir)`
> (diferença de conjuntos, por caminho) como a linha de **arquivos órfãos** do §1.

**Consequência para o handoff:** a Task 2 deixa de ser "mudar o comportamento de
`find_tex_files`" (mudança em função compartilhada → exigiria revalidar `pattern_profile`,
`text_analysis`, `foreign_terms`, `bib_check`) e passa a ser "**adicionar uma função nova**"
(adição pura → nada que já funciona muda de comportamento). Os scripts existentes só mudam se
**escolherem** chamar a função nova — uma troca deliberada de uma linha, não uma regressão por
baixo. Ver §5.

---

## 1. Assinatura e contrato da função nova

```python
def find_manifest_files(directory, main_file=None):
    """Return the ordered list of .tex files reachable from the project's main
    file via \\input/\\include (the 'manifest'), path-resolved and de-duplicated.

    - If main_file is None, auto-detect it: the .tex under `directory` that
      contains both \\documentclass and \\begin{document} (whitespace tolerated,
      e.g. `\\begin {document}`). If none or several
      are found, fall back to find_tex_files(directory) (glob-all) and mark the
      result as un-resolved (see return contract).
    - Comments are stripped (latex_corpus.strip_comment) before scanning each
      line, so an \\include behind % does NOT count as included.
    - \\input and \\include are both recognized; both pull the target into the
      manifest (the \\include page-break semantics are irrelevant to discovery).
    - Paths resolve relative to the project ROOT (standard LaTeX \\input semantics):
      'others/capa' -> '<root>/others/capa.tex' (append '.tex' if absent; honor an
      explicit '.tex' if present). A bare name in a subfolder (\\input{util} inside
      others/) resolves against the ROOT, NOT the sibling others/util.tex -> it goes
      to 'unresolved' (correct: use a root-relative path). Every returned path is
      canonicalized with os.path.normpath, matching find_tex_files, so the dossier §1
      orphan diff (set difference) works even for a non-canonical <dir> ('.', './x').
    - Recurses into each included file (an included file may itself \\input others).
    - A cycle (a includes b includes a) is broken by a visited-set; never loops.
    - An \\input/\\include whose target does not resolve to an existing file is
      NOT included and is collected into a separate 'unresolved' list (a signal:
      either a typo in the path, or a construct the parser did not understand).
    """
```

Retorno (proposta — o formato exato é seu, contanto que exponha os três conjuntos):

```python
Manifest = namedtuple("Manifest", ["files", "unresolved", "resolved_ok"])
#   files       : list[str]  -- .tex incluídos, na ordem de descoberta, de-duplicados
#   unresolved  : list[str]  -- alvos de \input/\include que não casaram com arquivo existente
#   resolved_ok : bool       -- False quando caiu no fallback glob-all (sem main detectável)
```

`resolved_ok=False` é importante: diz ao `build_dossier` que a descoberta não conseguiu resolver
um manifesto (nenhum `main.tex` claro), então o diff de órfãos não é confiável e o §1 deve dizer
isso em vez de listar o projeto inteiro como órfão.

---

## 2. Regras do parser (todas derivadas de um `main.tex` real)

O `main.tex` de referência (projeto Brasil 6G, fornecido pelo usuário) exercita cada regra:

```latex
\documentclass[a4paper,12pt]{article}
\input{others/configuration}
...
\begin{document}
\include{others/capa}
% \include{others/folha_de_rosto}      <- comentado: NÃO incluído
\include{others/historico_de_revisoes}
\include{others/lista_de_figuras}
\include{others/lista_de_tabelas}
\input{others/acronym}
\include{others/indice}
%\include{00_avisos}                     <- comentado: NÃO incluído
\include{01_introducao}
\include{02_panorama}
\include{03_nvidia}
\include{04_poc}
\include{05_status_proximos}
% \include{others/apendice}             <- comentado: NÃO incluído
\bibliographystyle{IEEEtran}
\bibliography{references.bib}
\end{document}
```

Regras que este arquivo fixa:

1. **Comentário vence.** Uma linha `% \include{...}` ou `%\include{...}` (com ou sem espaço
   após o `%`) **não** inclui. Limpe com `strip_comment()` antes de casar. Esta é a regra mais
   crítica: sem ela, `folha_de_rosto`, `00_avisos` e `apendice` seriam incluídos por engano.
2. **Subpasta + sem extensão, relativo ao ROOT.** `\include{others/capa}` resolve para
   `<root>/others/capa.tex`. O parser junta o caminho **ao root** (semântica padrão do `\input`
   do LaTeX — **não** relativo ao arquivo-pai), canonicaliza com `os.path.normpath` (igual à
   `find_tex_files`, para o diff de órfãos funcionar com `<dir>` não-canônico), e adiciona `.tex`
   se ausente.
3. **`\input` e `\include` contam igual.** `\input{others/configuration}` e
   `\input{others/acronym}` entram no manifesto tanto quanto os `\include`.
4. **`\documentclass` fora de `\begin{document}` é o âncora de detecção** do main, não um
   include — não confundir com `\input`.
5. **`\bibliography`/`\bibliographystyle` não são includes de `.tex`** — ignore-os na resolução
   de manifesto (o `.bib` é tratado pelo `bib_check.py`, não pela descoberta de corpus).
6. **Recursão.** `others/configuration.tex` é `\input`-ado no preâmbulo e pode ele mesmo ter
   `\input`s (pacotes, definições em arquivos separados) — recorra.

**Robustez verificada (findings da revisão; testes de regressão em `scripts/test_latex_corpus.py`):**
- Caminhos canonicalizados (`os.path.normpath`) nos **dois** lados do diff — funciona com `<dir>`
  não-canônico (`.`, `./proj`) e não duplica o main num ciclo.
- Main detectado mesmo com espaço: `\begin {document}`.
- `find_tex_files` casa `.tex` **case-insensitive** (`.TEX`/`.Tex` — Windows/macOS).
- Resolução **root-relative** (padrão LaTeX): um nome nu numa subpasta (`\input{util}` dentro de
  `others/`) vai para `unresolved`, não resolve para o irmão — comportamento **correto e
  pretendido** (é a semântica do `\input`; **não** é limitação a "corrigir" com parent-relative
  numa versão futura).

O que este `main.tex` **não** tem, e portanto fica fora de escopo (documentado como limite
conhecido): `\subfile`, `\import`, includes dentro de `\if...\fi`, e macros próprias que
expandam para `\input`. O parser reconhece só `\input`/`\include` literais. Se um projeto futuro
usar um mecanismo indireto, o arquivo logicamente-incluído apareceria como **órfão** no §1 (a
salvaguarda) — sinal para estender o parser, não falha silenciosa.

---

## 3. Fixture de teste (derivado do `main.tex` real)

Reproduza a estrutura do usuário, reduzida, versionada no repositório:

```
fixture-manifest/
├── main.tex                 (o main acima, verbatim ou reduzido preservando os 3 comentados)
├── 01_introducao.tex        (conteúdo mínimo)
├── 02_panorama.tex
├── 03_nvidia.tex
├── 04_poc.tex
├── 05_status_proximos.tex
├── 00_avisos.tex            <- órfão (comentado no main)
├── references.bib
└── others/
    ├── configuration.tex    (pode ter um \input aninhado, p/ testar recursão)
    ├── capa.tex
    ├── folha_de_rosto.tex   <- órfão (comentado no main)
    ├── historico_de_revisoes.tex
    ├── lista_de_figuras.tex
    ├── lista_de_tabelas.tex
    ├── acronym.tex
    ├── indice.tex
    └── apendice.tex         <- órfão (comentado no main)
```

## 4. Casos de teste (asserções, não inspeção visual)

> **Nota de fixture:** o `main.tex` real completo tem **12 incluídos + 3 órfãos**; a fixture de
> unit-test implementada (`scripts/test_latex_corpus.py`) **reduz para 8 incluídos + 3 órfãos =
> 11 `.tex`**, preservando um exemplar de cada regra. Os casos 1 e 8 abaixo citam os números da
> **fixture implementada** (autoritativa).

1. **Manifesto correto.** `find_manifest_files(fixture)` retorna exatamente os **8 incluídos**:
   `main`, `others/configuration`, `others/packages`, `others/capa`,
   `others/historico_de_revisoes`, `others/acronym`, `others/indice`, `01_introducao` (como
   caminhos `.tex` resolvidos). **Não** contém `00_avisos`, `others/folha_de_rosto`,
   `others/apendice`.
2. **Órfãos corretos.** `find_tex_files(fixture) − find_manifest_files(fixture)` = exatamente
   `{00_avisos.tex, others/folha_de_rosto.tex, others/apendice.tex}`.
3. **Comentário respeitado.** Descomentar `%\include{00_avisos}` no fixture move `00_avisos` do
   conjunto órfão para o incluído. (Teste que a regra 1 realmente depende do `%`.)
4. **Subpasta resolvida.** Todo caminho `others/X` do manifesto aponta para um arquivo existente
   sob `others/` — nenhum vira `unresolved`.
5. **Recursão.** Um `\input` dentro de `others/configuration.tex` aparece no manifesto.
6. **Unresolved é sinal, não crash.** Um `\include{others/inexistente}` adicionado ao fixture
   cai em `unresolved`, não levanta, e não entra em `files`.
7. **Fallback sem main.** `find_manifest_files` sobre um diretório sem `\documentclass`+
   `\begin{document}` retorna `resolved_ok=False` e `files == find_tex_files(dir)`.
8. **`find_tex_files` inalterada.** Um teste de regressão confirma que `find_tex_files` ainda
   retorna **todos** os `.tex` do fixture (**11** = 8 incluídos + 3 órfãos), incluindo os 3
   órfãos — prova de que a Task 2 não mudou o comportamento da glob-all.

O caso 8 é o que garante, executavelmente, que a correção da decisão 3 foi respeitada: se algum
dia `find_tex_files` for alterada para honrar o manifesto, o caso 8 falha.

---

## 5. Quem chama o quê (fronteira de consumo)

| Consumidor | Descoberta | Por quê |
|---|---|---|
| `pattern_profile.py` §2 (perfil) | `find_tex_files` (glob-all) | perfil reflete o projeto inteiro; órfão gigante deve aparecer no tamanho-por-arquivo |
| `pattern_profile.py` §9→§3 (classificação normativa) | `find_tex_files` (glob-all) | não perder marcador institucional (`historico_de_revisoes`) por um `%` de borda |
| `text_analysis.py` (§4) | `find_manifest_files` (**decidido: incluído**) | frequência/boilerplate/prolixidade sobre o corpus incluído (o que sai no PDF) |
| `iter_sentences` p/ corpus §6 | `find_manifest_files` | corpus revisável = o que sai no PDF |
| scripts de candidato §5 (`foreign_terms`, `bib_check`, `crossref_check`, ...) | `find_manifest_files` | não gerar candidato sobre rascunho órfão |
| `build_dossier.py` §1 | **ambas** (para o diff) | a diferença é o sinal de órfãos |

**Mudança nos scripts já escritos (`foreign_terms`, `bib_check`):** hoje chamam
`find_tex_files`. Para não gerar candidato sobre órfão, trocam para `find_manifest_files` — **uma
linha em cada**, deliberada e testável, não uma revalidação por comportamento alterado por baixo.
Reforça por que a correção da decisão 3 reduz risco: com `find_tex_files` intocada, essa é a
única mudança nesses dois scripts, e ela é visível no diff.

**Nota sobre `text_analysis.py` (§4) — DECIDIDO: incluído (manifesto).** Frequência lexical,
boilerplate e prolixidade rodam sobre o corpus **incluído**, não o inteiro (prolixidade de um
rascunho órfão não interessa; regra "revisar o que sai no PDF"). O `text_analysis.py` **não muda
de código** — herda o escopo de `iter_sentences`/`tokenize_words`, que já descobrem via
`find_manifest_files`. A tarefa correspondente é **revalidação + um teste** confirmando que um
arquivo órfão não entra em nenhuma das 4 seções — não uma edição de comportamento.

---

## 6. Ordem no plano

Esta função entra na **Task 2**, depois da Task 1 (ancoragem, verify-only) e **antes** de
qualquer script de candidato novo (Tasks 3+), porque todos eles vão descobrir através de
`find_manifest_files`. A Task 2 não toca `find_tex_files`, então não invalida nada da Task 1 nem
o comportamento dos scripts do outro agente — o handoff é "há uma função nova", não "o chão
mudou".
