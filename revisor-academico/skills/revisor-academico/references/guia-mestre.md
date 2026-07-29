# Guia de Revisão de Relatórios Técnicos — Documento Mestre

**Público-alvo:** agente de IA encarregado de revisar relatórios técnicos.
**Escopo deste arquivo:** hierarquia de precedência, algoritmo de decisão, núcleo de regras comum a todos os padrões e formato dos arquivos de saída.

## Documentos do conjunto

| Arquivo | Conteúdo |
|---|---|
| `guia-mestre.md` | **Este arquivo.** Regras de decisão e o que é comum a todos os padrões. Ler sempre, primeiro. |
| `padrao-nbr10719.md` | Definições específicas da ABNT NBR 10719 (edições 2015 e 1989) e da adaptação institucional da PUC Minas. |
| `padrao-inatel.md` | Definições específicas do template/modelo do Inatel. |

---

## 1. Siglas das fontes

| Sigla | Fonte |
|---|---|
| `10719-2015` | ABNT NBR 10719:2015 — *Informação e documentação — Relatório técnico e/ou científico — Apresentação*. 4ª ed., incorpora a Emenda 1 de 25.05.2015. **Norma vigente.** |
| `10719-1989` | ABNT NBR 10719:1989 — *Apresentação de relatórios técnico-científicos*. Edição cancelada e substituída. **Referência histórica.** |
| `PUC` | PUC Minas / Sistema Integrado de Bibliotecas — *Orientações para elaboração de relatório técnico e/ou científico conforme a NBR 10719:2015*. 6. ed., 2025. Adaptação institucional; supre lacunas de formatação da norma. |
| `INATEL` | Template/modelo de relatório técnico do Instituto Nacional de Telecomunicações. |

Ao citar uma regra em `errors.md` ou `warnings.md`, usar sempre a sigla + a localização dentro da fonte. Exemplo: `10719-2015, 5.8` ou `INATEL, estrutura pré-textual`.

---

## 2. Hierarquia de precedência

Ordem **obrigatória** de consulta. A primeira fonte que trata do aspecto em análise é a **fonte governante**.

```
1. Padrão institucional explícito ....... se informado/fornecido pelo usuário
2. INATEL ............................... template do Inatel
3. 10719-2015 ........................... norma ABNT vigente
4. PUC .................................. adaptação institucional PUC Minas
5. 10719-1989 ........................... norma ABNT histórica
6. Padrão implícito consistente do documento .... último recurso
```

### 2.1 Consequências do nível 6

Quando a resolução de um aspecto **chega ao nível 6** — ou seja, nenhuma das fontes 1 a 5 trata do assunto, e o documento adota uma convenção própria de forma consistente:

> Registrar em **`warnings.md`**: o padrão é divergente em relação ao conjunto normativo, mas **possivelmente correto**.

### 2.2 Incoerência com níveis superiores

Quando o padrão do documento **contradiz** uma fonte governante dos níveis 1 a 5:

> Registrar em **`errors.md`**, informando **por que** é possivelmente um erro: qual fonte foi contrariada, qual o dispositivo específico e qual o impacto.

### 2.3 Inconsistência interna

Quando o documento **não tem** padrão consistente para o aspecto (aplica regras diferentes em ocorrências equivalentes):

> Registrar em **`errors.md`**. Inconsistência interna é sempre erro, independentemente de qualquer norma.

---

## 3. Algoritmo de decisão

Executar para **cada aspecto verificável** do documento.

```
PARA cada aspecto:

  A) O documento é internamente consistente nesse aspecto?
     NÃO ──> errors.md  (motivo: inconsistência interna)
              listar todas as ocorrências divergentes
     SIM ──> segue

  B) Identificar a FONTE GOVERNANTE:
     percorrer a hierarquia 1 → 5 e parar na primeira fonte que trata do aspecto.

  C) Alguma fonte de 1 a 5 trata do aspecto?
     NÃO ──> nível 6: o padrão do documento governa
              ──> warnings.md  (divergente, possivelmente correto)
     SIM ──> segue

  D) O padrão do documento é coerente com a fonte governante?
     SIM ──> conforme; nada a reportar
     NÃO ──> errors.md
              informar: fonte contrariada, dispositivo, e por que é possivelmente erro
```

### 3.1 Nota sobre ruído

O nível 6 não deve gerar entrada em `warnings.md` para toda e qualquer microdecisão editorial não normatizada. Registrar apenas escolhas **estruturais ou de formatação sistemática** — algo que um revisor humano notaria como convenção deliberada do documento. Preferências de redação, escolha vocabular e estilo de prosa ficam fora.

### 3.2 Nota sobre a ordem 2 → 3

`INATEL` tem precedência sobre `10719-2015`. Isso significa que **onde o template do Inatel diverge da ABNT, o template vence** e o documento que segue o Inatel está conforme. Não reportar como erro um desvio da ABNT que seja exigência do template.

O inverso também vale: onde o `INATEL` é silencioso, a `10719-2015` volta a governar.

---

## 4. Calibração do padrão — migrada para o `pattern_profile.py`

A identificação automática do padrão normativo em uso (antes descrita aqui como uma leitura de
calibração feita pelo agente) passou a ser **determinística**: o `pattern_profile.py` varre o
projeto **inteiro** (glob-all) em busca dos sinais estruturais e emite a **classificação
normativa** — `INATEL` | `NBR10719/PUC` | `híbrido` | `nenhum reconhecido` — no **§3 do dossiê**.
O agente **consome essa classificação pronta**; não refaz a calibração aqui.

Rodar sobre o projeto inteiro (não só os arquivos incluídos) é deliberado: um marcador
institucional forte pode viver num arquivo de borda ou atrás de um `\include` comentado, e a
classificação não pode perdê-lo.

As definições específicas de cada padrão continuam em `padrao-inatel.md` / `padrao-nbr10719.md`;
a hierarquia de precedência e o algoritmo de decisão por aspecto estão nos §§2–3 acima.

---

## 5. Núcleo comum a todos os padrões

Regras que valem em `10719-2015`, `PUC` e `INATEL` simultaneamente. Desvios aqui são erro em qualquer padrão, salvo determinação explícita em contrário do nível 1.

### 5.1 Estrutura mínima

- O documento tem três partes funcionais identificáveis: **abertura** (objetivos e razões), **desenvolvimento** (o estudo em si) e **fechamento** (síntese e deduções).
- **Sumário** é obrigatório em todos os padrões.
- **Referências** são obrigatórias se houver qualquer citação no texto.
- **Nomenclatura dos títulos textuais é livre**, a critério do autor, em todos os padrões.
- Elementos pré-textuais **não** entram no sumário; pós-textuais **entram**.

### 5.2 Rastreabilidade cruzada

Verificações que independem de padrão e são as de maior valor:

| Verificação | Regra |
|---|---|
| Sumário ↔ texto | Títulos idênticos, numeração idêntica, páginas corretas |
| Listas ↔ elementos | Toda figura/tabela/sigla/símbolo da lista existe no texto, e vice-versa, na ordem correta |
| Citações ↔ referências | Nenhuma citação órfã; nenhuma referência não citada |
| Ilustrações ↔ texto | Toda ilustração é citada no corpo; nenhuma flutua sem menção |
| Numeração | Sem lacunas nem repetições em figuras, tabelas, quadros, equações, apêndices, anexos |
| Siglas | Expandidas na primeira ocorrência; constam da lista quando esta existe |

### 5.3 Numeração progressiva das seções (NBR 6024)

- Algarismos arábicos; seções primárias a partir de `1`
- Limite de profundidade: **seção quinária** (`1.1.1.1.1`)
- Indicativo alinhado à margem esquerda, separado do título por um espaço de caractere
- **Proibido** ponto, hífen, travessão, parênteses ou qualquer sinal entre o indicativo e o título
- Toda seção deve conter texto próprio — título seguido diretamente de subtítulo, sem conteúdo, é defeito
- Hierarquia destacada tipograficamente de forma **uniforme** da primária à quinária

### 5.4 Ilustrações

```
Figura 3 – Diagrama de blocos do receptor        ← identificação, parte SUPERIOR
        [ imagem ]
Fonte: elaborado pelo autor (2025).              ← fonte, parte INFERIOR, corpo menor
```

- Identificação na parte superior: palavra designativa + número de ordem em arábicos + separador + título
- **Fonte na parte inferior é elemento obrigatório, inclusive quando a ilustração é produção do próprio autor**
- Numeração sequencial e independente por tipo
- Citada no texto e inserida o mais próximo possível do trecho a que se refere
- Ilustração não citada não deve figurar no corpo — mover para apêndice ou anexo
- URL não é fonte de ilustração; a URL aparece apenas na lista de referências

### 5.5 Quadros × Tabelas

| | **Quadro** | **Tabela** |
|---|---|---|
| Conteúdo | teórico/qualitativo | numérico/quantitativo |
| Bordas | fechado, com moldura | laterais abertas |
| Padronização | ilustração comum | Normas de apresentação tabular do IBGE |

Tabela que ultrapassa a página: não fechar com traço horizontal inferior, indicar `continua`/`continuação` e **repetir o cabeçalho**.

Unidades, grandezas, múltiplos, submúltiplos e símbolos conforme o SI / Quadro Geral de Unidades de Medida (CONMETRO).

### 5.6 Equações e fórmulas

Destacadas do texto; numeradas, quando necessário, com algarismos arábicos **entre parênteses, alinhados à direita**.

```
x² + y² = z²            (1)
(x² + y²)/5 = n         (2)
```

### 5.7 Siglas

Primeira menção no texto: nome completo seguido da sigla entre parênteses — `Software Defined Radio (SDR)`. Menções seguintes: apenas a sigla. Não reexpandir depois.

### 5.8 Alíneas

- O texto que as antecede termina em **dois-pontos**
- Letras minúsculas seguidas de parêntese: `a)`, `b)`, `c)`
- Intermediárias terminam em **ponto-e-vírgula**; a última em **ponto**
- Subalíneas usam **símbolos**, mantidos os mesmos em todo o documento

### 5.9 Apêndice × Anexo

Distinção **semântica**, não estilística:

- **Apêndice** — texto ou documento **elaborado pelo autor** (questionário, TCLE, código-fonte próprio, deduções complementares)
- **Anexo** — texto ou documento **não elaborado pelo autor** (parecer de comitê de ética, datasheet de fabricante, certificado, regulamento)

Identificação: `APÊNDICE A – TÍTULO` / `ANEXO A – TÍTULO`, letras maiúsculas consecutivas + travessão + título. Esgotado o alfabeto, letras dobradas (`AA`, `AB`).

> Classificação trocada é **erro mesmo quando o documento é consistente**, porque a definição não é convenção editorial. Vai para `errors.md`.

### 5.10 Paginação

- Folhas pré-textuais contadas mas não numeradas visivelmente
- Numeração visível a partir da primeira folha da parte textual, em algarismos arábicos
- Sequência única do primeiro ao último volume
- Apêndices e anexos com numeração **contínua**, dando seguimento ao texto principal

### 5.11 Revisão a partir do source LaTeX

**Os documentos avaliados são sempre o source LaTeX, não o PDF compilado.** Isso muda o que é verificável e como.

#### O que a revisão de source faz melhor

Verificações mecânicas, exatas e exaustivas, impossíveis de fazer com confiabilidade sobre um PDF:

| Verificação | Como |
|---|---|
| Citações órfãs | toda chave em `\cite{}` existe no `.bib` |
| Referências não citadas | toda entrada do `.bib` aparece em algum `\cite{}` |
| Referências cruzadas quebradas | todo `\ref{}` tem `\label{}` correspondente |
| Rótulos duplicados | `\label{}` repetido |
| Ilustrações não citadas | `\label{fig:}` sem `\ref{}` correspondente |
| Siglas fora da lista | sigla literal no texto quando existe declaração para ela |
| Arquivos ausentes | caminho em `\includegraphics{}` ou `\include{}` inexistente |
| Macros indefinidas | macro usada sem `\newcommand` |
| Posição da legenda | ordem de `\caption` e `\includegraphics` dentro do ambiente |
| Parâmetros de layout | valores literais em `\geometry`, `\setcounter`, `\documentclass` |

#### O que não é verificável no source

Registrar como **não avaliado**, nunca como conforme:

- números de página, no corpo, no sumário e nas listas
- quebras de página, viúvas e órfãs
- posicionamento efetivo de flutuantes
- transbordo horizontal de tabelas e figuras
- aparência real de margens e espaçamentos

Para esses aspectos, avaliar o **mecanismo em vez do resultado**. Sumário gerado por `\tableofcontents` é correto por construção — não faz sentido conferir título a título, como se faria num documento de processador de texto. O que se verifica é se o comando está presente, se a profundidade está configurada e se os títulos das seções estão bem formados.

#### Deslocamento das verificações do §5.2

A rastreabilidade cruzada continua sendo o eixo da revisão, mas muda de alvo:

```
documento manual              source LaTeX
─────────────────────────     ─────────────────────────────
sumário ↔ títulos        →    \tableofcontents + tocdepth
lista de figuras ↔ figuras →  \listoffigures + \caption
lista de siglas ↔ siglas  →   \ac{} ↔ \acro{}, e sigla literal
citações ↔ referências    →   \cite{} ↔ chaves do .bib
numeração sem lacunas     →   automática; verificar contadores
```

#### Higiene do source

Reportar também, como qualidade de fonte:

- elementos **obrigatórios comentados** em `main.tex` (`% \include{...}`)
- `\include` apontando para arquivo inexistente
- macros de metadados definidas e não usadas, ou usadas e não definidas
- valores literais onde há macro disponível (data escrita à mão em vez de `\docDATA`)
- prefixos de `\label` heterogêneos (`fig:`, `tab_`, `sec:`)
- convenção de chave BibTeX declarada e não seguida

Seções comentadas durante a redação são normais e **não** devem ser reportadas, salvo quando o elemento é obrigatório.

---

## 6. Falsos positivos gerais

Não reportar como erro, em nenhum padrão:

1. **Nomenclatura dos títulos textuais.** `1 INTRODUÇÃO / 2 FUNDAMENTAÇÃO / 3 METODOLOGIA / 4 RESULTADOS / 5 DISCUSSÃO / 6 CONCLUSÃO` é conforme. Não exigir literalmente a palavra "Desenvolvimento".
2. **Ausência de elementos opcionais** no padrão aplicável.
3. **Ausência de referências** quando o relatório de fato não contém citações.
4. **Fonte tipográfica específica** (Latin Modern, Computer Modern, Charter em documentos LaTeX). O requisito é tipo **padronizado**, não um tipo determinado.
5. **Numeração de ilustrações por seção** (`Figura 2.1`), se uniforme.
6. **Separador de legenda** — travessão, hífen ou dois-pontos, se uniforme.
7. **Taxonomia própria de ilustrações**, se uniforme e refletida nas listas.
8. **Resumo/abstract em língua estrangeira** como adição.
9. **Elementos corporativos adicionais** — sumário executivo, histórico de revisões, matriz de rastreabilidade, controle de versões, tabela de aprovações, classificação de confidencialidade.
10. **Ausência de formulário de identificação e ficha catalográfica** em relatório interno de circulação restrita.
11. **Numeração visível já nos pré-textuais**, se uniforme e com contagem correta.
12. **Referências geradas por BibTeX** com pequenas variações de pontuação em relação à NBR 6023, desde que o estilo seja único em toda a lista.

---

## 7. Arquivos de saída

Toda execução de revisão produz **dois arquivos**.

### 7.1 `errors.md`

```markdown
# Erros — <nome do documento revisado>

Revisão em <data> · Padrão aplicado: <INATEL | 10719-2015 | híbrido>

| # | Local | Achado | Fonte contrariada | Por que é possivelmente um erro | Correção sugerida |
|---|-------|--------|-------------------|--------------------------------|-------------------|
| E01 | p. 12, Fig. 4 | Sem indicação de fonte | 10719-2015, 5.8 + consistência interna | A fonte é elemento obrigatório mesmo em ilustração autoral; as outras 11 figuras do documento a apresentam | Acrescentar `Fonte: elaborado pelo autor (2025).` |
| E02 | Sumário × seção 3.2 | Título divergente: sumário diz "Metodologia", texto diz "Materiais e métodos" | NBR 6027 via 10719-2015, 4.2.1.9 | O sumário deve reproduzir os títulos na mesma grafia em que aparecem no texto | Uniformizar os dois |
```

Regras de preenchimento:

- **Localização precisa** sempre: página, seção, número da figura/tabela/equação
- **Fonte contrariada** sempre identificada com sigla + dispositivo
- **Justificativa** explícita — o campo *por que* não é opcional
- Achados repetidos do mesmo tipo agrupados em uma linha com contagem e lista de localizações, nunca replicados dezenas de vezes
- Se não houver erros, criar o arquivo mesmo assim, declarando ausência de achados

### 7.2 `warnings.md`

```markdown
# Avisos — <nome do documento revisado>

Padrões divergentes do conjunto normativo, aplicados de forma consistente.
Possivelmente corretos — registrados para conferência humana.

| # | Local | Padrão observado | Situação | Observação |
|---|-------|------------------|----------|------------|
| W01 | Documento inteiro | Legenda de figura posicionada abaixo da imagem (24 ocorrências) | Nível 6 — nenhuma fonte governante endossa; aplicado uniformemente | Prática corrente em LaTeX e na 10719-1989. Confirmar se é escolha deliberada |
| W02 | Documento inteiro | Espaçamento entre linhas 1,5 | Nível 6 | 10719-2015 e PUC recomendam simples, sem caráter impositivo |
```

Regras de preenchimento:

- Registrar a **contagem de ocorrências** para evidenciar a consistência
- Indicar explicitamente que a resolução chegou ao **nível 6**
- Quando houver, mencionar qual fonte de menor prioridade admite a prática
- Não repetir aqui nada que já esteja em `errors.md`

### 7.3 Bloco de abertura comum

Ambos os arquivos devem ser precedidos, no corpo da resposta ao usuário, pelo registro do padrão inferido:

```markdown
## Padrão inferido do documento
- Origem: INATEL | 10719-2015 | PUC | híbrido
- Fonte: ... · Corpo: ... · Espaçamento: ... · Margens: ...
- Legendas de ilustração: acima | abaixo · Separador: travessão | hífen
- Numeração de ilustrações: corrida | por seção
- Sistema de citação: autor-data | numérico
- Profundidade de seccionamento: até seção ...
- Elementos presentes: ...
- Elementos ausentes relevantes: ...
```

---

## 8. Normas complementares invocadas

| Norma | Assunto | Onde importa |
|---|---|---|
| NBR 6023 | Referências — elaboração | Lista de referências |
| NBR 6024 | Numeração progressiva das seções | Indicativos de seção |
| NBR 6027 | Sumário | Composição do sumário |
| NBR 6028 | Resumo, resenha e recensão | Extensão e estrutura do resumo |
| NBR 6034 | Índice | Índice pós-textual |
| NBR 10520 | Citações em documentos | Citações, notas, fonte de ilustrações |
| NBR 10525 | ISSN | ISSN na capa e no formulário |
| NBR 12225 | Lombada | Lombada |
| IBGE — Normas de apresentação tabular | Tabelas | Estrutura de tabelas |
| CONMETRO / SI | Unidades de medida | Grandezas e símbolos |
| Código de Catalogação Anglo-Americano | Ficha catalográfica | Verso da folha de rosto |
