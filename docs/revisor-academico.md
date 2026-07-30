# revisor-academico

Skill que faz **revisão editorial de relatórios acadêmicos em LaTeX**, reconhecendo
padrões normativos nomeados (Inatel, NBR 10719/PUC) quando aplicável, com **fallback ao
padrão interno do documento** quando nenhum é reconhecido. Atua como um editor acadêmico
experiente e exigente — revisa LaTeX, gramática, terminologia, estrutura, rigor
acadêmico e conteúdo técnico — e entrega os resultados como uma **lista de apontamentos
em Markdown**, **sem alterar** os seus arquivos `.tex`.

> A instalação fica no [README](../README.md) (`/plugin install revisor-academico@ditoro-plugins`).
> Este documento é um aprofundamento de **como a skill funciona**.

## O que ela faz de diferente

Pedir "revise este texto" costuma devolver uma resposta corrida no chat. Esta skill produz
uma **saída estruturada, localizada e navegável**, e — deliberadamente — **não corrige** o
documento: quem decide o que acatar é você.

- a revisão passa por **categorias especializadas de mandato disjunto**, uma de cada vez
  (LaTeX, gramática, terminologia, estrutura, conteúdo técnico, referências) — cada categoria
  recebe atenção dedicada, o que reduz a chance de um problema real passar despercebido, mas
  não é garantia de cobertura completa;
- antes de revisar, a skill monta um **dossiê determinístico** do documento: manifesto de
  arquivos, **perfil de padrão** (estilo de citação, especificadores de float, convenção de
  rótulos, etc.) e **sinais objetivos** já localizados (referências cruzadas, bibliografia,
  floats, siglas, ortografia) — extraídos **uma única vez**, para que a revisão parta sempre
  dos mesmos fatos e não divirja sobre qual é a convenção interna do documento;
- opcionalmente, verifica **conformidade com um enunciado, rubric ou norma
  externa**, se você fornecer um na hora do pedido (ver "Conformidade com um
  enunciado ou rubric" abaixo);
- uma pasta `revisao/` com um índice e um arquivo por categoria de problema;
- cada apontamento com **localização exata** (`arquivo:linha`), problema e sugestão;
- itens ordenados por **severidade** e com **ID único** para referência;
- **nenhuma edição** aplicada aos seus arquivos-fonte.

## Pré-requisitos

Antes de revisar, a skill roda uma etapa determinística local (a Fase 0), então o ambiente
precisa de:

- **`python3`** disponível no `PATH`;
- **`hunspell`** + o dicionário **`pt_BR`** (usados na checagem de ortografia).

Sem eles a revisão **aborta logo no início**, com uma mensagem dizendo o que instalar. No
Debian/Ubuntu: `sudo apt-get install hunspell hunspell-pt-br` (no Windows/macOS, instale o
`hunspell` e o dicionário pt-BR antes de pedir a revisão).

## Como usar

Dentro do (ou apontando para) o diretório do seu projeto LaTeX, peça em linguagem natural:

```
Revise este relatório em LaTeX.
```

A skill vai:

1. **Montar um dossiê determinístico** (Fase 0): localizar o arquivo principal
   (`\documentclass`), seguir todos os `\input`/`\include` resolvendo a lista de arquivos uma
   única vez, calcular o perfil de padrão e a **classificação normativa** do documento
   (seleção explícita do usuário ou reconhecimento automático), e rodar as checagens
   objetivas — referências cruzadas, bibliografia, floats, siglas e ortografia
   (`hunspell -d pt_BR`) — todas já ancoradas a `arquivo:linha`. Arquivos `.tex` que existem
   no projeto mas não são alcançados a partir do principal são sinalizados como órfãos.
2. **Ler o dossiê uma vez** e percorrer as **categorias de revisão em sequência** — LaTeX,
   gramática, terminologia, estrutura/rigor acadêmico, conteúdo técnico, referências e
   (opcional) conformidade com requisitos. Cada categoria adjudica os sinais objetivos do
   dossiê (são candidatos, não vereditos — a skill decide caso a caso o que é erro real) e faz
   a leitura semântica que só um revisor consegue (tom, domínio técnico, rigor argumentativo),
   escrevendo direto no arquivo da sua categoria.
3. Reportar o caminho da pasta `revisao/`, a contagem por severidade e as fragilidades mais graves.

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

Nesse caso, a skill embute o texto **bruto** do enunciado no dossiê (§7) e, no passe de
conformidade, extrai dele a lista de requisitos e gera `07_conformidade_requisitos.md`, com os
requisitos não atendidos. Requisitos externos têm
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
    ├── 06_referencias_citacoes.md         # citações e bibliografia (conformidade de referências)
    ├── 07_conformidade_requisitos.md      # (opcional) conformidade com enunciado/rubric fornecido
    └── 08_avisos.md                       # divergências sem norma que as resolva, ou incerteza do revisor
```

### Severidade

Os itens de cada arquivo são ordenados do mais crítico ao menor (exceto os itens `AV`,
que são ordenados por localização no documento, não por severidade — não competem na
mesma escala):

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
| Avisos (Warning) — não são erros            | `AV`    |

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
- **Gramática e ortografia** — acentuação, crase, concordância, regência, pontuação,
  repetição excessiva de palavras/expressões (vício de linguagem), prolixidade,
  homônimos/parônimos confundidos pelo contexto.
- **Terminologia** — grafias divergentes do mesmo termo, acrônimos expandidos e listados.
- **Estrutura e rigor acadêmico** — tom impessoal, superlativos e "marketing" sem
  evidência, coloquialismos, redundância, seções que antecipam a conclusão, seções
  desproporcionais, conformidade com o padrão normativo reconhecido (Inatel/NBR
  10719/PUC), quando aplicável.
- **Conteúdo técnico** — precisão das afirmações, alegações absolutas indevidas, ausência
  de resultados quantitativos, citações a fontes (NIST, RFC, OWASP) sem referência.
- **Referências e citações** — citações `\cite` sem entrada correspondente, DOI ausente,
  campos essenciais ausentes (autor/título/ano/editora), formatação de referências
  conforme o padrão normativo reconhecido.
- **Conformidade com requisitos externos** (opcional) — cobertura de entregáveis exigidos
  por um enunciado/rubric fornecido, critérios de avaliação não atendidos; só se aplica
  quando você fornece esse material na hora do pedido (ver "Conformidade com um enunciado
  ou rubric" acima).
- **Avisos** (`⚠️ AV`, arquivo `08_avisos.md`) — não são erros: divergências de padrão sem
  nenhuma fonte normativa que as resolva, ou pontos que um revisor sinaliza por incerteza,
  para você conferir.

## Padrões normativos e fallback ao padrão do documento

A skill tenta reconhecer, para a parte estrutural/normativa da revisão, se o documento
segue um padrão nomeado — hoje, o template do Inatel ou a NBR 10719 (2015/PUC Minas/1989).
Você pode apontar isso diretamente no pedido ("revise seguindo o padrão Inatel", "revise
pela NBR 10719"), ou deixar a skill reconhecer automaticamente por sinais estruturais do
próprio documento. Quando um padrão é reconhecido, divergências dele viram apontamentos
normais (severidade 🔴/🟠/🟡) — exceto quando o próprio arquivo de referência do padrão já
rotula aquela divergência como "Severidade: AVISO" (ex.: convenção de nomenclatura de
chaves BibTeX não seguida, no guia do Inatel), caso em que ela vira `AV` em vez de erro; quando
nenhuma fonte normativa trata de um aspecto mas o documento é consistente nele, isso vira
um **Aviso** (`AV`), não um erro — é registrado para você conferir, não para corrigir às
cegas.

**Quando nenhum padrão é reconhecido** — documento não bate nem com Inatel nem com NBR
10719/PUC — a skill cai no comportamento clássico: detecta o padrão que o **próprio
documento** adota (numeração, estilo de figuras, formato de citações, grafia de
estrangeirismos) e aponta inconsistências com ele, sem impor nenhuma norma externa. Isso
evita falso-positivos contra convenções locais legítimas de documentos que não seguem
nenhum dos padrões nomeados.

## Nota de desenvolvimento

A skill fixa um **contrato de saída** estruturado: o baseline mostrou que, sem ela, o agente
até encontra os problemas mas entrega tudo **inline no chat**, sem os arquivos navegáveis. A
**v2.0** reescreveu o fluxo para rodar como uma única conversa sequencial dentro do *prompt
cache* do Claude Code, apoiada numa **camada determinística de scripts** (a Fase 0) que monta
o dossiê. Além dos testes unitários dessa camada, ela foi validada **ponta a ponta contra um
relatório real** — porque o portão de qualidade não são os testes, é a revisão do artefato real.
