# Checklist de revisão — recortes por passe

> Cada bloco carrega uma TAG `<!-- passe: N (PREFIXO) -->` indicando o passe dono.
> O checklist **inteiro** é carregado uma vez no prefixo; cada passe **atua só no seu recorte**
> (o passe N adjudica apenas os blocos marcados `passe: N`).
>
> **Armadilha a evitar:** a subcategoria **"Bibliografia e citações"** mora sob
> "LaTeX / estrutura" por proximidade temática, mas pertence ao **passe 6 (R)** — **não** ao
> passe 1 (C). Está marcada explicitamente abaixo.

## LaTeX / estrutura
<!-- passe: 1 (C) -->

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
  Esta é a regra de fallback quando nenhum padrão normativo é reconhecido; com um
  padrão reconhecido, use a escada de precedência específica dele (ver
  "Conformidade com padrão normativo reconhecido" em `## Estrutura e rigor acadêmico`).
- Posição da legenda de figura/tabela (acima/abaixo) — quando um padrão normativo é
  reconhecido, siga a convenção que ele determina; sem padrão reconhecido, siga o
  padrão interno já adotado pelo próprio documento, como de costume.
- Mesma imagem reutilizada em figuras distintas; arquivo de imagem ausente ou
  caminho quebrado.
- Tabela sem `\caption`/`\label`, ou com legenda vazia/genérica ("Tabela 1").
- Tabela extensa (muitas linhas) usando `tabular` em vez de `longtable` —
  candidata a estourar a página.
- Estilo de tabela inconsistente: `\hline` manual e `booktabs`
  (`\toprule`/`\midrule`) misturados no mesmo documento.

<!-- passe: 6 (R) — ESTE BLOCO É DO PASSE 6 (Referências), não do passe 1 -->
**Bibliografia e citações**
> Os itens com respaldo de script (chave `\cite` órfã, entrada `.bib` nunca citada, campo
> essencial ausente por tipo, DOI condicional, formato) são **adjudicação dos candidatos do §5**
> (`crossref_check.py` + `bib_check.py`) — não varredura do zero.
- Existência de seção de Referências; citações `\cite` sem entrada
  correspondente.
- DOI ausente em referências quando outras entradas do mesmo tipo já têm.
- Citação direta extensa (candidata a >3 linhas renderizadas em ABNT) sem
  recuo/formatação de bloco — linhas no código-fonte são só um indício
  aproximado, a checagem definitiva depende da renderização.
- Referência bibliográfica sem campo essencial (autor, título, ano, editora/veículo) para
  o tipo de fonte (livro, artigo, site, etc.) — regra de fallback quando nenhum padrão
  normativo é reconhecido; com um padrão reconhecido, use as regras de formatação de
  referências do arquivo `references/padrao-*.md` aplicável.
<!-- fim passe 6; retoma passe 1 (C) abaixo -->

**Hyperref e links**
<!-- passe: 1 (C) -->
- `\url`/`\href` com sintaxe malformada, ou link em texto cru sem comando.
- Cor/estilo de link inadequado ao padrão do documento (ex.: cores vivas num
  documento que o padrão indica ser impresso em P&B).

**Idioma e configuração técnica**
- Pacote de idioma (`babel`/`polyglossia`) configurado para idioma diferente
  do texto real do documento — afeta hifenização e nomes automáticos
  ("Capítulo"/"Chapter", "Figura"/"Figure").

## Gramática e ortografia
<!-- passe: 2 (G) -->

**Crase**
- Crase indevida ou ausente diante de pronomes indefinidos, substantivos femininos
  determinados, etc. (ex.: "à cada" quando o certo é "a cada"; "em relação a integração"
  quando falta a crase; "graças a isolação" quando falta a crase).

**Concordância verbal e nominal**
- Verbo não concorda em número/pessoa com o sujeito (ex.: "que compõe" para sujeito
  plural, deveria ser "que compõem"; "Os resultado" deveria ser "Os resultados").
- Concordância de gênero entre sujeito e predicativo (ex.: "a visão... é o mesmo"
  deveria ser "é a mesma").

**Regência verbal e nominal**
- Verbo usado com a preposição errada ou sem o conectivo exigido (ex.: "permitiu a
  rede estabelecer" — falta "à" + infinitivo ou "que" + subjuntivo).

**Ortografia e acentuação**
- Palavras grafadas incorretamente ou sem o acento exigido (ex.: "fléxivel" em vez de
  "flexível"; "posível" em vez de "possível"; "referencia" sem acento).

**Pontuação e espaçamento**
- Vírgula sem função sintática (ex.: "Aproximadamente, 6,5 kg").
- Espaços duplicados ou mal posicionados (antes de vírgula, logo após chave de
  abertura de comando, etc.).

**Digitação e resíduos de edição**
- Palavras ou artigos duplicados por erro de cópia/edição (ex.: "um uma antena", "de
  de forma gráfica", "protocolo... protocolo").
- Duas construções verbais coladas sem conectivo, resultando em frase agramatical
  (ex.: "os testes foram realizados concentraram-se").
- Palavras corrompidas/fundidas incorretamente (ex.: "deo enlace" em vez de "do
  enlace").

**Repetição excessiva de palavras ou expressões (vício de linguagem)**
- Usa as contagens de frequência lexical e a seção de frases repetidas/quase-repetidas
  (`text_analysis.py`) para identificar candidatos a repetição excessiva — tanto palavra/
  expressão sobre-usada quanto trecho/frase reaproveitada verbatim (boilerplate).
- Distingue vício de linguagem (conectivos, verbos de ligação, frases de transição usados
  em excesso — ex.: "portanto", "cabe destacar que", "no que tange a") de repetição
  legítima de termo de domínio (o assunto do próprio texto, que naturalmente recorre e não
  é um achado) — julgamento do revisor, não do script.
- Sinalizar quando o padrão se repete de forma notável ao longo do documento, não uma ou
  duas ocorrências isoladas.

**Prolixidade e frases excessivamente longas**
- Frases com excesso de orações subordinadas ou "rodeios" que prejudicam a clareza —
  sinalizar quando o padrão se repete ao longo do texto, não uma frase isolada pontualmente
  longa.
- Usa a seção de frases mais longas (`text_analysis.py`) como indício objetivo de candidatas;
  a divisão de frase é aproximada, então o julgamento do revisor decide se a frase longa é
  realmente prolixa ou só densa por natureza técnica.

**Homônimos e parônimos confundidos pelo contexto**
- Palavra correta ortograficamente mas errada pelo sentido da frase (ex.: "mas" no lugar de
  "mais", "se não" no lugar de "senão", e pares semelhantes) — diferente de erro de
  ortografia (a palavra existe e está bem escrita, só é a palavra errada para o contexto).

## Terminologia e consistência
<!-- passe: 3 (T) -->

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

## Estrutura e rigor acadêmico
<!-- passe: 4 (E) -->

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
  seções/capítulos — usa a seção de frases repetidas/quase-repetidas do `text_analysis.py`
  como indício de trechos reaproveitados verbatim entre seções.
- Objetivos declarados na introdução que não são todos retomados na
  conclusão.
- Seção ou capítulo com extensão muito desproporcional em relação aos demais (ex.: um
  capítulo com uma fração do tamanho dos outros, sem justificativa aparente no conteúdo) —
  usa a contagem de palavras por arquivo do perfil de padrão como indício; é contagem bruta,
  não conteúdo líquido, então julgamento do revisor decide se a disparidade é real ou só um
  artefato de um arquivo com mais figuras/tabelas/marcação.

**Conformidade com padrão normativo reconhecido**
- Quando um padrão institucional é identificado (seleção explícita do usuário, ou
  classificação normativa da Fase 0), aplique a hierarquia de
  `references/guia-mestre.md` e o(s) arquivo(s) `references/padrao-*.md` aplicável(is)
  para os aspectos estruturais/normativos: elementos pré-textuais/textuais/pós-textuais
  esperados e sua ordem, convenções específicas do padrão (ex.: Histórico de
  Atualizações do Inatel, distinção apêndice/anexo).
- O mapeamento entre o que o arquivo de referência chama de erro/aviso e a
  classificação final (severidade 🔴/🟠/🟡 ou categoria `AV`): onde `guia-mestre.md` ou o
  `padrao-*.md` aplicável rotula explicitamente "Severidade: ERRO" ou "Severidade: AVISO",
  siga o rótulo (erro → 🔴/🟠/🟡 pelo impacto; aviso → `AV`). Onde não há rótulo, aplique o
  algoritmo de `guia-mestre.md` §3: contradiz uma fonte de nível 1-5, ou inconsistência
  interna → erro; nenhuma fonte trata do aspecto mas o documento é consistente (nível 6) →
  `AV`. Este mecanismo só se aplica quando um padrão foi reconhecido.
- **Quando nenhum padrão é reconhecido**, este item não se aplica — os aspectos
  estruturais continuam cobertos pelos bullets já existentes neste checklist (floats,
  bibliografia, etc.), julgando pela consistência interna do documento, como sempre.

## Conteúdo técnico
<!-- passe: 5 (TC) -->

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

## Conformidade com requisitos externos
<!-- passe: 7 (REQ) -->

> Este recorte **só se aplica** quando o usuário forneceu um enunciado, rubric
> ou norma externa na chamada da skill (§7 do dossiê traz o enunciado bruto).
> Sem isso, pule — não crie o arquivo `07_conformidade_requisitos.md`.

**Cobertura de entregáveis exigidos**
- Aplicação, seção ou entregável explicitamente exigido pelo enunciado mas
  ausente do relatório.
- Elemento estrutural exigido por norma (ex.: Abstract em inglês, seção de
  limitações) mas ausente, mesmo que o documento seja internamente coerente
  sem ele.

**Critérios de rubric não atendidos**
- Critério de avaliação explícito (ex.: "comparação com pelo menos 2 trabalhos
  relacionados") sem evidência de que foi atendido no texto.

**Prioridade sobre o padrão interno**
- Quando o requisito externo conflita com o padrão que o documento já segue de
  forma coerente (ex.: enunciado pede citação IEEE, documento usa ABNT em
  tudo), **o requisito externo prevalece** — sinalizar como não conformidade,
  não como violação de um padrão interno legítimo.

**Se todos os requisitos fornecidos forem atendidos**
- Não crie o arquivo `07_conformidade_requisitos.md` (mesma regra de não
  criar arquivos vazios). Uma nota breve confirmando quais requisitos foram
  checados e atendidos pode abrir o arquivo **apenas quando ele já existe**
  por haver ao menos um requisito não atendido — essa nota não é um item
  formal (sem ID, sem severidade); só requisitos não atendidos viram itens.
