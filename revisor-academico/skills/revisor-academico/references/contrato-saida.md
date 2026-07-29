# Contrato de saída da revisão

O único contrato de saída da skill. Leia antes de escrever qualquer arquivo de revisão.

## O que a saída É

Crie uma pasta de saída (padrão: `revisao/` na raiz do projeto revisado; se já
existir, use `revisao_AAAA-MM-DD/`). Dentro dela:

1. **`00_INDICE.md`** — sempre presente (modelo abaixo).
2. **Um arquivo `.md` por categoria de problema**, numerado: `NN_<categoria>.md`.

Cada arquivo só existe se houver ao menos um item para ele. **Não crie arquivos vazios.**

Categorias e prefixos de ID:

| Arquivo (exemplo)                          | Tema                                                       | Prefixo ID |
|--------------------------------------------|-----------------------------------------------------------|:----------:|
| `01_correcoes_latex.md`                    | Bugs de LaTeX: refs, labels, listas, floats, imagens      | `C`        |
| `02_gramatica_ortografia.md`               | Gramática, ortografia, crase, concordância, digitação     | `G`        |
| `03_terminologia_consistencia.md`          | Terminologia, acrônimos, padronização de grafia           | `T`        |
| `04_estrutura_conteudo_academico.md`       | Estrutura, redundância, tom, rigor, conformidade normativa | `E`        |
| `05_conteudo_tecnico_<assunto>.md`         | Precisão técnica e argumentação (ex.: segurança)          | `TC`       |
| `06_referencias_citacoes.md`               | Citações, bibliografia, conformidade de referências       | `R`        |
| `07_conformidade_requisitos.md`            | Conformidade com enunciado/rubric/norma externa (só existe se um requisito externo foi fornecido) | `REQ` |
| `08_avisos.md`                             | Divergências de padrão sem fonte normativa que as resolva, ou pontos sinalizados por incerteza — não são erros | `AV` |

## Severidade (ordene os itens de cada arquivo por ela, do mais crítico ao menor)

- 🔴 **Crítico** — erro que quebra a compilação, a numeração ou a coerência do documento.
- 🟠 **Importante** — afeta a qualidade acadêmica, a precisão técnica ou a consistência.
- 🟡 **Menor** — refinamento, estilo, padronização.

Além da severidade, existe uma categoria à parte — `⚠️ Aviso` (arquivo `08_avisos.md`,
prefixo `AV`) — para itens que não são necessariamente erros: uma divergência de padrão
sem nenhuma fonte normativa que a resolva, ou um ponto que o revisor sinaliza por
incerteza, para conferência humana. Itens `AV` não competem com 🔴/🟠/🟡 — são um eixo
diferente (incerteza, não gravidade) — e são ordenados por **localização** no documento, não
por severidade.

## Formato de cada item

Cada item tem um **ID único** = prefixo da categoria + número indexador no arquivo
(`C1`, `C2`, `G1`, `E6`, `AV1`…). Estrutura obrigatória: severidade (ou `⚠️` para
itens `AV`), título, **Local**, **Trecho** (quando houver), **Problema**, **Sugestão**.

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

Separe os itens com `---`. Use `arquivo:linha` reais — todos vêm da âncora do §6 do dossiê
(formato `latex_corpus.anchor()`); não invente linhas nem reabra o `.tex`.

## Numeração: escritor único vs. múltiplos escritores

O desenho é **misto e explícito** — não há consolidador, então a numeração acontece em dois
regimes conforme o arquivo tenha um ou mais escritores:

- **Arquivos de escritor único (01, 02, 03, 06):** o passe dono escreve os itens **com o ID
  final**, numerados por severidade no próprio turno. Sem finalização.
- **Arquivos de múltiplos escritores (04, 05, 08 — e 07 quando existe):** os contribuintes
  (os passes de julgamento e, no futuro, a auditoria B) **apendam candidatos** — o corpo do
  item completo (severidade, título, **Local**, Trecho, Problema, Sugestão) **sem o número do
  ID**, com o **Local** em formato `anchor()`. Append não exige releitura, então não há corrida
  de numeração entre escritores.
- **Finalização (uma vez, após todos os contribuintes de múltiplos escritores terem apendado —
  hoje isso coincide com o turno da auditoria A; quando a auditoria B ligar, roda depois de B
  retornar):** lê os candidatos acumulados de cada arquivo de múltiplos escritores, **ordena,
  deduplica e atribui os IDs de uma vez**, reescrevendo o arquivo:
  - **04, 05, 07:** ordenar **por severidade** (do mais crítico ao menor); IDs `E`/`TC`/`REQ`.
  - **08:** ordenar **por localização**; IDs `AV`.

## Dedup em dois modos (na finalização)

Casar achados equivalentes de dois modos, porque nem todo achado tem um `arquivo:linha` único:

- **Por localização** — itens ancorados (com `arquivo:linha` via `anchor()`) que apontam o
  mesmo ponto e descrevem o mesmo problema fundem-se num item só, mantendo a **severidade mais
  alta**.
- **Por identidade do requisito/elemento** — achados de **ausência** (ex.: "nenhum Abstract em
  nenhum arquivo", "requisito X não atendido") não têm um `arquivo:linha` único; casam pela
  identidade do requisito/elemento a que se referem, não pelo local. Só dedup por localização
  deixaria esses duplicados escaparem.

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

`⚠️ Aviso` (arquivo `08_avisos.md`) é uma categoria à parte, não uma severidade: marca
algo que não é necessariamente um erro — confira se está correto.

## Arquivos desta revisão

| Arquivo | Tema | Severidades |
|---|---|---|
| [01_correcoes_latex.md](01_correcoes_latex.md) | Bugs de LaTeX | 🔴🟡 |
| [08_avisos.md](08_avisos.md) | Avisos (não são erros) | ⚠️ |
| ... | ... | ... |

## Resumo executivo

**Pontos fortes**
- <ponto 1>
- <ponto 2>

**Principais fragilidades a tratar**
1. 🔴 <fragilidade mais grave, com referência ao ID>
2. 🟠 <...>

**Avisos para conferência:** <N> (ver `08_avisos.md`)

---

Detalhes e localização exata em cada arquivo temático.
```

Obtenha data/hora reais executando `date "+%d/%m/%Y às %H:%M:%S"`.

## `references/*.md` são insumo normativo, não contrato de saída

Os arquivos `references/guia-mestre.md` e `references/padrao-*.md` são **insumo normativo**:
use deles apenas a hierarquia de fontes, o algoritmo de decisão e os rótulos de
severidade/aviso. **Ignore qualquer formato de saída que eles contenham** — em especial os
arquivos `errors.md`/`warnings.md` e o bloco "Padrão inferido" descritos no `guia-mestre.md`
§7. O único contrato de saída é **este arquivo**.
