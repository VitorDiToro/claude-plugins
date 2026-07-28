# ABNT NBR 10719 — Guia de Revisão Específico

**Complementa** `guia-mestre.md`. Ler o documento mestre antes deste.
**Escopo:** definições específicas de `10719-2015`, `10719-1989` e da adaptação institucional `PUC`.

**Posição na hierarquia:** `10719-2015` = nível 3 · `PUC` = nível 4 · `10719-1989` = nível 5.

> `10719-1989` foi cancelada e substituída. **Nunca usar como exigência.** Serve apenas para reconhecer que uma estrutura antiga é intencional, e como fonte de desempate no nível 5 quando 2015 e PUC são silenciosos.

---

## 1. Estrutura — `10719-2015`

```
PARTE EXTERNA
├── Capa .......................................... opcional
└── Lombada ....................................... opcional  (NBR 12225)

PARTE INTERNA
├── Elementos pré-textuais
│   ├── Folha de rosto ............................ OBRIGATÓRIO
│   ├── Errata .................................... opcional
│   ├── Agradecimentos ............................ opcional
│   ├── Resumo na língua vernácula ................ OBRIGATÓRIO  (NBR 6028)
│   ├── Lista de ilustrações ...................... opcional
│   ├── Lista de tabelas .......................... opcional
│   ├── Lista de abreviaturas e siglas ............ opcional
│   ├── Lista de símbolos ......................... opcional
│   └── Sumário ................................... OBRIGATÓRIO  (NBR 6027)
├── Elementos textuais  (nomenclatura livre, a critério do autor)
│   ├── Introdução ................................ OBRIGATÓRIO
│   ├── Desenvolvimento ........................... OBRIGATÓRIO
│   └── Considerações finais ...................... OBRIGATÓRIO
└── Elementos pós-textuais
    ├── Referências ............................... obrigatório SE houver citações  (NBR 6023)
    ├── Glossário ................................. opcional
    ├── Apêndice .................................. opcional
    ├── Anexo ..................................... opcional
    ├── Índice .................................... opcional  (NBR 6034)
    └── Formulário de identificação ............... obrigatório SE não houver ficha catalográfica
```

**A ordem é normativa.** Elementos opcionais podem ser omitidos; os presentes devem respeitar a sequência.

### 1.1 Pares condicionais

- `Referências` é formalmente opcional, mas torna-se **obrigatória** se o texto contiver qualquer citação.
- `Formulário de identificação` e `ficha catalográfica` são **mutuamente supletivos**: pelo menos um deve existir. Ausência de ambos → `errors.md`, ressalvado o falso positivo 10 do guia mestre (relatório interno de circulação restrita).

---

## 2. Elementos pré-textuais

### 2.1 Capa (opcional)

Primeira capa, conteúdo recomendado: nome e endereço da instituição responsável; número do relatório; ISSN, se houver (NBR 10525); título e subtítulo; classificação de segurança, se houver.

Segunda, terceira e quarta capas: recomenda-se não inserir informação.

`PUC` acrescenta: instituição na margem superior, centralizada, em caixa alta; título em caixa alta e centralizado; subtítulo em caixa baixa.

Classificação de segurança — exemplos de grau: reservado, secreto, confidencial, público. Avaliada pela estimativa do prejuízo que a divulgação não autorizada causaria à entidade responsável.

### 2.2 Folha de rosto (obrigatória)

**Anverso — ordem normativa:**

1. Nome do órgão/entidade que solicitou ou gerou o relatório
2. Título do projeto, programa ou plano ao qual o relatório se vincula
3. Título do relatório
4. Subtítulo, se houver, precedido de dois-pontos (evidencia subordinação ao título)
5. Número do volume, em algarismo arábico, se houver mais de um
6. Código de identificação, se houver — composição sugerida: sigla da instituição + categoria do relatório + data + indicação do assunto + número sequencial na série
7. Classificação de segurança, quando o conteúdo for sigiloso
8. Nome do autor ou autor-entidade (título, qualificação ou função podem ser incluídos)
9. Local (cidade) da instituição — acrescentar sigla da UF em caso de homônimos
10. Ano de publicação, em algarismos arábicos

Regras derivadas:

- Se a instituição que solicitou o relatório é a mesma que o gerou, o nome **não** se repete no campo de autoria.
- Relatório em vários volumes tem **título geral**; cada volume pode ter título específico adicional.

**Verso (ou folha subsequente):**

- Equipe técnica (opcional): comissão de estudo, colaboradores, coordenação
- Ficha catalográfica, obrigatória quando não se usa o formulário de identificação

### 2.3 Errata (opcional)

Inserida logo após a folha de rosto. Composta pela referência completa da publicação seguida da tabela de correções, com as colunas *Folha · Linha · Onde se lê · Leia-se*. Apresentada em papel avulso ou encartado, acrescida ao relatório depois de impresso.

### 2.4 Resumo na língua vernácula (obrigatório)

Conforme NBR 6028. Verificar:

- Parágrafo **único**, sem enumeração de tópicos, sem ilustrações, sem citações
- Sequência: objetivo → metodologia → resultados → conclusões
- Verbo na terceira pessoa
- Extensão de 150 a 500 palavras (`PUC`); `10719-1989` fixava o teto em 500
- `Palavras-chave:` logo abaixo, iniciais minúsculas salvo nomes próprios e científicos, separadas por ponto-e-vírgula
- Corpo 12, espaçamento simples

Relatório em **volumes**: resumo apenas no primeiro. Em **partes**: cada parte tem o seu.

### 2.5 Listas (todas opcionais)

| Lista | Ordenação | Conteúdo de cada linha |
|---|---|---|
| Ilustrações | ordem de aparição no texto | nome designativo + número + travessão + título + página |
| Tabelas | ordem de aparição no texto | `Tabela N – Título ..... página` |
| Abreviaturas e siglas | **alfabética** | sigla + expressão por extenso |
| Símbolos | ordem de aparição no texto | símbolo + significado |

Recomenda-se **lista própria para cada tipo** de ilustração quando houver muitos.

### 2.6 Sumário (obrigatório)

Último elemento pré-textual, conforme NBR 6027.

- Número da seção + título **na mesma grafia do texto** + página
- **Elementos pré-textuais não entram**
- Elementos pós-textuais **entram**
- Tipografia dos itens espelha a hierarquia dos títulos no texto

Verificação item a item entre sumário e corpo é obrigatória. Divergência → `errors.md`.

---

## 3. Elementos textuais

A nomenclatura dos títulos é **livre**. A norma exige a **função** das três partes.

### 3.1 Introdução

Apresenta os objetivos do relatório e as razões de sua elaboração; delimita o tema; expõe os fundamentos teóricos; situa o trabalho em relação a outros.

Critérios de qualidade herdados de `10719-1989` (nível 5 — usar como aviso, não como erro):

- não repetir nem parafrasear o resumo
- não detalhar teoria experimental, método ou resultados
- não antecipar conclusões e recomendações

### 3.2 Desenvolvimento

Parte mais extensa, subdividida em quantas seções forem necessárias. Espera-se:

- **Materiais e métodos** — materiais, procedimentos, condições do experimento; para instrumentos comerciais, marca, modelo e precisão de medida
- **Resultados** — o observado, preferencialmente em tabelas ou gráficos
- **Discussão** — interpretação e confronto com valores esperados ou com a literatura

Minúcias de provas matemáticas ou de procedimentos experimentais migram para apêndice/anexo.

### 3.3 Considerações finais

Sintetiza os resultados, destacando alcance e consequências do estudo. Deduções extraídas dos resultados, apresentadas de forma clara e ordenada.

Critérios de `10719-1989`:

- **não** introduzir dados quantitativos novos
- **não** trazer resultados ainda em disputa
- **recomendações** são declarações concisas de ações futuras derivadas das conclusões
- constituem seção própria, encerrando a parte textual

---

## 4. Elementos pós-textuais

| Elemento | Regras de verificação |
|---|---|
| **Referências** | Alinhadas à **margem esquerda**, não justificadas; separadas entre si por linha em branco de espaço simples. NBR 6023. Não referenciar fonte não citada — havendo interesse, criar seção `Bibliografia recomendada` |
| **Glossário** | Ordem **alfabética**; termos técnicos com as respectivas definições. Na `10719-2015` é **pós-textual** |
| **Apêndice** | Autoral. `APÊNDICE A – TÍTULO`, centralizado, negrito, caixa alta (`PUC`) |
| **Anexo** | Não autoral. `ANEXO A – TÍTULO`, mesma formatação |
| **Índice** | NBR 6034; entradas ordenadas por critério definido, remetendo a páginas ou seções |
| **Formulário de identificação** | Obrigatório se não houver ficha catalográfica; inserido na última página |

**Campos do formulário de identificação:** título e subtítulo · classificação de segurança · nº · tipo de relatório · data · título do projeto/programa/plano · nº · autor(es) · instituição executora e endereço · instituição patrocinadora e endereço · resumo · palavras-chave/descritores · edição · nº de páginas · nº do volume/parte · nº de classificação · ISSN · tiragem · preço · distribuidor · observações/notas.

---

## 5. Regras de apresentação

O que segue combina a `10719-2015` (que em boa parte apenas *recomenda*) com o `PUC`, que dá números concretos. Quando as duas divergem, a `10719-2015` prevalece por ser de nível superior.

### 5.1 Papel e margens

- Formato **A4** (210 × 297 mm), papel branco ou reciclado
- **Anverso:** esquerda e superior 3 cm; direita e inferior 2 cm
- **Verso:** espelhado — direita e superior 3 cm; esquerda e inferior 2 cm
- Pré-textuais iniciam no **anverso**, exceto a ficha catalográfica, no verso da folha de rosto
- Textuais e pós-textuais podem ser impressos em anverso e verso

### 5.2 Fonte e espaçamento

| Item | Regra |
|---|---|
| Fonte do texto | Corpo **12**, tipo **padronizado em todo o documento**; `PUC` sugere Arial ou Times New Roman |
| Corpo reduzido (10) | Citações com mais de 3 linhas, notas de rodapé, paginação, ficha catalográfica, legendas, notas e fontes de ilustrações e tabelas |
| Espaçamento entre linhas | **Simples** — a `10719-2015` recomenda simples, diferentemente do padrão 1,5 de teses e dissertações |
| Recuo de parágrafo | 1,25 cm (`PUC`) |
| Alinhamento | Justificado, exceto referências, à esquerda |

> Espaçamento 1,5 é o desvio institucional mais comum. Aplicado uniformemente, resolve-se no **nível 6** → `warnings.md`.

### 5.3 Paginação

- Pré-textuais contadas a partir da folha de rosto, mas **não numeradas**
- Numeração visível a partir da primeira folha da parte textual, em algarismos arábicos
- Posição: **canto superior direito**, a 2 cm da borda superior, corpo 10 (`PUC`)
- Anverso e verso: número no canto superior **direito no anverso** e **esquerdo no verso**
- Mais de um volume: **sequência única** do primeiro ao último
- Apêndices e anexos: numeração **contínua**, dando seguimento ao texto

### 5.4 Títulos de seção

Além das regras de numeração progressiva do guia mestre (§5.3):

- Títulos de seção primária começam no anverso, na parte superior, separados do texto seguinte por um espaço entre linhas
- Esquema tipográfico **sugerido** pelo `PUC` — é sugestão, não norma; o exigível é hierarquia distinguível e uniforme:

```
1 SEÇÃO PRIMÁRIA          — caixa alta, negrito, 12
1.1 Seção secundária       — caixa baixa, negrito, 12
1.1.1 Seção terciária      — caixa baixa, negrito, itálico, 12
1.1.1.1 Seção quaternária  — caixa baixa, itálico, 12
1.1.1.1.1 Seção quinária   — caixa baixa, sem destaque, 12
```

### 5.5 Títulos sem indicativo numérico

Devem ser **centralizados**; `PUC` acrescenta negrito e caixa alta:

> errata · agradecimentos · lista de ilustrações · lista de tabelas · lista de abreviaturas e siglas · lista de símbolos · resumo · sumário · referências · glossário · apêndice · anexo · índice

Numerar qualquer um desses (`6 REFERÊNCIAS`) contraria a `10719-2015`, 5.4 → `errors.md`, salvo se o padrão de nível superior determinar diferente.

### 5.6 Alíneas

Regras gerais no guia mestre (§5.8). Recuos sugeridos pelo `PUC`: alínea 0,63 cm; subalínea 1,27 cm; sub-subalínea 1,9 cm — deslocamento 0,63 cm.

### 5.7 Citações e notas de rodapé (NBR 10520)

- Notas dentro das margens, separadas do texto por **filete de 5 cm** a partir da margem esquerda, espaço simples
- A partir da segunda linha da mesma nota, alinhar abaixo da primeira letra da primeira palavra, destacando o expoente; sem espaço entre notas; corpo menor
- `PUC`: deslocamento de 0,5 cm, corpo 10
- Sistema de chamada **único** em todo o documento
- Notas limitadas ao mínimo necessário
- **Não** usar rodapé para referências bibliográficas completas

### 5.8 Ilustrações e tabelas

Regras gerais no guia mestre (§5.4 e §5.5). Complementos:

- `PUC`: título centralizado, corpo 12, espaçamento simples; fonte na parte inferior conforme NBR 10520, corpo 10, alinhada às margens da ilustração
- Ilustração autoral: `elaborado pelo próprio autor`, `elaboração própria` ou equivalente
- Quadros e tabelas no mesmo tipo e corpo do texto (12), redutíveis até o limite da legibilidade
- Tabelas conforme as Normas de apresentação tabular do IBGE

---

## 6. Divergências entre as três fontes

Tabela de desempate. Um relatório pode legitimamente seguir qualquer coluna, desde que consistente — mas a resolução obedece à hierarquia: `10719-2015` antes de `PUC`, e `PUC` antes de `10719-1989`.

| Aspecto | `10719-1989` | `10719-2015` | `PUC` |
|---|---|---|---|
| Terminologia das partes | preliminares / texto / pós-liminares | pré-textuais / textuais / pós-textuais | igual a 2015 |
| Capa | parte integrante (1ª a 4ª capas) | **opcional** | opcional |
| Falsa folha de rosto | prevista, opcional | não prevista | não prevista |
| Prefácio / apresentação | previsto, complementar | não previsto | não previsto |
| Fecho da parte textual | `Conclusões e/ou recomendações` | `Considerações finais` | `Considerações finais` |
| Apêndice | não distinguido de anexo | **distinção formal** (autoral × não autoral) | igual a 2015 |
| Posição dos anexos | **antes** de agradecimentos e referências | depois das referências e do glossário | igual a 2015 |
| Agradecimentos | **pós-textual** | **pré-textual** | pré-textual |
| Glossário | pós-textual, após as referências | pós-textual | pós-textual |
| Identificação do relatório | `ficha de identificação`, pós-textual, essencial | `formulário de identificação`, supletivo | igual a 2015 |
| Ficha catalográfica | não prevista | verso da folha de rosto | verso da folha de rosto ou folha subsequente |
| Seções de anexo | numeradas com prefixo de letra (`A.1`, `A.3.1`) | não normatizado | não normatizado |
| Ilustrações de anexo | numeração prefixada (`Tabela A.5`, `Figura B.4`) | não normatizado | não normatizado |
| Paginação | ímpares à direita, pares à esquerda; texto inicia em página ímpar | a partir da parte textual | canto superior direito a 2 cm; espelhada |
| **Legenda de figura** | **abaixo** da figura | **acima** de qualquer ilustração | acima |
| Resumo | até 500 palavras; tradução em trabalhos de grande vulto | conforme NBR 6028 | 150–500 palavras + palavras-chave |
| Volumes e partes | `v.1`, `Parte 1:` com título próprio | volume em arábico na folha de rosto | igual a 2015 |
| Reprodução e impressão | seção própria: papel, tinta preta, encadernação, sem papel colorido | não abordado | papel branco ou reciclado |
| Separador em legendas | — | **travessão** | travessão para quadros; hífen para figuras e tabelas *(inconsistência da própria fonte)* |

### 6.1 Legenda de figura — o caso mais frequente

Documentos gerados em LaTeX com templates antigos frequentemente colocam a legenda **abaixo** da figura, seguindo a `10719-1989` e a prática internacional. Como a `10719-2015` (nível 3) trata do assunto e exige a identificação **acima**, e o `INATEL` pode ou não tratar:

- Se o `INATEL` exigir abaixo → conforme, nada a reportar
- Se o `INATEL` for silencioso e a `10719-2015` governar → contradição com nível 3 → **`errors.md`**, com nota de que a prática segue a edição de 1989 e é amplamente usada
- Reportar sempre de forma agrupada, com contagem, e não figura a figura

---

## 7. Checklist específico da NBR 10719

### 7.1 Estrutura

- [ ] Folha de rosto presente, elementos essenciais na ordem normativa
- [ ] Resumo presente, parágrafo único, objetivo→método→resultados→conclusão, sem citações nem ilustrações
- [ ] Palavras-chave presentes e uniformemente formatadas
- [ ] Sumário presente; sem pré-textuais; com pós-textuais
- [ ] Três funções textuais identificáveis
- [ ] Referências presentes se houver citações
- [ ] Ordem dos elementos respeitada
- [ ] Ficha catalográfica **ou** formulário de identificação presente, quando aplicável
- [ ] Glossário nos **pós-textuais** (posição da 2015)

### 7.2 Formatação

- [ ] A4; margens 3/2 cm, espelhadas em anverso e verso
- [ ] Corpo 12, tipo único; corpo reduzido nas exceções previstas
- [ ] Espaçamento simples, ou desvio uniforme registrado em `warnings.md`
- [ ] Paginação: contagem a partir da folha de rosto, numeração visível a partir da parte textual, canto superior direito, continuidade em apêndices e anexos
- [ ] Títulos sem indicativo numérico centralizados e não numerados
- [ ] Hierarquia tipográfica de títulos uniforme, até a seção quinária
- [ ] Referências alinhadas à esquerda, separadas por linha em branco
- [ ] Notas de rodapé com filete de 5 cm, corpo menor, alinhamento uniforme
- [ ] Ilustrações com identificação acima e fonte abaixo, inclusive as autorais
- [ ] Tabelas com laterais abertas, conforme IBGE; quadros fechados

### 7.3 Conteúdo

- [ ] Introdução não repete o resumo nem antecipa conclusões
- [ ] Objetivos declarados e retomados no fecho
- [ ] Metodologia reproduzível; equipamentos com marca, modelo e precisão
- [ ] Resultados distinguíveis da discussão
- [ ] Discussão confronta resultados com o esperado ou com a literatura
- [ ] Fecho sem dados quantitativos novos e sem resultados em disputa
- [ ] Recomendações, quando presentes, derivadas das conclusões
- [ ] Toda sigla expandida na primeira ocorrência
- [ ] Unidades no SI
- [ ] Detalhamento excessivo deslocado para apêndice
- [ ] Classificação de segurança indicada quando o conteúdo é sigiloso

---

## 8. Falsos positivos específicos desta norma

Além dos gerais do guia mestre:

1. **`Conclusão` ou `Conclusões e recomendações`** no lugar de `Considerações finais` — nomenclatura textual é livre.
2. **Ausência de capa e lombada** — opcionais na `10719-2015`.
3. **Ausência de errata, agradecimentos, glossário, índice e listas** — todos opcionais.
4. **Numeração de seções de anexo com prefixo de letra** (`A.1`, `B.2.1`) — não normatizado na 2015, previsto na 1989; consistente, resolve-se em nível 5 ou 6.
5. **Ilustrações de anexo com numeração prefixada** (`Figura B.4`) — mesma situação.
6. **Resumo sem palavras-chave** quando o documento é anterior à adoção da NBR 6028:2021 — aviso, não erro.
