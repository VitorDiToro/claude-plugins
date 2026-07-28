# Template Inatel — Guia de Revisão Específico

**Complementa** `guia-mestre.md`. Ler o documento mestre antes deste.
**Escopo:** template/modelo de relatório técnico do Inatel, em LaTeX.

**Posição na hierarquia:** `INATEL` = **nível 2**, abaixo apenas de um padrão institucional explícito e **acima** da `10719-2015`.

> Onde o `INATEL` diverge da ABNT, **o template vence**. Não reportar desvio da ABNT que seja exigência ou prática estabelecida do template.
> Onde o `INATEL` é silencioso, a `10719-2015` (nível 3) volta a governar. Ver `padrao-nbr10719.md`.

---

## 0. Princípio de aplicação: nada é rígido

A arquitetura do template **varia entre projetos**. Nomes de arquivo, organização de diretórios, nomes de macros, valores numéricos do preâmbulo e até a existência de certos elementos mudam de um projeto para outro.

**Consequência para o agente:**

1. **Nunca** verificar a existência de um arquivo com nome específico.
2. **Nunca** assumir um valor numérico de layout como exigência.
3. Identificar elementos por **assinatura semântica** — comandos LaTeX e conteúdo — e não por nome de arquivo, diretório ou macro.
4. Extrair os parâmetros de formatação **do próprio projeto sob revisão** e verificar coerência interna, em vez de compará-los a números memorizados.

O que é estável no `INATEL` é a **estrutura** e o **conjunto de convenções**. Todo o resto é parâmetro do projeto.

Ao longo deste guia, valores concretos aparecem como **referência típica**, marcados como tal. Referência típica não é critério de conformidade e não gera achado.

---

## 1. Identificação dos elementos no source

Tabela de assinaturas. É por aqui que o agente localiza cada elemento, independentemente de como o projeto organiza seus arquivos.

| Elemento | Assinatura no source |
|---|---|
| Arquivo principal | contém `\documentclass` e `\begin{document}` |
| Preâmbulo de configuração | arquivo trazido por `\input`/`\include` no preâmbulo, com `\usepackage`, `\geometry`, `fancyhdr` |
| **Capa** | primeiro bloco após `\begin{document}`; `\newgeometry` próprio, `\pagestyle{empty}`, logos em `\includegraphics`, título em `\fontsize` grande |
| **Folha de rosto** | tabela de metadados com rótulos em negrito (`Título:`, `Autor(es):`, `Data:`, `Versão:`, …) |
| **Histórico de Atualizações** | tabela cujo cabeçalho contém `Versão`, `Data`, `Autor(es)`, `Notas`; título com a palavra *Histórico* |
| **Lista de figuras** | `\listoffigures` |
| **Lista de tabelas** | `\listoftables` |
| **Acrônimos / siglas** | pacote `acronym` com `\begin{acronym}` e `\acro{}`, ou `glossaries` |
| **Lista de símbolos** | `glossaries` com opção `symbols`, ou lista manual |
| **Sumário** | `\tableofcontents`, geralmente com `\renewcommand{\contentsname}{Sumário}` |
| **Seções textuais** | `\section{...}` nos arquivos incluídos entre o sumário e o pós-texto |
| **Apêndice** | `\begin{appendices}` ou `\appendix` |
| **Referências** | `\bibliography{...}`, `\printbibliography` ou `thebibliography` |
| Comando de página padrão | macro definida no preâmbulo que aplica `\newgeometry` + `\pagestyle{fancy}`, invocada no início de cada arquivo de seção |
| Macros de metadados | `\newcommand` no arquivo principal, agrupadas num bloco de definições do documento |

> **Nomes são pistas, não critérios.** Um arquivo chamado `indice.tex` pode conter o **sumário**; um chamado `historico_de_revisoes.tex` pode gerar uma seção intitulada *Histórico de Atualizações*. Sempre classificar pelo comando e pelo conteúdo, nunca pelo nome. Quando nome e conteúdo divergirem, registrar em `warnings.md` como ruído de manutenção — não como erro.

---

## 2. Estrutura — `INATEL`

Esta é a parte estável do padrão.

```
PARTE EXTERNA
└── Capa .......................................... OBRIGATÓRIO

PARTE INTERNA   (pré-texto em numeração romana)
├── Elementos pré-textuais
│   ├── Folha de rosto ............................ opcional
│   ├── Histórico de Atualizações ................. OBRIGATÓRIO
│   ├── Errata .................................... opcional
│   ├── Agradecimentos ............................ opcional
│   ├── Lista de figuras .......................... obrigatório SE houver figuras
│   ├── Lista de tabelas .......................... obrigatório SE houver tabelas
│   ├── Lista de símbolos ......................... opcional
│   ├── Acrônimos / siglas ........................ obrigatório SE houver siglas
│   ├── Glossário ................................. opcional
│   └── Sumário ................................... OBRIGATÓRIO
├── Elementos textuais   (numeração arábica, reiniciada)
│   ├── Introdução ................................ OBRIGATÓRIO
│   ├── Desenvolvimento ........................... OBRIGATÓRIO
│   ├── Considerações finais ...................... opcional
│   └── Conclusão ................................. OBRIGATÓRIO
└── Elementos pós-textuais
    ├── Apêndice .................................. opcional
    ├── Referências ............................... obrigatório SE houver citações
    ├── Anexo ..................................... opcional
    ├── Índice .................................... opcional
    └── Formulário de identificação ............... obrigatório SE não houver ficha catalográfica
```

**Ordem das listas:** figuras → tabelas → símbolos → siglas.

**Pós-texto:** o apêndice **precede** as referências, inverso da `10719-2015`. Seguir o Inatel.

### 2.1 Tolerância na ordem

A ordem acima é a esperada, mas projetos variam. Antes de reportar uma ordem divergente:

- Elementos **ausentes** não geram achado se forem opcionais.
- Troca de posição entre elementos **opcionais adjacentes** → `warnings.md`.
- Elemento **obrigatório** fora de posição, ou sumário que não seja o último pré-textual → `errors.md`.

### 2.2 Apêndice e anexo

Ambos opcionais. Vale a distinção **semântica** do guia mestre §5.9 — apêndice é material do autor, anexo é material de terceiro — e ela continua sendo erro quando trocada, mesmo com o documento consistente, porque não é convenção editorial.

**Posição do anexo:** o template prevê o elemento mas raramente o exercita, e não fixa sua posição em relação às referências. Aceitar tanto `apêndice → anexo → referências` quanto `apêndice → referências → anexo`, desde que uniforme. Divergência interna entre múltiplos anexos → `errors.md`.

### 2.3 Lista de símbolos

Opcional. É comum o mecanismo estar carregado no preâmbulo e não ser usado — isso **não** é defeito e não gera achado. Verificar apenas quando a lista existir de fato.

---

## 3. Deltas em relação à `10719-2015`

| Aspecto | `10719-2015` | `INATEL` | Efeito |
|---|---|---|---|
| **Capa** | opcional | **OBRIGATÓRIA** | Ausência → `errors.md` |
| **Lombada** | opcional | não prevista | Nunca é erro |
| **Folha de rosto** | **OBRIGATÓRIA** | **opcional** | Ausência não é erro |
| **Histórico de Atualizações** | inexistente | **OBRIGATÓRIO** | Ausência → `errors.md`. Ver §5 |
| **Resumo + palavras-chave** | **OBRIGATÓRIO** | **dispensado** | Ausência nunca é erro. Ver §6 |
| **Lista de figuras** | opcional | **obrig. se houver figuras** | Gerada automaticamente |
| **Lista de tabelas** | opcional | **obrig. se houver tabelas** | Gerada automaticamente |
| **Lista de siglas** | opcional; "Lista de abreviaturas e siglas" | **obrig. se houver siglas**; título usual **"Acrônimos"** | Gerada automaticamente |
| **Glossário** | pós-textual | pré-textual | Posição pré-textual não é erro |
| **Considerações finais** | **OBRIGATÓRIO** | **opcional** | Ausência não é erro |
| **Conclusão** | não é elemento separado | **OBRIGATÓRIA** | Ausência → `errors.md` |
| **Ordem pós-textual** | referências → apêndice | **apêndice → referências** | Seguir Inatel |
| **Paginação pré-textual** | contada, não numerada | **numerada em romanos** | Não reportar |
| **Posição do fólio** | canto superior direito (`PUC`) | **rodapé centralizado** | Não reportar |
| **Legenda de figura** | acima | **abaixo** | Não reportar. Ver §4.3 |
| **Legenda de tabela** | acima | **acima** | Conforme |
| **Separador da legenda** | travessão | **dois-pontos** | Não reportar |
| **Fonte da ilustração** | **obrigatória**, inclusive autoral | **dispensada**, uso tolerado | Ausência nunca é erro. Ver §7 |
| **Título de apêndice** | `APÊNDICE A – Título` | **título obrigatório**, formato livre | Título vazio → `errors.md`. Ver §8.4 |
| **Estilo de referências** | NBR 6023 | **numérico, estilo IEEE** | Não reportar |
| **Idioma dos acrônimos** | não normatizado | **inglês** | Ver §4.5 |

### 3.1 Inversões de obrigatoriedade

```
                            10719-2015      INATEL
Capa                        opcional    →   obrigatória
Folha de rosto              obrigatória →   opcional
Considerações finais        obrigatória →   opcional
Histórico de Atualizações   inexistente →   obrigatório
Resumo                      obrigatório →   dispensado
Fonte da ilustração         obrigatória →   dispensada
```

---

## 4. Convenções de formatação

### 4.1 Parâmetros a extrair do projeto

Estes valores **variam entre projetos** e devem ser lidos do preâmbulo do documento sob revisão. A coluna de referência serve para orientar a leitura, nunca para julgar conformidade.

| Parâmetro | Onde ler | Referência típica |
|---|---|---|
| Classe do documento | `\documentclass` | `article` |
| Corpo base | opção da `\documentclass` | 12 pt |
| Papel | opção da classe / `\geometry` | A4 |
| Família tipográfica | pacote de fonte no preâmbulo | Latin Modern |
| Margens de conteúdo | `\newgeometry` dentro do comando de página padrão | topo maior, para acomodar o cabeçalho; laterais e base menores |
| Espaçamento entre linhas | `setspace` acionado ou não | simples |
| Alinhamento | `\justify` no início dos arquivos de seção | justificado |
| Profundidade de numeração | `\setcounter{secnumdepth}{...}` | 5 |
| Profundidade do sumário | `\setcounter{tocdepth}{...}` | 5 |
| Filete de nota de rodapé | `\renewcommand{\footnoterule}{...}` | 5 cm — coincide com a `10719-2015`, 5.5 |

**O que verificar:** que o valor é aplicado **uniformemente**, que todo arquivo de seção invoca o comando de página padrão, e que não há sobrescrita local não justificada. **O que não verificar:** se o número bate com o de outro projeto.

### 4.2 Cabeçalho, rodapé e paginação

Invariantes do padrão:

- Cabeçalho sem filete, com logo do projeto
- Fólio no **rodapé, centralizado**
- Pré-texto em **algarismos romanos**, visíveis
- Texto em **arábicos, reiniciando em 1** na Introdução

### 4.3 Ilustrações e tabelas

Convenção **assimétrica** do template:

```latex
% FIGURA — legenda ABAIXO da imagem
\begin{figure}[h]
    \centering
    \includegraphics[width=14cm,keepaspectratio]{figures/exemplo.pdf}
    \caption{Legenda da figura.}
    \label{fig:exemplo}
\end{figure}

% TABELA — legenda ACIMA do tabular
\begin{table}[h]
    \caption{Legenda da tabela.}\label{tab:exemplo}
    \centering
    \begin{tabular}{...}
    ...
    \end{tabular}
\end{table}
```

- Nomes designativos redefinidos para *Figura* e *Tabela*
- Sem `\captionsetup` → separador padrão da classe, **dois-pontos** (`Figura 1: Legenda`)
- Legendas terminam em ponto final
- Sub-figuras com legenda própria e `\caption` geral ao final do ambiente
- Sugestão do template: usar **Times New Roman** no texto interno das figuras

### 4.4 Posicionamento de flutuantes

**Ordem de prioridade do template:**

```
[h]  →  [h!]  →  [!ht]  →  [H]
```

| Especificador | Significado | Situação |
|---|---|---|
| `[h]` | aqui, se couber | **preferencial** |
| `[h!]` | aqui, ignorando os parâmetros estéticos de flutuação | 1ª alternativa |
| `[!ht]` | aqui ou no topo da página, ignorando os parâmetros | 2ª alternativa |
| `[H]` | posição absoluta, sem flutuação (requer `float`) | último recurso |

**Regra de revisão:**

> **Todo flutuante cujo especificador não seja `[h]` gera entrada em `warnings.md`**, informando qual especificador foi usado e sua posição na escala de prioridade.

Isso inclui:

- ambientes `figure` e `table` **sem especificador** — o padrão da classe (`tbp`) afasta o flutuante do texto e é o caso mais grave da escala
- qualquer combinação fora da lista acima (`[t]`, `[b]`, `[p]`, `[htbp]`, …) → `warnings.md`, com nota de que está fora da escala do template

**Nunca classificar como erro.** A escolha de posicionamento é decisão do autor diante do resultado da compilação, que o agente não observa. O papel do aviso é sinalizar que o autor subiu na escala e que o afastamento entre a ilustração e o trecho que a cita pode ter aumentado — o que toca a exigência, comum a todos os padrões, de inserir a ilustração o mais próximo possível do texto a que se refere.

**Formato de reporte:** uma entrada agregada por especificador, com contagem e lista de localizações.

```markdown
| W03 | 7 ocorrências | Flutuantes com `[!ht]` (2º nível da escala) | Nível 6 | Preferencial é `[h]`. Locais: fig:arq_geral, fig:setup_lab, tab:parametros, … |
| W04 | 3 ocorrências | Flutuantes sem especificador (padrão `tbp`) | Nível 6 | Fora da escala; afasta o flutuante do texto citante |
```

### 4.5 Acrônimos

- Pacote `acronym`, tipicamente com `printonlyused`
- Uso no texto por comando (`\ac{SIGLA}`), com expansão automática na primeira ocorrência
- Declarações concentradas num único arquivo de acrônimos
- Termos em inglês em `\emph{}` ou `\textit{}`
- **Regra explícita do template:** acrônimos em **inglês**
- **Regra explícita do template:** a cada novo acrônimo, adicionar/confirmar no arquivo de acrônimos

Consequência: a obrigatoriedade "lista de siglas se houver siglas" é satisfeita **mecanicamente**, desde que os autores usem o comando. Sigla digitada literalmente no texto **não** entra na lista — é este o defeito a caçar, não a ausência da lista.

### 4.6 Referências bibliográficas

- Estilo **numérico, padrão IEEE** — não é NBR 6023
- Citação por `\cite{}`
- Base BibTeX única, referenciada em `\bibliography{}`
- **Convenção de chave declarada pelo template:**

```
ano_sobrenomeDoPrimeiroAutor_primeiraPalavraDoTítulo
Exemplo: 2019_rappaport_above
```

A convenção pode variar entre projetos. Verificar **qual convenção o projeto declara** — em arquivo de avisos, README ou comentário de preâmbulo — e conferir a base contra ela. Não havendo convenção declarada, verificar apenas a uniformidade das chaves existentes.

---

## 5. Histórico de Atualizações

Elemento **exclusivo** do Inatel, sem correspondente na ABNT. **Obrigatório.**

**Posição:** após a folha de rosto, antes das listas.

**Estrutura:** tabela com quatro colunas.

| Coluna | Conteúdo |
|---|---|
| `Versão` | inteiro sequencial |
| `Data` | data da revisão |
| `Autor(es)` | nomes completos, um por linha |
| `Notas` | descrição da alteração |

Rótulos e larguras podem variar. Identificar pela presença das quatro funções, não pelo texto exato do cabeçalho.

### 5.1 Verificações

- [ ] Elemento presente e posicionado após a folha de rosto
- [ ] As quatro colunas funcionais existem
- [ ] Versões sequenciais, sem lacunas
- [ ] Datas em formato uniforme e **cronologicamente crescentes**
- [ ] Nenhuma célula vazia
- [ ] Datas coerentes com as macros de metadados e com a data da capa — ver §8.2

---

## 6. Resumo — dispensado

**Decisão institucional: o `INATEL` dispensa o *Resumo na língua vernácula*.**

Trata-se de supressão deliberada, não de omissão. O nível 2 governa e determina a ausência.

- Ausência de resumo e de palavras-chave → **nada a reportar**, em nenhum arquivo de saída
- Não descer para a `10719-2015` neste aspecto
- Não registrar em `warnings.md`

Se um projeto específico **incluir** um resumo, é adição legítima. Verificá-lo então conforme `padrao-nbr10719.md` §2.4, mas sem nunca exigi-lo.

---

## 7. Fonte das ilustrações — dispensada, uso tolerado

**Decisão institucional: o `INATEL` dispensa a indicação de fonte nas ilustrações.**

O nível 2 governa e afasta a exigência da `10719-2015`, 5.8. Consequências:

- Ilustração sem fonte → **nada a reportar**
- **Não** gerar a entrada agregada em `warnings.md` prevista na versão anterior deste guia
- Não descer para a `10719-2015` neste aspecto

### 7.1 Uso tolerado

Projetos podem implementar e usar uma macro de fonte. Nesse caso:

- O uso é **livre e parcial**. Como o elemento é dispensado, aplicá-lo a algumas ilustrações e não a outras **não** configura inconsistência interna e **não** gera achado.
- Verificar apenas se as ocorrências existentes são bem formadas e mutuamente uniformes: mesma posição relativa ao `\caption`, mesmo padrão de redação e de pontuação final.
- Divergência entre as ocorrências existentes → `warnings.md`.

Implementação de referência, caso um projeto queira adotá-la:

```latex
\newcommand{\fonte}[1]{%
  \par\vspace{-0.3cm}%
  {\footnotesize\raggedright Fonte: #1\par}%
}
```

### 7.2 Atribuição de material de terceiros

A dispensa é da **regra de forma** da ABNT, não do dever de creditar autoria alheia.

Ilustração evidentemente reproduzida ou adaptada de terceiro — captura de artigo, figura de norma técnica, imagem de fabricante, gráfico de relatório externo — sem qualquer atribuição, nem na legenda, nem por citação, nem por `\fonte{}`, deve gerar entrada em **`warnings.md`**.

Isso é boa prática de integridade acadêmica e questão de direito autoral, não conformidade normativa. Manter o tom informativo e não classificar como erro: o agente não tem como determinar a procedência de uma imagem com segurança a partir do source.

---

## 8. Padrões defeituosos recorrentes

Defeitos observados em documentos reais do template. São descritos como **padrões de código a detectar**, não como ocorrências em arquivos específicos.

### 8.1 Sequestro de `\listoftables` para gerar título de outra lista

```latex
\renewcommand{\listtablename}{Acrônimos}
\listoftables
```

Renomear a lista de tabelas e chamá-la de novo **duplica a lista de tabelas**, agora sob outro título. A lista pretendida vem de outro mecanismo, logo abaixo.

**Detecção:** mais de um `\listoftables` ou `\listoffigures` no documento; `\renewcommand{\listtablename}` ou `\listfigurename` com valor que não designe tabelas ou figuras.

**Severidade: ERRO.** Correção: usar um título de seção não numerado com entrada no sumário, em vez de reaproveitar o comando de lista.

### 8.2 Macros de metadados usadas e não definidas

Elementos de identificação frequentemente referenciam macros que o arquivo principal não define, quebrando a compilação com *Undefined control sequence*.

**Detecção:** toda macro no padrão de metadados do projeto usada em qualquer arquivo deve ter `\newcommand` correspondente. Levantar o conjunto de macros usadas e o de definidas, e reportar a diferença nos dois sentidos — indefinidas são erro, definidas e não usadas são aviso.

**Severidade: ERRO** para usadas e não definidas.

### 8.3 Datas divergentes e literais

Capa, macros de metadados e histórico frequentemente carregam datas diferentes para o mesmo documento, e a capa costuma trazer data escrita à mão com a macro correspondente comentada ao lado.

**Detecção:** extrair toda data do source e conferir coerência; sinalizar data literal onde exista macro disponível; verificar se as datas do histórico são compatíveis com a data declarada do documento.

**Severidade: ERRO.**

### 8.4 Apêndices sem título

Seções de apêndice declaradas com título vazio recebem letra mas nenhuma denominação.

**Decisão institucional: o preenchimento do título é obrigatório no `INATEL`.**

**Detecção:** dentro do ambiente de apêndices, comando de seção com argumento vazio ou contendo apenas espaços — `\section{}`, `\section{ }`.

**Severidade: ERRO.** Regra de nível 2, não mais herdada da ABNT.

O **formato** do título é livre: o Inatel não exige a construção `APÊNDICE A – Título` da `10719-2015`. Basta que o argumento seja preenchido e que os títulos sejam mutuamente coerentes em estilo. Não reportar a ausência do travessão nem da palavra designativa.

### 8.5 Acrônimos duplicados

Sigla declarada duas vezes: LaTeX usa a última definição e descarta silenciosamente a primeira.

**Detecção:** chaves de declaração repetidas no arquivo de acrônimos.

**Severidade: ERRO.**

### 8.6 Siglas concorrentes para o mesmo conceito

Coexistência da forma em inglês e da forma em português para o mesmo conceito — por exemplo, a sigla inglesa e sua tradução declaradas separadamente. Contraria a regra de acrônimos em inglês do próprio template.

**Detecção:** expansões semanticamente equivalentes sob chaves distintas; expansões em português quando o projeto declara acrônimos em inglês.

**Severidade: ERRO.** Verificar também acentuação das expansões em português remanescentes.

### 8.7 Convenção de chave BibTeX não seguida

Quando o projeto declara uma convenção de nomenclatura de chaves, é comum que a maioria das entradas não a siga, inclusive os próprios exemplos do template.

**Severidade: AVISO.** Não afeta a compilação; afeta manutenção.

Menor: variação de caixa nos tipos de entrada (`@article`, `@Article`, `@ARTICLE`). BibTeX é insensível a caixa; puramente cosmético.

---

## 9. Verificações de source

Método geral em `guia-mestre.md` §5.11. Específicas do Inatel:

### 9.1 Integridade da montagem

- [ ] O arquivo principal traz o preâmbulo de configuração
- [ ] Toda macro de metadados usada está definida
- [ ] Ordem dos elementos conforme §2, com as tolerâncias de §2.1
- [ ] Nenhum elemento **obrigatório** comentado no arquivo principal
- [ ] Nenhum `\include`/`\input` apontando para arquivo inexistente
- [ ] Troca de numeração romana → arábica na transição pré-texto → texto
- [ ] Todo arquivo de seção invoca o comando de página padrão do projeto
- [ ] Todo arquivo de seção textual aplica o alinhamento justificado

> Seções comentadas durante a redação são normais e **não** devem ser reportadas, salvo quando o elemento é obrigatório.

### 9.2 Rastreabilidade

- [ ] Toda chave em `\cite{}` existe na base BibTeX
- [ ] Toda entrada da base é citada — se não, `warnings.md`
- [ ] Toda sigla usada por comando tem declaração correspondente
- [ ] Nenhuma sigla escrita literalmente quando existe declaração para ela
- [ ] Nenhuma declaração de sigla duplicada
- [ ] Todo `\ref{}` tem `\label{}` correspondente
- [ ] Todo rótulo de figura ou tabela é referenciado no texto
- [ ] Nenhum `\label` duplicado
- [ ] Todo arquivo em `\includegraphics{}` existe

### 9.3 Convenções de escrita

- [ ] Acrônimos em inglês
- [ ] Prefixos de `\label` uniformes (`sec:`, `fig:`, `tab:`)
- [ ] Referência cruzada com espaço não separável (`Seção~\ref{}`)
- [ ] Termos estrangeiros em `\textit{}` ou `\emph{}`
- [ ] Chaves BibTeX conforme a convenção declarada pelo projeto
- [ ] Legenda de figura **depois** do gráfico; de tabela **antes** do `tabular`
- [ ] **Flutuantes com `[h]`** — qualquer outro especificador → `warnings.md` (§4.4)
- [ ] **Todo apêndice com título preenchido** — argumento vazio → `errors.md` (§8.4)
- [ ] Apêndice contém material do autor; anexo, material de terceiro (§2.2)

### 9.4 Não verificável no source

Registrar como não avaliado, nunca como conforme: números de página, quebras, viúvas e órfãs, posicionamento efetivo dos flutuantes, transbordo horizontal, aparência das margens.

Avaliar o **mecanismo** e não o resultado.

---

## 10. Checklist Inatel

Aplicar **depois** do checklist comum do guia mestre.

### 10.1 Estrutura obrigatória

- [ ] Capa
- [ ] Histórico de Atualizações, íntegro (§5.1)
- [ ] Lista de figuras, se houver figuras
- [ ] Lista de tabelas, se houver tabelas
- [ ] Lista de siglas, se houver siglas
- [ ] Sumário, como último pré-textual
- [ ] Introdução
- [ ] Desenvolvimento
- [ ] Conclusão
- [ ] Referências, se houver citações

### 10.2 Ordem

- [ ] Pré-texto: capa → folha de rosto → histórico → listas → sumário
- [ ] Listas: figuras → tabelas → símbolos → siglas
- [ ] Considerações finais, se presente, antes da Conclusão
- [ ] Pós-texto: **apêndice → referências**

### 10.3 Não reportar

Conformes no Inatel, ainda que divirjam da ABNT:

- ausência de folha de rosto, lombada, resumo, palavras-chave, errata, agradecimentos, glossário, índice, lista de símbolos, considerações finais, apêndice, anexo
- **ausência de indicação de fonte nas ilustrações** (§7)
- uso parcial de macro de fonte, em algumas ilustrações e não em outras (§7.1)
- título de apêndice sem a construção `APÊNDICE A – Título` da ABNT, desde que preenchido (§8.4)
- mecanismo de lista de símbolos carregado no preâmbulo e não usado (§2.3)
- pré-texto numerado em algarismos romanos
- fólio no rodapé centralizado
- reinício da numeração arábica na Introdução
- legenda **abaixo** da figura
- separador de legenda em dois-pontos
- lista de siglas intitulada "Acrônimos"
- referências em estilo numérico IEEE
- apêndice antes das referências
- seção "Histórico de Atualizações"
- `Conclusão` como seção de fechamento
- margens, fonte e corpo diferentes dos de outro projeto do mesmo template

---

## 11. Decisões institucionais registradas

Pendências resolvidas. Não reabrir sem nova determinação.

| # | Questão | Decisão | Efeito | Seção |
|---|---|---|---|---|
| 1 | Resumo na língua vernácula | **Dispensado** — supressão deliberada, não omissão | Ausência nunca é reportada; nível 2 afasta a `10719-2015` | §6 |
| 2 | Fonte das ilustrações | **Dispensada**, com uso tolerado | Ausência nunca é reportada; uso parcial não é inconsistência | §7 |
| 3 | Título dos apêndices | **Preenchimento obrigatório**, formato livre | Argumento vazio → `errors.md`; formato ABNT não é exigido | §8.4 |
| 4 | Lista de símbolos | **Opcional** | Mecanismo carregado e não usado não é defeito | §2.3 |
| 5 | Anexo | **Opcional**, posição livre em relação às referências | Distinção semântica com o apêndice continua valendo | §2.2 |

Nenhuma pendência estrutural permanece aberta. As lacunas remanescentes são de parâmetro, não de norma, e resolvem-se lendo o preâmbulo do projeto sob revisão (§4.1).
