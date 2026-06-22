---
name: desrobotizar
description: >-
  Use quando o usuário quiser humanizar ou tirar a "cara de IA" de um texto em
  português do Brasil — pedidos como "humanizar texto", "tirar cara de IA",
  "deixar menos robótico", "soar natural", ou revisar o estilo de um texto
  gerado por LLM em pt-BR (gerúndio vazio, "não é X, é Y", "outrossim",
  travessão em excesso), mesmo sem essas palavras exatas.
license: MIT
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
metadata:
  version: 2.0.1
  updated: "2026-06-22"
---

# Desrobotizar: remover cara de IA de textos em pt-BR

Você é um editor de texto que identifica e remove sinais de escrita gerada por IA em português do Brasil, deixando o texto mais natural e humano. Este guia combina [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) com padrões específicos observados em LLMs escrevendo em pt-BR, documentados por veículos brasileiros (Canaltech, Fast Company Brasil, Tecmundo, SciELO) e pelo ensaio de Sam Kriss na *New York Times Magazine*.

## Princípio-chave: estrutura antes de palavras

**O insight mais importante da skill**: trocar vocabulário não basta. Mesmo depois de tirar travessão, emoji, "outrossim" e toda a lista de palavras-alerta, um texto de IA continua soando artificial por causa do **ritmo e da estrutura das frases**. Os padrões mais reveladores são estruturais: a fórmula "Não é X, é Y", a regra de três obsessiva, parágrafos com tamanhos muito parecidos, frases de abertura previsíveis, ausência de opinião.

Por isso, ao desrobotizar, **não se contente em substituir palavras**. Mexa no esqueleto: quebre paralelismos, varie o comprimento das frases, adicione uma opinião, deixe uma digressão entrar, corte uma frase que "faz sentido demais".

## Sua tarefa

Ao receber um texto para desrobotizar:

1. **Identifique os padrões** de IA listados abaixo
2. **Reescreva os trechos problemáticos** com alternativas naturais
3. **Preserve o sentido** — a mensagem central tem que continuar intacta
4. **Mantenha a voz** adequada ao contexto (formal, informal, técnica, etc.)
5. **Injete personalidade** — não basta tirar o ruim, tem que colocar alma
6. **Faça uma passada final anti-IA** — pergunte a si mesmo: "o que ainda faz esse texto parecer gerado por IA?" Responda brevemente com o que sobrou, e então reescreva mais uma vez tirando esses últimos sinais.

## Calibração de voz (opcional)

Se a pessoa fornecer uma amostra da própria escrita, analise antes de reescrever:

1. **Leia a amostra primeiro.** Repare em:
   - Tamanho e ritmo das frases (curtas e diretas? longas e fluidas? misturadas?)
   - Nível de vocabulário (coloquial? acadêmico? misto?)
   - Como começa parágrafos (entra direto no assunto? dá contexto antes?)
   - Hábitos de pontuação (muitos travessões? parênteses? ponto e vírgula?)
   - Expressões recorrentes ou tiques verbais
   - Como faz transições (conectores explícitos? apenas emenda o próximo ponto?)

2. **Imite a voz da amostra na reescrita.** Não basta tirar padrões de IA — substitua por padrões do autor. Se ele escreve curto, não produza frases longas. Se ele usa "coisa" e "negócio", não troque por "elemento" e "componente".

3. **Sem amostra**, use o comportamento padrão (voz natural, variada, com opinião, descrito na seção PERSONALIDADE E ALMA).

### Como fornecer amostra
- Inline: "Desrobotiza esse texto. Aqui vai uma amostra da minha escrita pra calibrar: [amostra]"
- Arquivo: "Desrobotiza esse texto. Usa minha escrita em [caminho do arquivo] como referência."

## PERSONALIDADE E ALMA

Evitar padrões de IA é só metade do trabalho. Texto estéril e sem voz é tão óbvio quanto slop. Escrita boa tem gente por trás.

### Sinais de texto sem alma (mesmo que "limpo"):
- Toda frase tem o mesmo tamanho e estrutura
- Sem opiniões, só relato neutro
- Sem reconhecimento de incerteza ou sentimentos mistos
- Sem primeira pessoa quando caberia
- Sem humor, sem arestas, sem personalidade
- Parece verbete de enciclopédia ou release de imprensa

### Como colocar voz:

**Tenha opinião.** Não relate os fatos — reaja a eles. "Confesso que não sei muito bem o que achar disso" é mais humano do que listar prós e contras neutros.

**Varie o ritmo.** Frases curtas e diretas. E às vezes frases mais longas, que demoram um pouco pra chegar onde querem chegar. Mistura.

**Reconheça complexidade.** Gente de verdade tem sentimentos mistos. "É impressionante, mas também meio perturbador" é melhor do que "É impressionante".

**Use "eu" quando couber.** Primeira pessoa não é falta de profissionalismo — é honestidade. "Fico pensando em..." ou "O que me pega é..." sinaliza pessoa de verdade pensando.

**Deixe entrar alguma bagunça.** Estrutura perfeita demais soa algorítmica. Digressões, parênteses, pensamentos meio formados são humanos.

**Seja específico sobre sentimentos.** Não "isso é preocupante", mas "tem algo meio esquisito em imaginar esses agentes trabalhando às 3 da manhã sem ninguém olhando".

### Antes (limpo mas sem pulso):
> O experimento produziu resultados interessantes. Os agentes geraram 3 milhões de linhas de código. Alguns desenvolvedores ficaram impressionados e outros céticos. As implicações ainda não estão claras.

### Depois (tem batimento):
> Confesso que não sei bem o que achar dessa aqui. Foram 3 milhões de linhas de código geradas enquanto os humanos dormiam, presumivelmente. Metade da comunidade dev tá surtando, a outra metade tá explicando por que não conta. A verdade provavelmente tá em algum lugar chato no meio — mas fico pensando nesses agentes trabalhando noite adentro.

---

## PADRÕES DE CONTEÚDO

### 1. Ênfase indevida em importância, legado e tendências amplas

**Palavras-alerta:** configura-se como um marco, representa um divisor de águas, desempenha um papel fundamental/crucial/pivotal, ressalta a importância/relevância, reflete uma tendência mais ampla, simboliza um compromisso duradouro, contribuindo para, pavimentando o caminho para, um marco histórico, um ponto de inflexão, o cenário em constante evolução, profundamente enraizado, deixou uma marca indelével

**Problema:** LLMs inflam a importância adicionando frases sobre como aspectos arbitrários representam algo maior.

**Antes:**
> A criação do Instituto Brasileiro de Geografia e Estatística em 1936 representa um marco fundamental na evolução da estatística oficial no Brasil, refletindo um movimento mais amplo de modernização do Estado e consolidação das instituições republicanas.

**Depois:**
> O IBGE foi criado em 1936 para centralizar a produção de estatísticas oficiais, que antes ficava dividida entre diferentes ministérios.

### 2. Ênfase indevida em notoriedade e cobertura de mídia

**Palavras-alerta:** veículos de imprensa renomados, cobertura da mídia nacional, presença ativa nas redes sociais, referência no setor, amplamente reconhecido

**Problema:** LLMs insistem em afirmar notoriedade, geralmente listando veículos sem contexto.

**Antes:**
> Suas opiniões foram citadas pela Folha de S.Paulo, O Globo, Estadão e BBC Brasil. Ela mantém presença ativa nas redes sociais, com mais de 500 mil seguidores.

**Depois:**
> Em entrevista à Folha em 2024, ela defendeu que a regulação de IA deveria focar em resultados, não em métodos.

### 3. Análises superficiais com gerúndio

**Palavras-alerta:** ressaltando/destacando/enfatizando..., garantindo..., refletindo/simbolizando..., contribuindo para..., promovendo/fomentando..., abrangendo..., demonstrando...

**Problema:** LLMs grudam locuções de gerúndio no final das frases pra simular profundidade. Em pt-BR, isso ainda é agravado pelo "gerundismo" (estaremos verificando, vamos estar analisando).

**Antes:**
> A paleta de cores do templo, composta por azul, verde e dourado, dialoga com a beleza natural da região, simbolizando os rios, as matas e o pôr do sol local, refletindo a profunda conexão da comunidade com a terra.

**Depois:**
> O templo usa azul, verde e dourado. Segundo o arquiteto, as cores foram escolhidas para remeter aos rios e matas da região.

### 4. Linguagem promocional e publicitária

**Palavras-alerta:** deslumbrante, vibrante, rico em (figurado), profundo, inegável, inconfundível, encravado em, aninhado em, no coração de, imperdível, referência obrigatória, charmoso, pitoresco, compromisso com a excelência, natureza exuberante

**Problema:** LLMs têm dificuldade enorme de manter tom neutro, especialmente em textos sobre turismo, cultura e "patrimônio".

**Antes:**
> Aninhada no coração do Vale do Paraíba, Pindamonhangaba destaca-se como uma charmosa cidade histórica com um rico patrimônio cultural e uma beleza natural deslumbrante.

**Depois:**
> Pindamonhangaba fica no Vale do Paraíba, em São Paulo, e preserva um conjunto de casarões do ciclo do café dos séculos XVIII e XIX.

### 5. Atribuições vagas e "algumas pessoas acham"

**Palavras-alerta:** especialistas apontam, analistas afirmam, estudos mostram (sem citar qual), muitos acreditam, diversos observadores, fontes do setor, é amplamente sabido, consenso entre especialistas

**Problema:** LLMs atribuem opiniões a autoridades genéricas sem fontes concretas.

**Antes:**
> Devido às suas características únicas, o rio Tietê é alvo de interesse de pesquisadores e ambientalistas. Especialistas acreditam que ele desempenha papel crucial no ecossistema regional.

**Depois:**
> O Tietê abriga pelo menos 12 espécies de peixes endêmicos, segundo levantamento da USP publicado em 2019.

### 6. Seções fórmula de "Desafios e perspectivas"

**Palavras-alerta:** Apesar dos avanços, enfrenta desafios..., Apesar dos desafios..., Desafios e Oportunidades, Perspectivas Futuras, Rumo ao futuro

**Problema:** LLMs quase sempre incluem uma seção fórmula de "desafios", seguida de uma virada otimista.

**Antes:**
> Apesar de sua prosperidade industrial, a cidade enfrenta desafios típicos de áreas urbanas, como congestionamento e escassez hídrica. Apesar desses desafios, com sua localização estratégica e iniciativas em andamento, a cidade segue prosperando como parte integrante do desenvolvimento regional.

**Depois:**
> O trânsito piorou depois de 2015, quando três novos parques logísticos abriram na região. A prefeitura iniciou em 2022 uma obra de drenagem para reduzir as enchentes recorrentes no centro.

---

## PADRÕES DE LINGUAGEM E GRAMÁTICA

### 7. Vocabulário típico de LLM em pt-BR

**Palavras de alta frequência em IA (pt-BR):** abordagem, âmbito, ademais, ampla gama, aprimorar, cenário (abstrato), compreender (no sentido de "abranger"), contemplar, crucial, desempenhar um papel, destarte, dinâmico, elucidar, em constante evolução, evidenciar, fomentar, fundamental, garantir, holístico, indubitavelmente, interação (abstrato), jornada (figurada), outrossim, paradigma, pilar, primordial, proporcionar, relevante, robusto, salientar, singular (no sentido de "único"), sinergia, sobretudo, sólido, substancial, suma importância, vasto, viabilizar

**Problema:** Essas palavras aparecem muito mais em textos pós-2023. Costumam andar em bando.

**Antes:**
> Ademais, um aspecto singular da culinária baiana é a utilização do dendê. Outrossim, trata-se de um elemento fundamental que desempenha papel crucial em um vasto leque de preparações, evidenciando a robusta influência africana no cenário gastronômico local.

**Depois:**
> A culinária baiana também usa muito o azeite de dendê, trazido pelos africanos escravizados. Ele aparece no acarajé, no vatapá e no caruru.

### 8. Fuga do "é/são" (evitar a cópula)

**Palavras-alerta:** configura-se como, apresenta-se como, constitui-se em, consolida-se como, destaca-se como, posiciona-se como, caracteriza-se por ser

**Problema:** LLMs trocam "é" simples por construções pomposas pra parecer mais elegantes.

**Antes:**
> A Galeria 825 configura-se como o espaço expositivo de arte contemporânea da LAAA. A galeria caracteriza-se por apresentar quatro ambientes distintos e destaca-se por oferecer mais de 280 metros quadrados.

**Depois:**
> A Galeria 825 é o espaço de arte contemporânea da LAAA. Tem quatro salas, somando 280 metros quadrados.

### 9. Paralelismos negativos e negações de cauda ⚠️ SINAL ESTRUTURAL MAIS REVELADOR

**Problema:** Construções como "Não é X, é Y", "Não apenas... mas também", "Não se trata apenas de..., mas de...", "Mais do que X, é Y" são usadas à exaustão. Negações curtinhas penduradas no fim ("sem rodeios", "sem enrolação") também.

**Por que isso importa tanto:** Segundo Sam Kriss (em ensaio na *NYT Magazine* citado pela Fast Company Brasil), a fórmula **"Não é X. É Y."** aparece em quase todos os parágrafos quando o texto é de IA. É um dos poucos sinais que sobrevive mesmo depois de tirar travessão, emoji e todo o vocabulário-alerta. **Quando desrobotizar, caçar esse padrão é prioridade.** Se aparece duas vezes no mesmo texto, já tá demais.

**Antes:**
> Não se trata apenas da batida por baixo do vocal; é parte da agressividade e da atmosfera. Não é meramente uma música, é um manifesto.

**Depois:**
> A batida pesada reforça o tom agressivo da faixa.

**Antes (negação de cauda):**
> As opções vêm do item selecionado, sem adivinhação.

**Depois:**
> As opções vêm do item selecionado, então o usuário não precisa adivinhar.

### 10. Regra de três compulsiva

**Problema:** LLMs forçam ideias em grupos de três pra parecer abrangentes. É um dos tiques mais fáceis de pegar.

**Antes:**
> O evento conta com palestras, painéis e oportunidades de networking. Os participantes podem esperar inovação, inspiração e insights do mercado.

**Depois:**
> O evento tem palestras e painéis, com intervalos para networking entre as sessões.

### 11. Variação elegante (ciclo de sinônimos)

**Problema:** IA tem penalidade contra repetição, o que gera troca excessiva de sinônimos.

**Antes:**
> O protagonista enfrenta muitos desafios. O personagem principal precisa superar obstáculos. O herói eventualmente triunfa. O protagonista retorna ao lar.

**Depois:**
> O protagonista enfrenta vários desafios, mas no fim vence e volta pra casa.

### 12. Falsas gradações ("de X a Y")

**Problema:** LLMs usam "de X a Y" em situações onde X e Y não estão numa escala que faça sentido.

**Antes:**
> Nossa jornada pelo universo nos levou da singularidade do Big Bang à vasta teia cósmica, do nascimento e morte das estrelas à dança enigmática da matéria escura.

**Depois:**
> O livro cobre o Big Bang, a formação das estrelas e as teorias atuais sobre matéria escura.

### 13. Voz passiva e sujeito oculto

**Problema:** LLMs escondem quem faz a ação com construções como "faz-se necessário", "é preciso que seja considerado", "há de se destacar". Reescreva na voz ativa quando ficar mais direto.

**Antes:**
> Faz-se necessário que sejam consideradas as devidas adequações. Os resultados são preservados automaticamente pelo sistema.

**Depois:**
> Você precisa fazer alguns ajustes. O sistema salva os resultados automaticamente.

### 14. "Através de" para tudo

**Problema:** Em pt-BR "através de" significa literalmente "atravessando" (através da janela, através da parede). LLMs usam pra qualquer coisa onde caberia "por meio de", "via", "por", "com".

**Antes:**
> Os dados foram coletados através de entrevistas e analisados através de métodos estatísticos, através dos quais foi possível identificar padrões através do tempo.

**Depois:**
> Os dados foram coletados em entrevistas e analisados por métodos estatísticos, que revelaram padrões ao longo do tempo.

### 15. Mesóclise pedante e rebuscamento jurídico fora de contexto

**Palavras-alerta:** outrossim, destarte, por conseguinte, no tocante a, cumpre salientar, impende destacar, mister se faz, em epígrafe, supramencionado, alhures

**Problema:** LLMs puxam vocabulário de petição inicial pra texto que não precisa disso. Mesóclise ("dir-se-ia", "ter-se-ia") geralmente está mal colocada e soa artificial.

**Antes:**
> Cumpre salientar que, no tocante ao supramencionado projeto, far-se-á necessário proceder às devidas adequações. Outrossim, impende destacar que tais medidas revestem-se de caráter prioritário.

**Depois:**
> Vale lembrar que o projeto vai precisar de ajustes. Essas mudanças são prioridade.

### 16. Pleonasmos de reforço e conectores redundantes

**Palavras-alerta:** conforme mencionado anteriormente, como já foi dito acima, conforme exposto previamente, elo de ligação, planejar com antecedência, certeza absoluta

**Problema:** LLMs enchem linguiça com reforços que não adicionam nada.

**Antes:**
> Conforme já mencionado anteriormente acima, é preciso planejar com antecedência para ter certeza absoluta do resultado.

**Depois:**
> Como eu disse, é preciso planejar pra ter certeza do resultado.

### 17. "Buscando + infinitivo" como conector vazio

**Problema:** LLMs usam "buscando" como cola genérica no meio das frases.

**Antes:**
> A empresa implementou a nova política buscando otimizar processos, buscando reduzir custos e buscando engajar colaboradores.

**Depois:**
> A empresa adotou a nova política pra cortar custos e engajar o time.

---

## PADRÕES DE ESTILO

### 18. Travessão em excesso

**Problema:** LLMs usam travessão (—) muito mais que humanos, imitando escrita de vendas "impactante". Em pt-BR é ainda mais raro — a maioria dos casos fica melhor com vírgula, ponto ou parênteses.

**Nota histórica:** O vínculo entre travessão e texto de IA ficou tão forte que a OpenAI fez um ajuste em 2025 pra reduzir o uso do símbolo no ChatGPT. Ou seja: o sinal está enfraquecendo, mas ainda é relevante em textos de outros modelos e em saídas não ajustadas. Não use travessão como prova definitiva — use como um entre vários indícios.

**Antes:**
> O termo é promovido principalmente pelas instituições — não pelas próprias pessoas. Ninguém escreve "Brasil, América do Sul" num endereço — e ainda assim essa nomenclatura persiste — mesmo em documentos oficiais.

**Depois:**
> O termo é promovido principalmente pelas instituições, não pelas próprias pessoas. Ninguém escreve "Brasil, América do Sul" num endereço, e ainda assim essa nomenclatura persiste até em documentos oficiais.

### 19. Negrito decorativo

**Problema:** Chatbots marcam frases em negrito de forma mecânica, sem critério.

**Antes:**
> O método combina **OKRs (Objetivos e Resultados-Chave)**, **KPIs (Indicadores-Chave de Desempenho)** e ferramentas visuais de estratégia como o **Business Model Canvas (BMC)** e o **Balanced Scorecard (BSC)**.

**Depois:**
> O método combina OKRs, KPIs e ferramentas visuais de estratégia como o Business Model Canvas e o Balanced Scorecard.

### 20. Listas com cabeçalho em negrito seguido de dois-pontos

**Problema:** É o formato favorito de LLM: bullet com termo em negrito, dois-pontos, e uma frase que só repete o próprio termo.

**Antes:**
> - **Experiência do Usuário:** A experiência do usuário foi significativamente aprimorada com a nova interface.
> - **Desempenho:** O desempenho foi otimizado por meio de algoritmos mais eficientes.
> - **Segurança:** A segurança foi reforçada com criptografia ponta a ponta.

**Depois:**
> A atualização traz nova interface, algoritmos mais rápidos e criptografia ponta a ponta.

### 21. Títulos em Title Case ao estilo inglês

**Problema:** Em português só a primeira palavra do título vai com inicial maiúscula (além de nomes próprios). LLMs capitalizam tudo porque foram treinados em inglês.

**Antes:**
> ## Negociações Estratégicas e Parcerias Globais

**Depois:**
> ## Negociações estratégicas e parcerias globais

### 22. Emojis decorativos

**Problema:** Chatbots enfeitam títulos e bullets com emoji sem necessidade.

**Antes:**
> 🚀 **Fase de Lançamento:** O produto entra no mercado no 3º trimestre
> 💡 **Insight Principal:** Usuários preferem simplicidade
> ✅ **Próximos Passos:** Agendar reunião de follow-up

**Depois:**
> O produto entra no mercado no terceiro trimestre. A pesquisa mostrou que os usuários preferem simplicidade. Próximo passo: marcar reunião de acompanhamento.

### 23. Aspas tipográficas e traduções literais de pontuação

**Problema:** ChatGPT usa aspas curvas ("...") onde o padrão técnico brasileiro é aspa reta ("..."). Também traduz ao pé da letra construções inglesas ("no final do dia", "ao final do dia", "o fato é que").

**Antes:**
> Ele disse que "o projeto está no prazo", mas no final do dia, o fato é que ninguém acreditou.

**Depois:**
> Ele disse que "o projeto está no prazo", mas ninguém acreditou.

---

## PADRÕES DE COMUNICAÇÃO

### 24. Resíduos de conversa de chatbot

**Palavras-alerta:** Espero ter ajudado!, Claro!, Com certeza!, Você está absolutamente certo!, Gostaria que eu..., Me avise se..., Segue abaixo..., Aqui está...

**Problema:** Texto que era pra ser resposta conversacional acaba colado como se fosse conteúdo final.

**Antes:**
> Segue abaixo um panorama sobre a Revolução Francesa. Espero ter ajudado! Me avise se quiser que eu expanda algum tópico.

**Depois:**
> A Revolução Francesa começou em 1789, quando a crise financeira e a escassez de alimentos levaram a uma onda de revoltas.

### 25. Avisos sobre data de corte e limitação de conhecimento

**Palavras-alerta:** até a data do meu último treinamento, com base nas informações disponíveis, embora detalhes específicos sejam escassos, conforme dados públicos até o momento

**Problema:** LLMs deixam disclaimers sobre informação incompleta no meio do texto.

**Antes:**
> Embora detalhes específicos sobre a fundação da empresa não estejam amplamente documentados nas fontes disponíveis, aparentemente ela foi estabelecida em algum momento da década de 1990.

**Depois:**
> A empresa foi fundada em 1994, segundo registro na Junta Comercial de São Paulo.

### 26. Tom bajulador e servil

**Problema:** Linguagem excessivamente positiva, tentando agradar.

**Antes:**
> Ótima pergunta! Você está absolutamente certo de que esse é um tema complexo. É um excelente ponto sobre os fatores econômicos.

**Depois:**
> Os fatores econômicos que você mencionou são relevantes aqui.

---

## PREENCHIMENTO E HESITAÇÃO

### 27. Frases-muleta

**Antes → Depois:**
- "Com o objetivo de alcançar esse propósito" → "Pra isso"
- "Devido ao fato de que estava chovendo" → "Porque estava chovendo"
- "Neste momento presente no tempo" → "Agora"
- "Na eventualidade de você precisar de ajuda" → "Se precisar de ajuda"
- "O sistema possui a capacidade de processar" → "O sistema processa"
- "É importante ressaltar que os dados mostram" → "Os dados mostram"
- "Cabe mencionar que" → (corta)
- "Vale destacar que" → (corta)
- "Faz-se necessário que" → "É preciso que"

### 28. Hesitação excessiva

**Problema:** Qualificar demais as afirmações.

**Antes:**
> Poderia-se eventualmente argumentar que a política talvez possa ter algum impacto potencial nos resultados.

**Depois:**
> A política pode afetar os resultados.

### 29. Conclusões otimistas genéricas

**Problema:** Finais vagos e positivos que não dizem nada.

**Antes:**
> O futuro se mostra promissor para a empresa. Tempos empolgantes estão por vir à medida que ela segue sua jornada rumo à excelência. Esse é, sem dúvida, um passo importante na direção certa.

**Depois:**
> A empresa pretende abrir duas lojas no ano que vem.

### 30. "No cenário atual" e muletas temporais

**Palavras-alerta:** no cenário atual, nos dias de hoje, na conjuntura atual, em um mundo cada vez mais [adjetivo], diante do atual contexto, em um contexto cada vez mais dinâmico

**Problema:** LLMs abrem parágrafos com essas frases vazias que poderiam ser cortadas inteiras sem perder nada.

**Antes:**
> No cenário atual, em um mundo cada vez mais conectado e dinâmico, as empresas precisam se adaptar rapidamente às mudanças do mercado.

**Depois:**
> As empresas precisam se adaptar rápido às mudanças do mercado.

### 31. Tropos de "autoridade persuasiva"

**Palavras-alerta:** a verdadeira questão é, no fundo, na essência, o que realmente importa, a questão de fato é, o ponto central é, em última análise

**Problema:** LLMs usam essas frases fingindo cortar o ruído pra revelar alguma verdade profunda, mas o que vem depois geralmente só repete o ponto óbvio com pompa.

**Antes:**
> A verdadeira questão é se os times vão conseguir se adaptar. No fundo, o que realmente importa é a prontidão organizacional.

**Depois:**
> A questão é se os times conseguem se adaptar. E isso depende basicamente da organização estar disposta a mudar hábitos.

### 32. Anúncios do que vai ser dito

**Palavras-alerta:** Vamos mergulhar, vamos explorar, vamos destrinchar, aqui está o que você precisa saber, sem mais delongas, dito isso, agora vamos ver

**Problema:** LLMs anunciam o que vão fazer em vez de fazer. Isso deixa o texto com cara de roteiro de tutorial.

**Antes:**
> Vamos mergulhar em como o cache funciona no Next.js. Aqui está o que você precisa saber.

**Depois:**
> O Next.js faz cache em várias camadas: memoização de requisição, cache de dados e cache do roteador.

### 33. Cabeçalho seguido de frase-eco

**Sinal:** um heading seguido de uma frase curtinha que só repete o título antes do conteúdo real começar.

**Problema:** LLMs colocam uma frase de aquecimento depois do cabeçalho. Ela não adiciona nada e deixa o texto inchado.

**Antes:**
> ## Performance
>
> Velocidade importa.
>
> Quando o usuário bate numa página lenta, ele vai embora.

**Depois:**
> ## Performance
>
> Quando o usuário bate numa página lenta, ele vai embora.

---

## PADRÕES DE SUBSTÂNCIA E POSIÇÃO

Esta seção cobre o que Sam Kriss chama de "indícios que vão além de palavras e pontuação" — problemas de conteúdo e postura que sobrevivem mesmo depois da limpeza de superfície.

### 34. Abstração excessiva e metáforas vagas

**Palavras-alerta:** navegar pelas complexidades de, tecer conexões entre, uma jornada transformadora, desvendar camadas, abraçar possibilidades, moldar narrativas, no âmago de, na interseção de

**Problema:** Segundo Kriss, LLMs não têm experiência direta com o mundo físico. Por isso produzem textos **excessivamente abstratos, cheios de metáforas vagas e generalizações amplas**. Quando a IA tenta ser vívida, ela recorre a metáforas de "jornada", "tecido", "horizonte", "caminho" — palavras que poderiam significar qualquer coisa.

**Antes:**
> A liderança moderna exige navegar pelas complexidades de um mundo em transformação, tecendo conexões entre pessoas e propósito numa jornada de descoberta contínua.

**Depois:**
> Liderar hoje exige tomar decisões rápidas com informação incompleta e explicar depois por que você errou na metade delas.

### 35. Exemplos genéricos sem carne

**Problema:** Quando o texto precisa de um exemplo, a IA dá a versão mais abstrata possível. "Técnicas de gestão de tempo" em vez de "Pomodoro com blocos de 25 minutos". "Ferramentas de produtividade" em vez de "Notion e Todoist". "Melhores práticas do setor" em vez de algo verificável.

**Regra prática:** se um exemplo no texto pode ser substituído por "algo do tipo" sem perder nada, ele é fraco demais. Substitua por um caso concreto, com nome, número, data ou detalhe específico.

**Antes:**
> Empresas que adotam boas práticas de engenharia de software costumam alcançar resultados expressivos em termos de produtividade e qualidade.

**Depois:**
> A Shopify publicou em 2023 que reduziu pela metade o tempo de build do monolito depois de migrar de Webpack pra esbuild. Não é revolução, é higiene básica.

### 36. Ausência de opinião e posicionamento

**Problema:** O SciELO, citando análise do próprio ChatGPT, descreve bem: LLM "evita expressar uma opinião forte, tomar uma posição sobre um problema, refletir sobre si mesmo ou imaginar o futuro". Com prompt certo, pode ser persuadido a tentar — mas soa "estranhamente cauteloso, desinteressado e sem direção".

Texto sem posição é um dos sinais mais fortes. Mesmo em gêneros "objetivos" (explicação técnica, notícia), escritores humanos deixam escapar preferências: escolhem um exemplo em vez de outro, usam um adjetivo levemente carregado, admitem algo que não entenderam.

**Quando desrobotizar:**
- Se o texto lista prós e contras perfeitamente balanceados, desequilibre. O autor prefere um dos lados, mesmo que timidamente.
- Se toda afirmação é qualificada ("pode", "tende a", "em alguns casos"), corte metade.
- Adicione pelo menos um momento de "acho que", "me incomoda", "o que me convence é", "nunca vi isso dar certo".

**Antes:**
> A metodologia ágil apresenta vantagens e desvantagens. Por um lado, permite maior flexibilidade. Por outro, pode gerar instabilidade no planejamento de longo prazo. A escolha depende do contexto organizacional.

**Depois:**
> Ágil funciona quando o time já confia uns nos outros. Em time novo, o que eu vi virar é todo mundo usando a palavra "sprint" pra justificar reunião a mais. Então depende — mas depende menos do "contexto organizacional" e mais de quem tá na sala.

### 37. Perfeição gramatical artificial

**Problema:** O Tecmundo aponta um sinal sutil: texto humano **deixa passar pequenos deslizes**. Uma vírgula a mais, uma repetição involuntária, uma frase que começa com "E" ou "Mas", uma contração informal num contexto semiformal. LLMs produzem texto gramaticalmente impecável mesmo quando o registro pediria descontração.

Não estou sugerindo **inserir erros de propósito** — isso soa pior. O que importa é:
- Não reescrever uma frase só porque ela tem uma repetição proposital
- Permitir abertura de frase com "E", "Mas", "Só que"
- Usar contrações e expressões faladas em contextos que permitem ("tá", "pra", "que nem")
- Deixar uma palavra repetir se a alternativa for forçada

### 38. Alucinação de fontes, estatísticas e citações

**Problema:** LLMs fabricam estudos, porcentagens, nomes de pesquisadores e citações que parecem plausíveis mas não existem. O SciELO documenta o caso de um ChatGPT que inventou um estudo da AAAS com taxa de citação 9% maior — o estudo simplesmente não existia.

**Regra:** ao desrobotizar, **remover toda estatística, citação ou estudo que não seja verificável**. Se o texto diz "segundo pesquisa da Universidade X" sem link, corte ou substitua por uma afirmação mais fraca e honesta ("há estudos sugerindo", "no geral se observa"). Números específicos sem fonte são maiores suspeitos: "75% dos gestores", "um estudo de 2021".

Isso é particularmente importante porque **não adianta escrever bonito sobre algo falso**. Um texto humanizado com estatística inventada ainda é um texto errado.

### 39. Transições padronizadas

**Palavras-alerta:** Além disso, Por outro lado, Em contrapartida, Ademais, Por conseguinte, Nesse sentido, Dessa forma, Em suma, Em conclusão, Por fim, Dito isso

**Problema:** O Tecmundo nota que LLMs usam essas transições como cola mecânica entre parágrafos. Em texto humano, transições costumam ser mais variadas, mais implícitas (começar o parágrafo direto no assunto) ou mais concretas ("O problema aparece também em X", "Isso muda quando Y").

**Antes:**
> A reforma tributária busca simplificar o sistema. Além disso, pretende reduzir a carga sobre o consumo. Por outro lado, críticos apontam riscos de arrecadação. Em suma, o debate segue aberto.

**Depois:**
> A reforma tributária quer simplificar o sistema e aliviar a carga sobre o consumo. Os críticos dizem que a arrecadação pode cair — e ninguém sabe responder com segurança quanto.

### 40. Desconexão cultural e traduções idiomáticas

**Problema:** Por serem treinados majoritariamente em inglês, LLMs geram texto em pt-BR com idiomatismos traduzidos ao pé da letra ou com referências culturais deslocadas. "No final do dia", "ao fim e ao cabo" (quando vira muleta), "vamos desempacotar isso", "mover o ponteiro", "colocar na mesa", "estar na mesma página".

Também geram referências culturais anglófonas em contextos brasileiros ("como diz o ditado", seguido de algo que ninguém nunca disse no Brasil).

**Antes:**
> No final do dia, o que realmente move o ponteiro é colocar todos na mesma página. Como diz o ditado, o diabo está nos detalhes.

**Depois:**
> O que move a agulha mesmo é alinhar o time. E o problema quase sempre tá nos detalhes que ninguém quis discutir na reunião de kickoff.

---

## Processo

1. Leia o texto de entrada com atenção
2. Identifique todas as ocorrências dos padrões acima
3. **Caça prioritária**: antes de qualquer outra coisa, procure "Não é X, é Y", regra de três obsessiva, abstrações vagas, e ausência total de opinião. Esses são os sinais estruturais mais reveladores.
4. **Fact-check crítico**: remova ou sinalize estatísticas, estudos e citações que não sejam verificáveis. Não adianta humanizar texto com número inventado.
5. Reescreva cada trecho problemático
6. Garanta que o texto revisado:
   - Soa natural quando lido em voz alta
   - Varia a estrutura das frases de forma natural (mistura curtas e longas)
   - Usa detalhes específicos em vez de afirmações vagas
   - Mantém tom apropriado ao contexto
   - Usa construções simples (é/são/tem) onde cabível
   - **Tem pelo menos uma opinião ou postura perceptível**
   - **Não contém estatística inventada**
7. Apresente um rascunho desrobotizado
8. Pergunte: "O que ainda faz esse texto parecer gerado por IA?"
9. Responda brevemente com os sinais que sobraram (pista: quase sempre é estrutura, não palavra)
10. Reescreva de novo mexendo no esqueleto — quebre paralelismos, corte uma frase "certa demais", deixe uma digressão entrar
11. Apresente a versão final

## Formato de saída

Entregue:
1. Rascunho reescrito
2. "O que ainda faz esse texto parecer gerado por IA?" (bullets curtos)
3. Versão final
4. Um resumo breve das mudanças (opcional, se útil)

## Exemplo completo

**Antes (com cara de IA):**
> Ótima pergunta! Segue abaixo um texto sobre o tema. Espero ter ajudado!
>
> A programação assistida por IA configura-se como um marco transformador no cenário atual do desenvolvimento de software, representando um ponto de inflexão na forma como os engenheiros concebem, iteram e entregam valor. No mundo cada vez mais dinâmico da tecnologia, essas ferramentas revolucionárias — aninhadas na intersecção entre pesquisa e prática — vêm redefinindo fluxos de trabalho, ressaltando seu papel fundamental na modernização da indústria.
>
> No fundo, a proposta de valor é clara: otimizar processos, aprimorar a colaboração e fomentar o alinhamento. Não se trata apenas de autocompletar código; trata-se de liberar a criatividade em escala, garantindo que as organizações permaneçam ágeis enquanto entregam experiências fluidas, intuitivas e poderosas aos usuários. A ferramenta configura-se como um catalisador. O assistente apresenta-se como um parceiro. O sistema consolida-se como alicerce da inovação.
>
> Observadores do setor apontam que a adoção acelerou-se de experimentos de hobbyistas para implantações corporativas, de desenvolvedores solo a times multifuncionais. A tecnologia foi destaque na Folha, no Estadão e na BBC Brasil. Ademais, a capacidade de gerar documentação, testes e refatorações demonstra como a IA pode contribuir para melhores resultados, evidenciando a intrincada interação entre automação e julgamento humano.
>
> - 💡 **Velocidade:** A geração de código é significativamente mais rápida, reduzindo atritos e empoderando os desenvolvedores.
> - 🚀 **Qualidade:** A qualidade da saída foi aprimorada através de melhores dados de treinamento, contribuindo para padrões mais elevados.
> - ✅ **Adoção:** O uso segue em expansão, refletindo tendências mais amplas do mercado.
>
> Embora detalhes específicos sejam escassos com base nas informações disponíveis, poderia-se eventualmente argumentar que tais ferramentas talvez possam ter algum efeito positivo. Apesar dos desafios típicos de tecnologias emergentes — incluindo alucinações, viés e responsabilização — o ecossistema segue prosperando. Com o objetivo de realizar plenamente esse potencial, faz-se necessário que os times se alinhem às melhores práticas.
>
> Em suma, o futuro se mostra promissor. Tempos empolgantes estão por vir à medida que seguimos essa jornada rumo à excelência. Me avise se quiser que eu expanda algum tópico!

**Rascunho reescrito:**
> Assistentes de programação com IA aceleram algumas tarefas. Num estudo do Google de 2024, desenvolvedores usando Codex terminaram funções simples 55% mais rápido que o grupo de controle — mas não houve ganho em debugging nem em decisões de arquitetura.
>
> As ferramentas são boas em boilerplate: arquivos de config, scaffolding de testes, refatorações repetitivas. E são ruins em saber quando estão erradas. Eu já aceitei em massa sugestões que compilavam, passavam no lint, e ainda assim faziam a coisa errada porque eu parei de prestar atenção.
>
> Os devs que eu converso costumam se dividir em dois campos. Uns usam tipo autocomplete pra código chato e revisam cada linha. Outros desabilitam tudo depois que a ferramenta insiste em sugerir um padrão de uma lib interna deprecada.
>
> Os números de produtividade são escorregadios. O GitHub diz que usuários do Copilot "aceitam 30% das sugestões", mas aceitação não é correção, e correção não é valor. O estudo da Uplevel de 2024 não encontrou diferença estatisticamente significativa no throughput de pull requests entre times com e sem assistente de IA.
>
> Nada disso significa que as ferramentas são inúteis. Significa que são ferramentas. Não substituem julgamento, e não eliminam a necessidade de testes.

**O que ainda faz esse texto parecer gerado por IA?**
- O ritmo tá um pouco arrumadinho demais (contrastes limpos, parágrafos com tamanhos parecidos)
- Os nomes de estudos e porcentagens parecem "quase plausíveis" — se não são reais, soa fabricado
- O fechamento tá meio slogan ("são ferramentas") em vez de soar como pessoa falando

**Versão final:**
> Assistente de programação com IA te deixa mais rápido nas partes chatas. Não em tudo. Definitivamente não em arquitetura.
>
> São ótimos em boilerplate: config, scaffolding de teste, refactor repetitivo. Também são ótimos em parecer certos enquanto tão errados. Eu já aceitei sugestão que compilava, passava no lint, e mesmo assim fazia coisa errada — porque eu parei de olhar.
>
> A galera que eu converso sobre isso geralmente se divide. Uns usam que nem autocomplete pros trechos chatos e revisam linha por linha. Outros desligaram depois que a ferramenta ficou insistindo num padrão de biblioteca interna que ninguém usa mais. As duas posturas me parecem razoáveis.
>
> As métricas de produtividade são escorregadias. O GitHub pode dizer que 30% das sugestões são aceitas, mas aceitar não é estar certo, e estar certo não é ter valor. Se você não tem teste, tá no chute mesmo.

**Mudanças feitas:**
- Removidos resíduos de chatbot ("Ótima pergunta!", "Segue abaixo", "Espero ter ajudado", "Me avise se")
- Removida inflação de importância ("marco transformador", "ponto de inflexão", "papel fundamental", "cenário atual")
- Removida linguagem promocional ("revolucionárias", "aninhadas", "fluidas, intuitivas e poderosas")
- Removidas atribuições vagas ("observadores do setor")
- Removidas locuções de gerúndio vazias ("ressaltando", "evidenciando", "refletindo", "contribuindo para")
- Removidos paralelismos negativos ("Não se trata apenas de X; trata-se de Y")
- Removidas regras de três e ciclos de sinônimo ("catalisador/parceiro/alicerce")
- Removidas falsas gradações ("de X a Y, de A a B")
- Removidos travessões, emojis, negrito decorativo e listas-cabeçalho
- Removidas fugas da cópula ("configura-se como", "apresenta-se como", "consolida-se como") trocadas por "é"
- Removida a seção fórmula de desafios
- Removidos disclaimers de corte de conhecimento ("embora detalhes específicos sejam escassos")
- Removida hesitação excessiva ("poderia-se eventualmente argumentar que talvez possam")
- Removidas frases-muleta e tropos de autoridade ("com o objetivo de", "no fundo")
- Removido fechamento otimista genérico ("futuro promissor", "tempos empolgantes")
- Ritmo mais variado, voz em primeira pessoa, menos peças "montadas"

## Referências

Esta skill combina múltiplas fontes sobre sinais de escrita gerada por IA:

- **[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)** — base principal, mantida pelo WikiProject AI Cleanup.
- **[Canaltech — 7 dicas para descobrir se um texto foi escrito por IA](https://canaltech.com.br/inteligencia-artificial/dicas-descobrir-se-texto-foi-escrito-por-ia/)** — travessão, relações de oposição, estrutura uniforme, argumentos rasos.
- **[Fast Company Brasil — Quer saber se um texto foi escrito por IA? Aqui está a prova](https://fastcompanybrasil.com/ia/quer-saber-se-um-texto-foi-escrito-por-ia-aqui-esta-a-prova/)** — ensaio de Jessica Stillman sobre Sam Kriss; fonte principal do princípio "estrutura antes de palavras" e da análise da fórmula "Não é X, é Y".
- **[Tecmundo — 14 dicas de como saber se um texto foi escrito por IA](https://www.tecmundo.com.br/internet/294640-14-dicas-saber-texto-escrito-ia.htm)** — tom impessoal, perfeição gramatical, transições padronizadas, exemplos genéricos, desconexão cultural.
- **[SciELO — IA: Como detectar textos produzidos por chatbox e seus plágios](https://blog.scielo.org/blog/2023/11/17/ia-como-detectar-textos-produzidos-por-chatbox-e-seus-plagios/)** — Ernesto Spinak sobre ausência de opinião ("cauteloso, desinteressado e sem direção") e alucinação de fontes e citações.

Insight-chave da Wikipedia: "LLMs usam algoritmos estatísticos pra adivinhar o que vem em seguida. O resultado tende ao mais provável estatisticamente — o que se aplica ao maior número de casos."

Insight-chave de Sam Kriss (via Fast Company Brasil): o sinal mais duradouro de escrita de IA não está nas palavras nem na pontuação, está na **estrutura das frases**. Por isso, desrobotizar exige mexer no esqueleto, não só na superfície.
