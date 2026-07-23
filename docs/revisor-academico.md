# revisor-academico

Skill que faz **revisão editorial de relatórios acadêmicos em LaTeX** seguindo a **ABNT
de forma não estrita**. Atua como um editor acadêmico experiente e exigente — revisa
LaTeX, gramática, terminologia, estrutura, rigor acadêmico e conteúdo técnico — e entrega
os resultados como uma **lista de apontamentos em Markdown**, **sem alterar** os seus
arquivos `.tex`.

> A instalação fica no [README](../README.md) (`/plugin install revisor-academico@ditoro-plugins`).
> Este documento é um aprofundamento de **como a skill funciona**.

## O que ela faz de diferente

Pedir "revise este texto" costuma devolver uma resposta corrida no chat. Esta skill produz
uma **saída estruturada, localizada e navegável**, e — deliberadamente — **não corrige** o
documento: quem decide o que acatar é você.

- a revisão é composta por **duas revisões independentes, consolidadas num
  único resultado** — reduz a chance de um problema real passar despercebido,
  mas não é garantia de cobertura completa;
- os dois revisores compartilham um **perfil de padrão do documento** (estilo
  de citação, especificadores de float, convenção de rótulos, etc.), extraído
  uma única vez, para não divergirem sobre qual é a convenção interna do
  documento;
- opcionalmente, verifica **conformidade com um enunciado, rubric ou norma
  externa**, se você fornecer um na hora do pedido (ver "Conformidade com um
  enunciado ou rubric" abaixo);
- uma pasta `revisao/` com um índice e um arquivo por categoria de problema;
- cada apontamento com **localização exata** (`arquivo:linha`), problema e sugestão;
- itens ordenados por **severidade** e com **ID único** para referência;
- **nenhuma edição** aplicada aos seus arquivos-fonte.

## Como usar

Dentro do (ou apontando para) o diretório do seu projeto LaTeX, peça em linguagem natural:

```
Revise este relatório em LaTeX.
```

A skill vai:

1. Localizar o arquivo principal (`\documentclass`) e seguir todos os `\input`/`\include`,
   resolvendo a lista de arquivos uma única vez, e calcular o perfil de padrão do documento.
2. Despachar **2 revisores independentes, em paralelo** — cada um usa o perfil de padrão
   compartilhado para os fatos objetivos, detecta de forma independente os aspectos que
   exigem leitura semântica (tom, domínio técnico, rigor argumentativo), e revisa por todo
   o checklist, sem saber da existência do outro.
3. Despachar um **consolidador** que une os achados dos dois revisores, resolve
   divergências de severidade e escreve a pasta `revisao/` final.
4. Reportar o caminho, a contagem por severidade e as fragilidades mais graves.

### Conformidade com um enunciado ou rubric

Se você tiver um enunciado de atividade, rubric de avaliação ou norma específica do seu
curso/instituição, cole o texto (ou aponte para o arquivo) **na mesma mensagem** em que pedir
a revisão:

```
Revise este relatório em LaTeX. O enunciado da atividade exige: (1) cobertura das
quatro aplicações integradas (LiDAR, coleira, armadilha, controlador de cargas);
(2) Resumo e Abstract; (3) resultados quantitativos de todas as métricas de rede
testadas em cada aplicação.
```

Nesse caso, a skill extrai uma lista de requisitos do texto fornecido (uma única vez,
compartilhada pelos 2 revisores e pelo consolidador) e passa a gerar também
`07_conformidade_requisitos.md`, com os requisitos não atendidos. Requisitos externos têm
prioridade sobre o padrão interno do documento — se o enunciado pede algo que o documento não
faz, isso é um apontamento real, mesmo que o documento seja consistente consigo mesmo sobre
não fazer aquilo. Sem enunciado/rubric mencionado, o comportamento é o mesmo de sempre — este
recurso é inteiramente opcional.

## Formato da saída

```
seu-projeto/
└── revisao/
    ├── 00_INDICE.md                       # índice, data/hora, "como usar", resumo executivo
    ├── 01_correcoes_latex.md              # refs, labels, listas, floats, imagens
    ├── 02_gramatica_ortografia.md         # gramática, ortografia, crase, concordância
    ├── 03_terminologia_consistencia.md    # grafia de termos, acrônimos
    ├── 04_estrutura_conteudo_academico.md # tom, superlativos, rigor, estrutura
    ├── 05_conteudo_tecnico_<assunto>.md   # precisão técnica e argumentação
    ├── 06_referencias_citacoes.md         # citações e bibliografia (ABNT)
    └── 07_conformidade_requisitos.md      # (opcional) conformidade com enunciado/rubric fornecido
```

### Severidade

Os itens de cada arquivo são ordenados do mais crítico ao menor:

- 🔴 **Crítico** — quebra a compilação, a numeração ou a coerência do documento.
- 🟠 **Importante** — afeta a qualidade acadêmica, a precisão técnica ou a consistência.
- 🟡 **Menor** — refinamento, estilo, padronização.

### Identificadores

Cada item tem um **ID único** = prefixo da categoria + índice (`C1`, `G2`, `TC1`…), para
você referenciar facilmente ao decidir o que corrigir.

| Categoria                         | Prefixo |
|-----------------------------------|:-------:|
| Correções de LaTeX                | `C`     |
| Gramática e ortografia            | `G`     |
| Terminologia e consistência       | `T`     |
| Estrutura e conteúdo acadêmico    | `E`     |
| Conteúdo técnico                  | `TC`    |
| Referências e citações            | `R`     |
| Conformidade com requisitos externos (opcional) | `REQ` |

### Exemplo de apontamento

```markdown
## 🔴 C1. `\label` usado no lugar de `\ref` na Introdução
**Local:** `01_introducao.tex:10`

Trecho:
> "...a Seção \label{sec:conclusao}, por fim, apresenta os comentários finais..."

**Problema:** foi usado `\label{sec:conclusao}` onde deveria ser `\ref{sec:conclusao}`.
A frase não exibirá o número da seção e cria um rótulo duplicado ("multiply defined").

**Sugestão:** trocar por `\ref{sec:conclusao}`.
```

## O que a skill revisa

- **LaTeX / estrutura** — referências cruzadas (`\ref`/`\label`), rótulos duplicados ou
  não-ASCII, listas automáticas (`\listoffigures`/`\listoftables`), floats, figuras que
  reutilizam a mesma imagem, arquivos de imagem ausentes, bibliografia.
- **Gramática e ortografia** — acentuação, crase, concordância, regência, pontuação.
- **Terminologia** — grafias divergentes do mesmo termo, acrônimos expandidos e listados.
- **Estrutura e rigor acadêmico** — tom impessoal, superlativos e "marketing" sem
  evidência, coloquialismos, redundância, seções que antecipam a conclusão, elementos
  ABNT esperados.
- **Conteúdo técnico** — precisão das afirmações, alegações absolutas indevidas, ausência
  de resultados quantitativos, citações a fontes (NIST, RFC, OWASP) sem referência.
- **Referências e citações** — citações `\cite` sem entrada correspondente, DOI ausente,
  conformidade ABNT de referências.
- **Conformidade com requisitos externos** (opcional) — cobertura de entregáveis exigidos
  por um enunciado/rubric fornecido, critérios de avaliação não atendidos; só se aplica
  quando você fornece esse material na hora do pedido (ver "Conformidade com um enunciado
  ou rubric" acima).

## Por que "ABNT não estrita"

Muitos relatórios seguem modelos baseados na ABNT, mas com pequenas diferenças de
instituição para instituição. Em vez de cobrar a norma ao pé da letra, a skill **detecta o
padrão que o próprio documento adota** (numeração, estilo de figuras, formato de citações,
grafia de estrangeirismos) e aponta **inconsistências com esse padrão** — o que é mais útil
e evita falso-positivos contra convenções locais legítimas.

## Nota de desenvolvimento

A skill foi construída com o `superpowers:writing-skills` (ciclo RED/GREEN/REFACTOR). O
baseline mostrou que, sem a skill, o agente encontra os problemas mas entrega tudo **inline
no chat**, sem os arquivos estruturados. A skill fixa o **contrato de saída** e foi validada
com teste em subagente sobre uma amostra LaTeX com problemas plantados.
