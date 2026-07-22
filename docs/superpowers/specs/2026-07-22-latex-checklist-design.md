# Design: reorganização da seção "LaTeX / estrutura" do checklist de revisão

## Contexto

A skill `revisor-academico` (`revisor-academico/skills/revisor-academico/SKILL.md`)
tem um checklist de revisão dividido em eixos temáticos. Um deles, **"LaTeX /
estrutura"**, hoje é uma lista plana de 5 bullets (refs cruzadas, listas
automáticas, floats, figuras, bibliografia). Este design expande e reorganiza
só essa subseção — as demais (Gramática, Terminologia, Estrutura acadêmica,
Conteúdo técnico) ficam fora de escopo.

Documentos revisados são desenvolvidos no **Overleaf**; a skill lê os arquivos
`.tex` fonte diretamente, sem acesso a artefatos de compilação (`.log`, `.aux`,
PDF renderizado). Qualquer verificação que dependa de compilar o documento
(warnings de `Overfull \hbox`, "Rerun to get cross-references right",
hifenização visível no PDF) fica fora do escopo — não é possível checá-la só
lendo o código-fonte.

## Decisões

1. **Escopo:** apenas a subseção "LaTeX / estrutura".
2. **Formato:** quebrar a lista plana em **subcategorias com mini-títulos**
   (era uma lista única; passa a ter 6 grupos temáticos), para manter
   navegável à medida que cresce.
3. **Critério de curadoria:** incluir apenas itens verificáveis por leitura
   estática do `.tex`/preâmbulo. Descartar o que exige compilação.
4. **Agrupamento por tipo de verificação, não por tipo de elemento:** bugs de
   rótulo/referência (`\ref`/`\label` órfão, duplicado, frágil) são a mesma
   checagem seja em figura, tabela, equação ou seção — uma única subcategoria
   cobre todos os casos, em vez de repetir a instrução por tipo de float.
5. **Atenção especial a `[H]`:** o especificador `[H]` força a posição exata
   do float e pode alterar fortemente o layout final do PDF; todo uso deve ser
   sinalizado como ponto de atenção, mesmo quando usado "corretamente" (pacote
   `float` presente).

## Checklist final da subseção "LaTeX / estrutura"

```markdown
**LaTeX / estrutura**

**Referências cruzadas e rótulos**
- `\ref` vs `\label` trocados; rótulos definidos e nunca referenciados (órfãos)
  — vale para figuras, tabelas, equações e seções, não só figuras; labels
  duplicados; rótulos com acento/caracteres não-ASCII (frágeis).
- Float ou equação referenciado no texto antes de aparecer na fonte (ordem
  inversa no código-fonte) — para floats isso é um proxy aproximado, já que a
  posição renderizada no PDF pode diferir da posição no `.tex`.
- Apêndices/anexos citados no texto mas nunca referenciados; prefixo de
  numeração (A.1, B.2) mencionado no texto que não corresponde a nenhum
  apêndice definido no documento (checagem exata da numeração compilada fica
  fora do escopo de leitura estática).

**Listas automáticas**
- `\listoffigures`/`\listoftables` duplicadas ou desviadas de função.

**Floats: consistência e legendas**
- Especificadores de posição (`[h]`, `[H]`, `[htbp]`) inconsistentes; pacote
  correspondente (`float`) ausente quando `[H]` é usado. **Sinalizar todo uso
  de `[H]` como ponto de atenção** — força a posição exata do float e pode
  afetar fortemente o layout do PDF final, mesmo quando usado corretamente.
- Mesma imagem reutilizada em figuras distintas; arquivo de imagem ausente ou
  caminho quebrado.
- Tabela sem `\caption`/`\label`, ou com legenda vazia/genérica ("Tabela 1").
- Tabela extensa (muitas linhas) usando `tabular` em vez de `longtable` —
  candidata a estourar a página.
- Estilo de tabela inconsistente: `\hline` manual e `booktabs`
  (`\toprule`/`\midrule`) misturados no mesmo documento.

**Bibliografia e citações**
- Existência de seção de Referências; citações `\cite` sem entrada
  correspondente.
- DOI ausente em referências quando outras entradas do mesmo tipo já têm.
- Citação direta extensa (candidata a >3 linhas renderizadas em ABNT) sem
  recuo/formatação de bloco — linhas no código-fonte são só um indício
  aproximado, a checagem definitiva depende da renderização.

**Hyperref e links**
- `\url`/`\href` com sintaxe malformada, ou link em texto cru sem comando.
- Cor/estilo de link inadequado ao padrão do documento (ex.: cores vivas num
  documento que o padrão indica ser impresso em P&B).

**Idioma e configuração técnica**
- Pacote de idioma (`babel`/`polyglossia`) configurado para idioma diferente
  do texto real do documento — afeta hifenização e nomes automáticos
  ("Capítulo"/"Chapter", "Figura"/"Figure").
```

## Fora de escopo (descartado nesta rodada)

- Warnings de compilação (`Overfull`/`Underfull \hbox`, `undefined reference`,
  `undefined control sequence`) — exigem `.log` de compilação.
- "Rerun to get cross-references right" ignorado — exige `.aux`/recompilação.
- Hifenização incorreta *visível* no PDF renderizado — exige compilar/olhar o
  PDF, não só o `.tex`.
- Notação inconsistente entre símbolos/variáveis em equações — julgado mais
  próximo de "Conteúdo técnico" (precisão/argumentação) do que de um bug de
  LaTeX; pode ser revisitado como adição a essa outra subseção, fora deste
  design.

## Impacto na implementação

Único arquivo afetado: `revisor-academico/skills/revisor-academico/SKILL.md`,
seção `## Checklist de revisão` → substituir os 5 bullets atuais de
"LaTeX / estrutura" pelo bloco com 6 subcategorias acima. Sem mudança de
formato de saída, severidade, IDs ou processo — só o conteúdo do checklist de
apoio ao revisor. Bump de versão da skill (patch, já que é ajuste de conteúdo
de um checklist existente) em `metadata.version`/`updated` no frontmatter e
entrada no `CHANGELOG.md` da skill.
