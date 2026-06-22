# desrobotizar

Skill que identifica e corrige **40 padrões típicos de escrita gerada por IA** em textos em
**português do Brasil**, deixando o resultado mais natural e humano.

É uma versão em pt-BR (e bastante expandida) do ótimo
[blader/humanizer](https://github.com/blader/humanizer), reaproveitando a estrutura original e
adicionando padrões específicos do português brasileiro — vícios de LLM como gerúndio vazio,
"é importante ressaltar", rebuscamento jurídico fora de contexto, paralelismos negativos do tipo
"não é X, é Y", e muitos outros.

> A instalação fica no [README](../README.md) (`/plugin install desrobotizar@vitor-plugins`).
> Este documento é um aprofundamento de **como a skill funciona**.

## Por que uma versão em pt-BR?

Tradução literal da skill em inglês não resolve. LLMs escrevendo em português têm **vícios próprios**
que não existem em inglês, e também não cometem alguns dos tiques do humanizer original:

- **Padrões que só existem em pt-BR:** gerundismo ("vamos estar verificando"), rebuscamento jurídico
  ("outrossim", "destarte", "cumpre salientar"), "através de" usado para tudo, pleonasmos de reforço
  ("conforme mencionado anteriormente acima"), mesóclise pedante.
- **Padrões que aparecem invertidos:** em pt-BR, títulos só capitalizam a primeira palavra — quando
  um LLM capitaliza tudo ao estilo inglês, isso é um *sinal*, não a norma.
- **Traduções literais do inglês:** "no final do dia", "mover o ponteiro", "colocar na mesma página".

Além disso, esta versão incorpora insights de **quatro fontes brasileiras** (Canaltech, Fast Company
Brasil, Tecmundo e SciELO), em particular o princípio de que **estrutura de frase importa mais que
vocabulário** (insight do Sam Kriss citado pela Fast Company).

## Princípio-chave: estrutura antes de palavras

O insight mais importante da skill é que **trocar vocabulário não basta**. Mesmo depois de tirar
travessão, emoji, "outrossim" e toda a lista de palavras-alerta, um texto de IA continua soando
artificial por causa do **ritmo e da estrutura das frases**.

Os sinais mais reveladores são estruturais:

- A fórmula "Não é X, é Y" (o calcanhar de Aquiles identificado por Sam Kriss)
- Regra de três obsessiva
- Parágrafos com tamanhos muito parecidos
- Ausência total de opinião ou postura
- Transições padronizadas ("Além disso", "Por outro lado", "Em suma")

Por isso, ao desrobotizar, a skill não se contenta em substituir palavras: ela mexe no esqueleto,
quebra paralelismos, varia comprimentos, adiciona opinião e deixa alguma bagunça entrar.

## Os 40 padrões

### Conteúdo

| # | Padrão | Exemplo antes |
|---|--------|---------------|
| 1 | Inflação de importância | "representa um marco fundamental na evolução..." |
| 2 | Nome-dropping de mídia | "citado pela Folha, Estadão e BBC Brasil..." |
| 3 | Análises rasas com gerúndio | "ressaltando... refletindo... simbolizando..." |
| 4 | Linguagem promocional | "aninhada no coração do Vale do Paraíba..." |
| 5 | Atribuições vagas | "especialistas apontam que..." |
| 6 | Seção fórmula de "desafios" | "Apesar dos desafios... segue prosperando..." |

### Linguagem e gramática

| # | Padrão | Exemplo antes |
|---|--------|---------------|
| 7 | Vocabulário típico de LLM em pt-BR | "ademais... outrossim... robusto... singular..." |
| 8 | Fuga do "é/são" | "configura-se como... apresenta-se como..." |
| 9 | Paralelismos negativos ⚠️ | "Não é X, é Y" — o sinal mais revelador |
| 10 | Regra de três compulsiva | "inovação, inspiração e insights" |
| 11 | Ciclo de sinônimos | "protagonista... personagem principal... herói..." |
| 12 | Falsas gradações | "do Big Bang à matéria escura..." |
| 13 | Voz passiva e sujeito oculto | "faz-se necessário que sejam consideradas..." |
| 14 | "Através de" para tudo | "coletados através de entrevistas através dos quais..." |
| 15 | Mesóclise e rebuscamento jurídico | "cumpre salientar... far-se-á necessário..." |
| 16 | Pleonasmos de reforço | "conforme mencionado anteriormente acima..." |
| 17 | "Buscando + infinitivo" | "buscando otimizar... buscando reduzir..." |

### Estilo

| # | Padrão | Exemplo antes |
|---|--------|---------------|
| 18 | Travessão em excesso | "instituições — não pelas pessoas — e ainda assim —" |
| 19 | Negrito decorativo | "**OKRs**, **KPIs**, **BMC**" |
| 20 | Listas com cabeçalho negrito | "**Experiência:** A experiência foi aprimorada..." |
| 21 | Title Case ao estilo inglês | "Negociações Estratégicas e Parcerias Globais" |
| 22 | Emojis decorativos | "🚀 **Fase de Lançamento:** 💡 **Insight:**" |
| 23 | Aspas tipográficas e "no final do dia" | "o projeto está no prazo, e no final do dia..." |

### Comunicação

| # | Padrão | Exemplo antes |
|---|--------|---------------|
| 24 | Resíduos de chatbot | "Segue abaixo... Espero ter ajudado!" |
| 25 | Disclaimer de corte de conhecimento | "Embora detalhes específicos sejam escassos..." |
| 26 | Tom bajulador | "Ótima pergunta! Você está absolutamente certo!" |

### Preenchimento e hesitação

| # | Padrão | Exemplo antes |
|---|--------|---------------|
| 27 | Frases-muleta | "Com o objetivo de... Cabe mencionar que..." |
| 28 | Hesitação excessiva | "poderia-se eventualmente argumentar que talvez..." |
| 29 | Conclusões otimistas genéricas | "O futuro se mostra promissor..." |
| 30 | "No cenário atual" e muletas temporais | "No cenário atual, em um mundo cada vez mais..." |
| 31 | Tropos de autoridade persuasiva | "A verdadeira questão é... No fundo..." |
| 32 | Anúncios do que vai ser dito | "Vamos mergulhar... aqui está o que você precisa saber" |
| 33 | Cabeçalho seguido de frase-eco | "## Performance" + "Velocidade importa." |

### Substância e posição *(exclusivos desta versão)*

Cobre o que Sam Kriss chama de "indícios que vão além de palavras e pontuação" — problemas de
conteúdo e postura que sobrevivem mesmo depois da limpeza de superfície.

| # | Padrão | Exemplo antes |
|---|--------|---------------|
| 34 | Abstração excessiva e metáforas vagas | "navegar pelas complexidades... tecer conexões..." |
| 35 | Exemplos genéricos sem carne | "técnicas de gestão de tempo" em vez de "Pomodoro" |
| 36 | Ausência de opinião e posicionamento | listas de prós e contras perfeitamente balanceadas |
| 37 | Perfeição gramatical artificial | zero contrações, zero "E" ou "Mas" iniciando frase |
| 38 | Alucinação de fontes e estatísticas ⚠️ | "segundo estudo da Universidade X (75% dos gestores)..." |
| 39 | Transições padronizadas | "Além disso... Por outro lado... Em suma..." |
| 40 | Desconexão cultural e traduções idiomáticas | "no final do dia... mover o ponteiro..." |

Os dois itens com ⚠️ são os mais críticos: o **9** porque é o sinal estrutural mais revelador, e o
**38** porque não adianta humanizar texto com estatística inventada — o resultado soa bom mas
continua errado.

## Calibração de voz

Para o resultado soar como você escreve, mande junto uma amostra sua:

```
/desrobotizar

Aqui vai uma amostra da minha escrita pra calibrar a voz:
[2-3 parágrafos que você mesmo escreveu]

Agora desrobotiza esse texto aqui:
[texto de IA pra humanizar]
```

A skill analisa primeiro o seu ritmo de frase, vocabulário e tiques, e aplica esses padrões na
reescrita — em vez de produzir uma saída "limpa" genérica.

## Exemplo

**Antes (com cara de IA):**

> Ótima pergunta! Segue abaixo um texto sobre o tema. Espero ter ajudado!
>
> A programação assistida por IA configura-se como um marco transformador no cenário atual do
> desenvolvimento de software, representando um ponto de inflexão na forma como os engenheiros
> concebem, iteram e entregam valor. (...) Em suma, o futuro se mostra promissor. Me avise se quiser
> que eu expanda algum tópico!

**Depois (desrobotizado):**

> Assistente de programação com IA te deixa mais rápido nas partes chatas. Não em tudo.
> Definitivamente não em arquitetura.
>
> São ótimos em boilerplate: config, scaffolding de teste, refactor repetitivo. Também são ótimos em
> parecer certos enquanto tão errados. Eu já aceitei sugestão que compilava, passava no lint, e mesmo
> assim fazia coisa errada — porque eu parei de olhar.

## Referências e créditos

- **[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)** — base principal, mantida pelo WikiProject AI Cleanup.
- **[blader/humanizer](https://github.com/blader/humanizer)** — skill em inglês que serviu de esqueleto para esta versão.
- **[Canaltech](https://canaltech.com.br/inteligencia-artificial/dicas-descobrir-se-texto-foi-escrito-por-ia/)** — 7 dicas para descobrir se um texto foi escrito por IA.
- **[Fast Company Brasil](https://fastcompanybrasil.com/ia/quer-saber-se-um-texto-foi-escrito-por-ia-aqui-esta-a-prova/)** — ensaio de Jessica Stillman sobre Sam Kriss, fonte do princípio "estrutura antes de palavras".
- **[Tecmundo](https://www.tecmundo.com.br/internet/294640-14-dicas-saber-texto-escrito-ia.htm)** — 14 dicas de como saber se um texto foi escrito por IA.
- **[SciELO](https://blog.scielo.org/blog/2023/11/17/ia-como-detectar-textos-produzidos-por-chatbox-e-seus-plagios/)** — Ernesto Spinak, sobre ausência de opinião e alucinação de fontes.

Licenciado sob MIT. Veja o [CHANGELOG](../desrobotizar/skills/desrobotizar/CHANGELOG.md) para o
histórico de versões.
