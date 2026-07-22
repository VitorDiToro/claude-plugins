# Design: expansão do checklist de conteúdo e dos guardrails de processo

## Contexto

A skill `revisor-academico` (`revisor-academico/skills/revisor-academico/SKILL.md`)
já teve sua seção "LaTeX / estrutura" reorganizada em 6 subcategorias (ver
`docs/superpowers/specs/2026-07-22-latex-checklist-design.md`). As demais
seções do `## Checklist de revisão` — **Terminologia e consistência**,
**Estrutura e rigor acadêmico** e **Conteúdo técnico** — continuam sendo um
único bullet/parágrafo denso cada, mais rasas que a seção de LaTeX. A seção
**Erros comuns a evitar** também cobre só o contrato de entrega (arquivos,
não editar, severidade, ID, ABNT rígida), sem guardrails sobre critério de
julgamento do conteúdo.

Esta rodada de brainstorming é **exploratória** (o autor ainda não terminou
de analisar os resultados de 2 execuções reais da skill em documentos
verdadeiros) — as ideias aqui não vêm de falhas observadas, mas de
completude proativa do checklist. Ficam fora de escopo, para uma rodada
futura informada por evidência real: ciclo de autorrevisão da própria
revisão, modo de re-revisão iterativa entre versões, e deduplicação de
achados repetidos (opções A, B, C descartadas nesta rodada em favor de D).

## Decisões

1. **Escopo:** expandir em subcategorias com mini-títulos (mesmo tratamento
   já aplicado a "LaTeX / estrutura") as 3 seções de conteúdo —
   Terminologia e consistência, Estrutura e rigor acadêmico, Conteúdo
   técnico — e adicionar 3 novos itens a "Erros comuns a evitar".
2. **Critério de sinalização por tipo de item:** alguns itens são
   **objetivos** (sinalizar em qualquer ocorrência, mesmo uma só — ex.:
   sigla reexpandida, superlativos/coloquialismos); outros exigem
   **recorrência real** para serem um problema (ex.: uso excessivo de
   analogias/didatismo). O checklist declara explicitamente qual regra
   vale em cada item, para não deixar isso implícito.
3. **Novo guardrail geral: falso negativo > falso positivo.** Em caso de
   dúvida sobre reportar ou não um achado de conteúdo, o padrão é
   reportar — o autor do documento decide o que acatar, mas só se o
   apontamento existir.
4. **Miscategorização entre arquivos (G/T/E/TC) não é guardrail.** Foi
   avaliada e descartada: se o achado é real, cair no arquivo "errado"
   ainda assim chega ao autor — não é o tipo de erro que compromete a
   revisão, ao contrário de um falso negativo.

## Checklist expandido

### Terminologia e consistência

```markdown
**Terminologia e consistência**

**Grafia e padronização de termos**
- Grafias divergentes do mesmo termo (ex.: front-end/frontend/Backend);
  nomes próprios/produtos grafados de formas diferentes (ex.: "GitHub" vs
  "Github").
- Termos em inglês (anglicismos) sem itálico (`\textit`) — a norma exige
  itálico para estrangeirismos; verificar se **todas** as ocorrências do
  mesmo termo usam `\textit` (não só consistência entre si, mas ausência em
  algum ponto). **Exceção:** nomes próprios e marcas (ex.: "GitHub",
  "Python", "Docker") não entram em itálico mesmo sendo em inglês.

**Acrônimos e siglas**
- Sigla usada antes de ser expandida na 1ª ocorrência; sigla nunca
  expandida.
- Expansão da sigla **digitada manualmente** no texto (ex.: "Interface de
  Programação de Aplicações (API)") em vez de gerida por um comando de
  acrônimo (`\ac{...}` do pacote `acro`/`acronym`). **Sinalizar sempre como
  ponto de atenção, mesmo quando está correta** — é frágil: nada garante
  que a mesma sigla não seja expandida de novo em outro capítulo sem o
  autor perceber, já que não há rastreamento automático.
- Sigla expandida mais de uma vez ao longo do documento (redundante) —
  mais grave quando a expansão é manual (ponto anterior), mas também ocorre
  se o documento usa `\ac`/`acro` de forma inconsistente (macro em alguns
  lugares, texto digitado em outros). **Sinalizar mesmo numa única
  reocorrência** — é objetivo, não exige um padrão recorrente para ser um
  problema.
- Gênero gramatical inconsistente para a mesma sigla (ex.: "a API" numa
  seção, "o API" em outra).

**Nomenclatura técnica consistente**
- Mesmo conceito nomeado de formas diferentes ao longo do texto (ex.: ora
  "modelo", ora "algoritmo", para o mesmo objeto) sem indicar que são
  sinônimos.
- Termo técnico traduzido em algumas ocorrências e mantido em inglês em
  outras (ex.: "framework" vs "arcabouço").

**Unidades e formatos numéricos**
- Separador decimal inconsistente (vírgula vs ponto); unidades grafadas de
  formas diferentes (ex.: "MB" vs "Mb").
```

### Estrutura e rigor acadêmico

```markdown
**Estrutura e rigor acadêmico**

**Tom e voz acadêmica**
- Superlativos/marketing (ex.: "revolucionário", "incrível") e
  coloquialismos — **sinalizar toda ocorrência**, sem exceção.
- Uso **excessivo** de analogias ou didatismo — sinalizar quando o padrão
  se repete ao longo do texto, não uma analogia pontual isolada.
- Uso de primeira pessoa quando o padrão do próprio documento é impessoal
  (ou vice-versa).

**Rigor argumentativo**
- Afirmações avaliativas sem evidência; generalização do resultado de um
  teste/experimento único para uma conclusão universal.
- Seções que antecipam a conclusão antes de ela ser sustentada pelos
  dados.

**Organização e fluxo**
- Redundância de conteúdo entre seções; lacunas ou saltos na numeração de
  seções/capítulos.
- Objetivos declarados na introdução que não são todos retomados na
  conclusão.

**Elementos ABNT esperados**
- Resumo/abstract, palavras-chave, sumário, lista de abreviaturas —
  presentes conforme o padrão que o próprio documento já adota.
```

### Conteúdo técnico

```markdown
**Conteúdo técnico**

**Precisão e alegações**
- Afirmações absolutas indevidas (ex.: "o pen-test provou que o sistema
  está seguro").

**Evidência quantitativa**
- Ausência de resultados quantitativos onde caberiam (cobertura, contagem
  de issues antes/depois, nº de vulnerabilidades).
- Resultado apresentado sem unidade, baseline de comparação ou tamanho de
  amostra.

**Fundamentação e citação técnica**
- Menções a normas/fontes técnicas (NIST, RFC, OWASP, ISO) sem referência
  bibliográfica formal.
- Ferramenta/tecnologia citada sem versão ou contexto de uso, quando isso
  afeta a reprodutibilidade.

**Coerência metodológica**
- Método descrito na seção de metodologia não bate com o que foi de fato
  relatado nos resultados.
- Limitações do estudo evidentes mas não mencionadas.
```

### Erros comuns a evitar (3 novos itens)

```markdown
- **Sub-relatar por complacência** — não deixar de sinalizar um problema
  real por "não querer ser chato". Em caso de dúvida entre reportar ou
  não, reporte: falso negativo é pior que falso positivo — o autor decide
  o que acatar, mas só se o apontamento existir.
- **Confundir afirmação assertiva com afirmação errada** — sinalizar rigor
  argumentativo só quando falta evidência ou a generalização é indevida,
  não simplesmente porque o trecho é direto/categórico.
- **Aplicar critério de "excesso"/"recorrência" a uma ocorrência isolada**,
  quando o item do checklist exige recorrência real (ex.: marcar uma única
  analogia como "uso excessivo de didatismo"). Itens que são objetivos
  mesmo numa única ocorrência (ex.: sigla reexpandida) não entram nessa
  regra.
```

## Fora de escopo (descartado nesta rodada)

- **Ciclo de autorrevisão (QA da própria revisão)** — etapa extra que relê
  os próprios apontamentos antes de entregar, buscando duplicatas/falsos
  positivos.
- **Modo de re-revisão iterativa** — comparar uma nova execução com uma
  `revisao_AAAA-MM-DD/` anterior para reportar só o que mudou.
- **Deduplicação/agrupamento de achados repetidos** — agrupar ocorrências
  do mesmo problema em um item só, em vez de um item por ocorrência.
- **Miscategorização entre categorias (G/T/E/TC)** como guardrail — avaliado
  e descartado (decisão 4 acima): não é um erro que compromete a revisão.

Essas quatro ideias devem ser revisitadas depois que o autor terminar de
analisar os 2 documentos já revisados — evidência real deve informar qual
delas (se alguma) vale a pena, em vez de especulação.

## Impacto na implementação

Único arquivo afetado: `revisor-academico/skills/revisor-academico/SKILL.md`,
seção `## Checklist de revisão`:
- Substituir o bullet único de "Terminologia e consistência" pelo bloco de
  4 subcategorias acima.
- Substituir o bullet único de "Estrutura e rigor acadêmico" pelo bloco de
  4 subcategorias acima.
- Substituir o bullet único de "Conteúdo técnico" pelo bloco de 4
  subcategorias acima.
- Acrescentar os 3 novos itens a `## Erros comuns a evitar`.

Sem mudança de formato de saída, severidade, IDs ou processo — só o
conteúdo do checklist e dos guardrails de apoio ao revisor. Segue o mesmo
padrão de release já usado (bump de versão minor, `CHANGELOG.md`,
`README.md`) descrito em `docs/development.md`.
