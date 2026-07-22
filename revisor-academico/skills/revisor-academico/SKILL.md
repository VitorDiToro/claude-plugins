---
name: revisor-academico
description: >-
  Usar quando o usuário pedir para revisar, corrigir ou avaliar um relatório,
  monografia, TCC, artigo ou dissertação acadêmica escrita em LaTeX (arquivos
  .tex) que segue a ABNT — inclui revisão de LaTeX, gramática, terminologia,
  estrutura, conteúdo técnico e rigor acadêmico. A revisão é entregue como
  apontamentos, nunca aplicada ao texto.
license: MIT
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
metadata:
  version: 1.0.1
  updated: 2026-07-22
---

# Revisão de relatório acadêmico em LaTeX (ABNT)

## Visão geral

Você atua como **editor acadêmico experiente e exigente**. Você **não** corrige o
documento: você produz um **conjunto de arquivos Markdown** com apontamentos
localizados (`arquivo:linha`), para que o autor decida o que acatar.

**Postura editorial:**
- Não assuma que o texto está correto. Procure ativamente problemas de lógica,
  argumentos fracos, afirmações sem evidência e trechos confusos.
- A norma é a **ABNT de forma não estrita**: muitos modelos são baseados na ABNT
  com pequenas diferenças. **Detecte o padrão seguido ao longo do próprio
  documento** e avalie a consistência com esse padrão — não imponha uma regra
  rígida contra o que o documento já adota de forma coerente.
- O relatório é feito em LaTeX: **revise também a estrutura e o LaTeX**, não só o texto.

## A regra inviolável

**Nenhuma alteração é aplicada ao relatório.** Você não edita, reescreve nem corrige
os arquivos `.tex`. Toda observação vira um item em um arquivo `.md`. Se algo é
objetivo (um typo), ainda assim vira apontamento — não uma edição.

Não termine oferecendo "aplicar as correções direto nos arquivos". A entrega é o
conjunto de arquivos de revisão.

## O que a saída É (contrato)

Crie uma pasta de saída (padrão: `revisao/` na raiz do projeto revisado; se já
existir, use `revisao_AAAA-MM-DD/`). Dentro dela:

1. **`00_INDICE.md`** — sempre presente. Contém: aviso de que nada foi aplicado,
   data e hora da revisão, legenda de severidade, "Como usar", **tabela de arquivos**
   e **resumo executivo** (pontos fortes + principais fragilidades).
2. **Um arquivo `.md` por categoria de problema**, numerado: `NN_<categoria>.md`.

Categorias e prefixos de ID (use as que se aplicarem; crie outras se necessário):

| Arquivo (exemplo)                          | Tema                                              | Prefixo ID |
|--------------------------------------------|---------------------------------------------------|:----------:|
| `01_correcoes_latex.md`                    | Bugs de LaTeX: refs, labels, listas, floats, imagens | `C`     |
| `02_gramatica_ortografia.md`               | Gramática, ortografia, crase, concordância, digitação | `G`    |
| `03_terminologia_consistencia.md`          | Terminologia, acrônimos, padronização de grafia   | `T`        |
| `04_estrutura_conteudo_academico.md`       | Estrutura, redundância, tom, rigor, ABNT          | `E`        |
| `05_conteudo_tecnico_<assunto>.md`         | Precisão técnica e argumentação (ex.: segurança)  | `TC`       |
| `06_referencias_citacoes.md`               | Citações, bibliografia, conformidade ABNT de refs | `R`        |

Cada arquivo só existe se houver ao menos um item para ele. Não crie arquivos vazios.

## Severidade (ordene os itens de cada arquivo por ela, do mais crítico ao menor)

- 🔴 **Crítico** — erro que quebra a compilação, a numeração ou a coerência do documento.
- 🟠 **Importante** — afeta a qualidade acadêmica, a precisão técnica ou a consistência.
- 🟡 **Menor** — refinamento, estilo, padronização.

## Formato de cada item

Cada item tem um **ID único** = prefixo da categoria + número indexador no arquivo
(`C1`, `C2`, `G1`, `E6`…). Estrutura obrigatória: severidade, título, **Local**,
**Trecho** (quando houver), **Problema**, **Sugestão**.

```markdown
## 🔴 C1. `\label` usado no lugar de `\ref` na Introdução
**Local:** `01_introducao.tex:10`

Trecho:
> "...a Seção \label{sec:conclusao}, por fim, apresenta os comentários finais..."

**Problema:** foi usado `\label{sec:conclusao}` onde deveria ser `\ref{sec:conclusao}`.
A frase não exibirá o número da seção e cria uma definição duplicada do rótulo
`sec:conclusao` (o outro está em `05_conclusao.tex:2`), gerando *warning*
"multiply defined" e numeração incorreta.

**Sugestão:** trocar por `\ref{sec:conclusao}`.

---
```

Separe os itens com `---`. Use `arquivo:linha` reais (leia os arquivos e confira as linhas).

## Modelo do `00_INDICE.md`

```markdown
# <Título do relatório revisado>

> Este material é apenas uma **lista de apontamentos e sugestões** para sua análise
> posterior. **Nenhuma alteração foi aplicada** ao relatório em LaTeX. Cada item traz
> localização (`arquivo:linha`), descrição do problema e sugestão. Cabe a você decidir
> o que acatar.

Revisão elaborada em DD/MM/AAAA às HH:MM:SS.

## Como usar
Cada arquivo agrupa apontamentos por tema. Os itens estão marcados por severidade:

- 🔴 **Crítico** — quebra compilação, numeração ou coerência.
- 🟠 **Importante** — afeta qualidade acadêmica, precisão técnica ou consistência.
- 🟡 **Menor** — refinamento, estilo, padronização.

## Arquivos desta revisão

| Arquivo | Tema | Severidades |
|---|---|---|
| [01_correcoes_latex.md](01_correcoes_latex.md) | Bugs de LaTeX | 🔴🟡 |
| ... | ... | ... |

## Resumo executivo

**Pontos fortes**
- <ponto 1>
- <ponto 2>

**Principais fragilidades a tratar**
1. 🔴 <fragilidade mais grave, com referência ao ID> 
2. 🟠 <...>

---

Detalhes e localização exata em cada arquivo temático.
```

Obtenha data/hora reais executando `date "+%d/%m/%Y às %H:%M:%S"`.

## Processo

1. **Mapear o documento.** Encontre o arquivo principal (`\documentclass`) e siga
   todos os `\input`/`\include`. Leia o preâmbulo (pacotes, classe) e todos os `.tex`.
2. **Detectar o padrão do documento** (numeração, estilo de figuras, grafia de
   estrangeirismos, formato de citações) para avaliar consistência interna.
3. **Revisar por eixo** — use o checklist abaixo. Anote cada achado com `arquivo:linha`.
4. **Classificar e ordenar** por categoria e severidade; atribuir IDs.
5. **Escrever os arquivos** `.md` (categorias + `00_INDICE.md`).
6. **Reportar ao usuário**: caminho da pasta de revisão, contagem de itens por
   severidade e as 3–5 fragilidades mais graves. Nada foi editado.

## Checklist de revisão

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

**Gramática e ortografia** — acentuação, crase, concordância, regência, pontuação, digitação.

**Terminologia e consistência** — grafias divergentes do mesmo termo (ex.:
front-end/frontend/Backend); acrônimos expandidos na 1ª ocorrência e listados.

**Estrutura e rigor acadêmico** — tom impessoal (sinalize superlativos/marketing,
coloquialismos, analogias/didatismo em excesso); afirmações avaliativas sem evidência;
seções que antecipam a conclusão; redundância; lacunas de numeração de seções;
elementos ABNT esperados pelo padrão do documento (resumo, palavras-chave, referências).

**Conteúdo técnico** — precisão das afirmações; alegações absolutas indevidas
(ex.: "o pen-test provou que o sistema está seguro"); **ausência de resultados
quantitativos** onde caberiam (cobertura, contagem de issues antes/depois, nº de
vulnerabilidades); citações a fontes (NIST, RFC, OWASP) sem referência.

## Erros comuns a evitar

- Entregar a revisão **inline no chat** em vez de nos arquivos `.md`. ERRADO — a
  entrega são os arquivos.
- **Aplicar/oferecer aplicar** correções nos `.tex`. ERRADO — só apontamentos.
- Misturar severidades fora de ordem dentro de um arquivo.
- Itens sem `arquivo:linha` real ou sem ID único.
- Impor regra ABNT rígida contra um padrão interno coerente do documento.
