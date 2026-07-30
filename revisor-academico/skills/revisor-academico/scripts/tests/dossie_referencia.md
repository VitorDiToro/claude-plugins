# §1 Manifesto de arquivos

### Arquivos no manifesto (2)
- `main.tex`
- `capitulos/cap1.tex`

### Arquivos órfãos (.tex existentes no projeto, mas não alcançados a partir do arquivo principal)
- `capitulos/orfao.tex`

### Alvos de \input/\include não resolvidos
(nenhum alvo não resolvido)

### Arquivo principal
Um arquivo principal (`\documentclass` + `\begin{document}`) foi identificado com clareza; o manifesto e o diff de órfãos acima são confiáveis.

# §2 Perfil de padrão do documento

## Perfil de padrão do documento

### Especificadores de float
Pacote `float` carregado:
main.tex:7:\usepackage{float}

### Mecanismo de siglas
Ocorrências de comandos de acrônimo (\ac, \acs, \acl, \acf, \acp): 0
Pacote `acronym`/`acro`:
(não encontrado)
Padrões de expansão manual '(SIGLA)': 1

### Estilo de citação/bibliografia
main.tex:19:\bibliographystyle{plain}
      2 \cite{

### Convenção de prefixo de rótulo
      1 fig

### Estilo de tabela
\hline (manual): 0
booktabs (\toprule/\midrule/\bottomrule): 0

### Configuração de idioma
main.tex:8:\usepackage[brazil]{babel}

### Estilo de aspas
Retas ("): 0
Tipográficas (`` ou ''): 0

### Tamanho por arquivo (contagem bruta de palavras)
249 capitulos/cap1.tex
99 main.tex
56 capitulos/orfao.tex

### Sinais de padrão institucional
Sinais de INATEL:
Histórico de Atualizações:
(não encontrado)
Seção "Conclusão":
(não encontrado)
Acrônimos com `printonlyused`:
(não encontrado)
Sinais de NBR10719/PUC:
Seção "Resumo":
(não encontrado)
Seção "Considerações finais":
(não encontrado)
Seção "Glossário":
(não encontrado)
"Folha de rosto":
(não encontrado)

# §3 Classificação normativa

**Classificação normativa:** nenhum reconhecido

_Base da classificação (sinais de padrão institucional de §2): nenhum sinal de padrão institucional (nem INATEL, nem NBR10719/PUC) foi encontrado no corpus._

# §4 Análise textual do documento

## Análise textual do documento

### Palavras mais frequentes (top 30, sem stopwords)
7	sistema
4	desempenho
4	figure
4	trabalho
3	proposto
3	utiliza
2	api
2	avaliar
2	comunicacao
2	conforme
2	descrito
2	desenvolvimento
2	document
2	experimental
2	fig
2	figura
2	grafico
2	metodologia
2	presente
2	processamento
1	abordagem
1	abrangente
1	acelerou
1	acima
1	adiante
1	agil
1	ambiente
1	anterior
1	apenas
1	aplicacoes

### Expressões mais frequentes (2 a 4 palavras, top 20)
4	do sistema
3	desempenho do sistema
3	do sistema proposto
3	utiliza uma
2	avaliar o desempenho do
2	de desempenho
2	desempenho do sistema proposto
2	experimental para avaliar o
2	metodologia experimental para avaliar
2	o desempenho do sistema
2	o presente trabalho utiliza
2	o sistema
2	para avaliar o desempenho
2	presente trabalho utiliza uma
2	trabalho utiliza uma metodologia
2	uma metodologia experimental para
2	utiliza uma metodologia experimental
1	a figura fig naoexiste
1	a interface de programacao
1	a operacao continua do

### Frases repetidas ou quase-repetidas (boilerplate)
_Divisão de frase aproximada — sinal de apoio, não medida exata; o julgamento do revisor decide._

- **2 ocorrências** — capitulos/cap1.tex:33; capitulos/cap1.tex:5
  > O presente trabalho utiliza uma metodologia experimental para avaliar o desempenho do sistema proposto.

### Frases mais longas (prolixidade)
_Divisão de frase aproximada — sinal de apoio, não medida exata; o julgamento do revisor decide._
_Frases com mais de 45 palavras:_
- **58 palavras** — capitulos/cap1.tex:13
  > Este trabalho descreve, de maneira detalhada e abrangente, o desenvolvimento de um sistema completo de aquisicao, processamento, armazenamento e transmissao de…

# §5 Candidatos objetivos por categoria

## Termos estrangeiros sem itálico (candidatos)

_Sinal objetivo sobre glossário fixo — o revisor decide se cada ocorrência é vício real ou exceção legítima (nome próprio, marca, citação). Nomes próprios e marcas conhecidas já são ignorados automaticamente._


- **framework** (1 sem itálico) — nenhuma ocorrência usa itálico (1 no total)
  - `capitulos/cap1.tex:9` — `framework`

## Referências cruzadas (\ref/\label) — candidatos

_Sinais objetivos sobre `\label`/`\ref` (e menções textuais a apêndice/anexo) — casamento de chaves, duplicatas, rótulos frágeis. **Não** cobre `.bib`/`\cite` (isso é do `bib_check`). O revisor decide se cada candidato é vício real ou uma exceção legítima (ex.: rótulo intencionalmente não referenciado)._

### Rótulos órfãos (`\label` nunca referenciado)
- `capitulos/cap1.tex:21` — rótulo `fig:grafico` (`\label`) nunca é referenciado por `\ref`/`\eqref`/`\autoref`/`\Cref`/`\cref`

### Referências quebradas (sem `\label` correspondente)
- `capitulos/cap1.tex:15` — `fig:naoexiste` não tem `\label` correspondente

## Verificação de bibliografia (candidatos)

_Sinais objetivos e mecânicos sobre os arquivos `.bib` — presença de campos, formato, casamento com `\cite`. **Não** avaliam se a fonte é apropriada, atual ou confiável (isso é julgamento de conteúdo, fora do escopo). O revisor decide o que acatar._

### Citações sem entrada no `.bib`
- `capitulos/cap1.tex:15` — `\cite{chaveFantasma}` não tem entrada em nenhum `.bib`

### Entradas nunca citadas (órfãs)
- `refs.bib:8` — entrada `jones2019` (`@book`) nunca é citada

## Floats, imagens e tabelas — candidatos

_Sinais objetivos sobre `\includegraphics` (existência de arquivo e reuso), ambientes `figure`/`table` (`\caption`/`\label` ausentes), `tabular` extensa (candidata a `longtable`, limiar de 30 quebras de linha) e mistura de `\hline` com booktabs no mesmo projeto. O revisor decide se cada candidato é vício real ou uma exceção legítima._

### Imagem referenciada não encontrada
- `capitulos/cap1.tex:19` — `\includegraphics` aponta para `figuras/ausente.png`, não encontrado no projeto (testado na raiz e em `figures/`/`fig/`/`images/`/`img/`, com extensões png/pdf/jpg/jpeg/eps)

### Figura/tabela sem `\caption` ou sem `\label`
- `capitulos/cap1.tex:24` — ambiente `figure` sem `\caption` e sem `\label`

## Siglas e acrônimos — candidatos

_Sinais objetivos sobre siglas: uso em prosa antes da 1ª expansão manual, expansão manual `Nome Completo (SIGLA)` (sinalizada sempre como ponto de atenção, mesmo quando correta — frágil frente a `\ac`/pacote `acro`/`acronym`), reexpansão manual da mesma sigla e gênero gramatical inconsistente ("a API" vs "o API"). São candidatos, não vereditos: o revisor decide se cada um é vício real ou uma exceção legítima._

### Sigla usada antes da 1ª expansão
- `capitulos/cap1.tex:7` — sigla `API` usada antes de sua 1ª expansão manual (em `capitulos/cap1.tex:29`)

### Expansão manual (frágil frente a `\ac`/pacote de acrônimos)
- `capitulos/cap1.tex:29` — expansão manual `Interface de Programacao de Aplicacoes (API)` — sinalizar sempre como ponto de atenção, mesmo quando está correta (frágil frente a `\ac`/pacote `acro`/`acronym`)

## Léxico, crase e formatos — candidatos

_Sinais objetivos de léxico: superlativos/marketing e coloquialismos (lista curada), padrões conhecidos de erro de crase, inconsistência de separador decimal e grafias divergentes do mesmo termo. Candidatos, não vereditos -- o revisor decide se cada ocorrência é vício real ou um uso legítimo (ex.: citação direta, termo técnico)._

### Superlativos, marketing e coloquialismos

- **inovadora** (marketing/superlativo, 1 ocorrência)
  - `capitulos/cap1.tex:11` — `inovadora`

## Ortografia (hunspell pt_BR)

(script spell_check.py falhou: hunspell (ou o dicionário pt_BR) não foi encontrado neste ambiente.)


# §6 Corpus normalizado

_Frases da prosa (comandos/comentários LaTeX removidos), extraídas do corpus do manifesto e ancoradas à sua localização de origem -- insumo bruto para a passada de revisão, não uma lista de achados._

- `main.tex:6` — article float babel
- `main.tex:15` — document
- `main.tex:17` — capitulos/cap1
- `main.tex:19` — plain refs
- `main.tex:22` — document
- `capitulos/cap1.tex:3` — Capitulo Um
- `capitulos/cap1.tex:5` — O presente trabalho utiliza uma metodologia experimental para avaliar o desempenho do sistema proposto.
- `capitulos/cap1.tex:7` — O sistema utiliza uma API para comunicacao entre os modulos internos, permitindo a troca de mensagens em tempo real.
- `capitulos/cap1.tex:9` — O projeto foi implementado com o auxilio de um framework de desenvolvimento agil, o que acelerou o ciclo de testes.
- `capitulos/cap1.tex:11` — Trata-se de uma abordagem inovadora para o processamento digital de sinais, conforme descrito na literatura correlata smith2020 .
- `capitulos/cap1.tex:13` — Este trabalho descreve, de maneira detalhada e abrangente, o desenvolvimento de um sistema completo de aquisicao, processamento, armazenamento e transmissao de dados provenientes de sensores distribuidos ao longo de uma rede de comunicacao sem fio, considerando aspectos de desempenho, confiabilidade, seguranca da informacao e eficiencia energetica durante toda a operacao continua do sistema proposto pelos autores deste trabalho.
- `capitulos/cap1.tex:15` — Conforme mostra a Figura fig:naoexiste , o sistema apresenta melhorias significativas em relacao a versao anterior, um resultado tambem relatado por outro autor chaveFantasma .
- `capitulos/cap1.tex:17` — figure figuras/ausente.png Grafico de desempenho do sistema fig:grafico figure
- `capitulos/cap1.tex:24` — figure Uma segunda figura, apresentada apenas como texto ilustrativo, sem legenda e sem rotulo associado.
- `capitulos/cap1.tex:27` — figure
- `capitulos/cap1.tex:29` — Mais adiante, convem esclarecer que a Interface de Programacao de Aplicacoes (API) e o mecanismo central descrito acima.
- `capitulos/cap1.tex:31` — O experimeto de validacao foi conduzido em ambiente controlado de laboratorio.
- `capitulos/cap1.tex:33` — O presente trabalho utiliza uma metodologia experimental para avaliar o desempenho do sistema proposto.
