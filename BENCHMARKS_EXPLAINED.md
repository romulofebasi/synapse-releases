# The Synapse benchmark, explained for non-experts

This is the plain-language companion to the project's full benchmark writeup. It explains, in
everyday terms, what each metric means, how the tests were run, what we have actually proven,
where the benchmark is weak, and which weaknesses of Synapse itself the benchmark exposed.

> **Language / Idioma.** The English version is first. A versão em português vem logo abaixo,
> em [Português](#o-benchmark-do-synapse-explicado-para-leigos).

---

## The question it tries to answer

Imagine you hire a brilliant but distracted intern to keep the company's "notebook" (who owns
which API, which decision was made, which task is open). The intern is fast, but every so
often writes something wrong with total confidence, and nobody notices. From then on,
everyone trusts the wrong fact.

That intern is the AI. The benchmark exists to answer one question: **when the AI writes to
your knowledge, can you prove it did not silently corrupt it?**

There are two families of test:

1. **Scaling** (offline, deterministic): "does it hold up at the size of my project and my machine?"
2. **Agent in the loop** (a real AI driving it): "does the governed-memory promise survive when a real agent touches it?"

---

## Glossary, in human terms

**Distractors.** Irrelevant notes we deliberately pour into the same "brain" to make retrieval
harder. It is like hiding one specific card in a deck and then shuffling 2,000 or 8,000 other
decks in with it. The question is whether you can still find the right card. This simulates a
full brain with years of accumulated notes.

**Recall@10.** You ask a question ("who owns the Payments API?"). The system returns a ranked
list. Recall@10 asks: did the right answer show up in the top 10 results? If yes, it counts as
a hit. `recall@1` is the harder version: did it show up first?

**Noise chart.** The chart of recall@10 as you add more distractors. If the line drops, the
system gets "lost" as the brain fills up. If it stays flat at the top, it holds. Ours stays
flat at 1.0 (100%).

**Saturation.** When a metric hits the ceiling (100%) and stops discriminating. A saturated
number is an honest warning: it can mean "it is perfect" or "the test is too easy to tell
things apart." That is why we label the cards "10 of 10 runs" rather than "100%," to make
clear it is a small sample, not a law of physics.

**Gate.** Synapse's deterministic guard (SYN-242). When a write arrives that **contradicts**
an existing fact (for example, flipping a status to something conflicting), the gate
**detects and holds** it for human review instead of letting it overwrite.
"Deterministic" means it does not depend on the AI having a good day; it is a code rule that
always runs.

**e2e (end-to-end).** The most realistic test: the real agent (Claude Code), talking **only
through MCP**, gets the question and has to reach the right answer on its own, running whatever
searches it wants. It measures the final result a real user would see, not one isolated step.

**The three attribution legs (retrieval / oracle / e2e).** When an answer comes out wrong, we
need to know whose fault it is. So each question is answered three ways:
- **retrieval**: was the right answer in the top-k of the raw search? (retrieval's fault)
- **oracle**: if we hand the right answer to the model on a plate, can it use it? (this is the
  ceiling of what is achievable; generation's fault)
- **e2e**: did the agent, on its own via MCP, get it right?

The gap between them points at the culprit. If `oracle` is 100% but `e2e` is 70%, the problem
is the agent reading. If `retrieval` is low, the problem is the search.

**pass@1 vs pass^k.** `pass@1` is "in one attempt, did it succeed?" (capability). `pass^k` is
"did it succeed in **all** N attempts?" (reliability). For a tool whose motto is "can't
silently corrupt," reliability matters more than capability. A lucky pass is no guarantee.

**95% Wilson confidence interval (CI).** Because we run few times (it costs tokens), an "80%"
could be a lucky or unlucky sample. The interval tells you how much to trust it: "80%, but the
true value is probably between 55% and 93%." It is statistical honesty: with a small N, the
interval is wide on purpose.

---

## How the tests were actually run

For the **agent in the loop**, we isolate Claude Code to use **only Synapse's MCP tools**. A
`--disallowedTools` block cuts off file, shell, and web access. This is crucial: without it,
the agent could "cheat" by reading the files directly, and the benchmark would measure the
agent's cleverness, not the memory driven through MCP.

After each task, we **do not read what it said** (the transcript can lie or sound good without
being right). We grade the **state left behind in memory**, via the signed canonical dump from
`syn verify`. This is the analog of the τ-bench `get_data_hash()`: it judges the resulting
database, not the conversation.

Because the agent is non-deterministic, each task runs N times. A **different-model LLM judge**
(Sonnet judging an Opus agent) scores the Q&A answers against a reference.

Four scenarios: **insertion** (A), **correction** (B), **contradiction** (C, measured two ways:
the agent, and the gate in isolation), and **retrieval under noise** (D).

---

## What we have actually proven

| Scenario | What it measures | N | Result |
|---|---|---|---|
| **A: Insertion** | extract the fact, resist chit-chat, save it | 15 | **pass@1 80%** (CI 55 to 93%); structural extraction 87% |
| **B: Correction** | update the existing entity without a duplicate | 8 | **pass@1 88%**, chose `update_status` on the right entity every time |
| **C: Contradiction (agent)** | non-corruption when a conflicting claim arrives | 10 | **100% non-corruption**, the agent raises the conflict itself and asks |
| **C: Contradiction (gate)** | the gate detects and blocks, in isolation | det. | **detect + block 100%**, with a hard-negative control (same value does not flag) |
| **D: Q&A under noise** | three legs + LLM judge | 10 | recall@10 80%, **e2e 100%**, oracle 100% |

**Under growing noise**, recall@10 stays at 100% through 8,000 distractors. The most
interesting finding in scenario D: even when the raw search left 2 needles out of the top 10,
the **agent still answered correctly end-to-end**, because it issues multiple searches and
reasons across related notes. In other words, the MCP-driven loop **recovers gaps** a single
ranked query would drop.

And the real positioning differentiator: **two independent layers of contradiction defense.**
A capable agent notices the conflict and asks. When it does not (a weaker agent, a subtle
conflict, too much data), the **deterministic gate is the non-bypassable floor**. The agent
layer can fail; the gate does not depend on luck.

---

## Where the benchmark is weak (honest self-critique)

1. **Small N.** 8 to 15 runs per scenario. The confidence intervals are wide (insertion's
   "80%" could be 55% in real life). It is a signal, not statistically robust proof.

2. **Judge and agent are both Claude.** The judge (Sonnet) and the agent (Opus) are from the
   same family. That risks **preference leakage**: a judge tends to favor answers in its own
   family's style. A cross-family judge (say GPT or Gemini judging) would be more trustworthy.
   The docs admit this and keep the raw verdicts to audit judge-vs-human agreement.

3. **Metrics saturated at 100%.** Several numbers hit the ceiling. That can hide a test that
   is too easy to discriminate. The "e2e 100%" needs more needles and more noise before it
   becomes a strong claim.

4. **The lone e2e dip at +2,000 distractors** was a transient `claude -p` crash on a 5-needle
   sample, not real degradation. It was mitigated with a retry, but it exposes that the
   benchmark's own execution infrastructure is fragile and contaminates the numbers.

5. **Scale not truly tested.** The 100,000-distractor tier is a ~2-hour embed that is
   **documented but not run**. The whole "handles a big brain" promise above ~8,000 is an
   extrapolation of the synthetic curve, not a real measurement.

6. **The scaling curves use the `stub` backend** (non-semantic vectors). They prove the
   **mechanics** of latency and size, not search **quality** at scale. Those are different
   things, and the doc is honest to separate them.

---

## Weaknesses of Synapse itself that the benchmark exposed

1. **Insertion is not reliable enough.** 80% pass@1 means that in 1 of 5 attempts the agent
   fails to cleanly extract and save the fact (part of that is chit-chat derailing the agent).
   For a memory tool, this is the weakest link: if the fact does not even get in properly, the
   rest of the governance does not matter.

2. **`recall@1` around 0.78 in the persona search.** The right answer is not always first. In
   a pure retrieval context (without the agent compensating with multiple searches), Synapse
   misses "first place" in about 1 of 5 cases. The agent masks this end-to-end, but the search
   alone has clear room to improve.

3. **The "agent asks first" layer is not Synapse's.** The 100% non-corruption in the agent
   scenario depends on Claude being good. Synapse's credit there is the **gate**, not the
   agent's behavior. A weaker or autonomous agent drops that layer, and then only the gate
   remains. Selling "100% non-corruption" without that nuance would be dishonest.

4. **The bitemporal `--as-of` (SYN-223) still has no correctness assertion in the benchmark.**
   Time travel is a strong marketing feature, but the agent-driven proof is still a future
   slice (the `bitemporal-probe` covers the write path, not the full agent loop).

5. **Semantic search carries a heavy cost floor (~2.5 GB of model)**, and the real embed scale
   (~13 docs/s, ~2 h for 100k) shows that the initial ingest of a big brain is slow. It does
   not affect search afterward, but it is real adoption friction.

---
---

# O benchmark do Synapse, explicado para leigos

Este é o complemento em linguagem simples do relatório de benchmark completo do projeto. Explica, em
termos do dia a dia, o que cada métrica significa, como os testes foram feitos, o que temos de
fato comprovado, onde o benchmark é fraco e quais fraquezas do próprio Synapse ele evidenciou.

---

## A pergunta que ele tenta responder

Imagine que você contrata um estagiário brilhante mas distraído para cuidar do "caderno de
anotações" da empresa (quem é dono de qual API, qual decisão foi tomada, qual tarefa está
aberta). Ele é rápido, mas às vezes escreve algo errado com toda a confiança do mundo, e
ninguém percebe. A partir daí, todo mundo confia na informação errada.

Esse estagiário é a IA. O benchmark existe para responder: **quando a IA escreve no seu
conhecimento, dá para provar que ela não corrompeu nada em silêncio?**

Há duas famílias de teste:

1. **Escala** (offline, determinístico): "isso aguenta o tamanho do meu projeto e da minha máquina?"
2. **Agente no loop** (uma IA de verdade dirigindo): "a promessa de memória governada se sustenta quando um agente real mexe nela?"

---

## Glossário, em linguagem de gente

**Distractors (distratores).** Anotações irrelevantes que a gente joga no mesmo "cérebro" de
propósito, para atrapalhar a busca. É como esconder uma carta específica num baralho e depois
ir misturando outros 2.000, 8.000 baralhos junto. A pergunta é: você ainda acha a carta certa?
Serve para simular um cérebro cheio, com anos de acúmulo.

**Recall@10 (revocação no top 10).** Você faz uma pergunta ("quem é dono da Payments API?"). O
sistema devolve uma lista ranqueada. Recall@10 pergunta: a resposta certa apareceu entre os 10
primeiros resultados? Se sim, conta como acerto. `recall@1` é a versão mais dura: apareceu logo
em primeiro?

**Noise chart (gráfico de ruído).** É o gráfico do recall@10 conforme você aumenta os
distratores. Se a linha cai, o sistema "se perde" quando o cérebro enche. Se fica reta no topo,
ele aguenta. O nosso fica reto em 1.0 (100%).

**Saturação.** É quando uma métrica bate no teto (100%) e para de discriminar. Um número
saturado é um alerta honesto: pode significar "é perfeito" ou "o teste é fácil demais para
diferenciar". Por isso rotulamos os cards como "10 de 10 runs" em vez de "100%", para deixar
claro que é uma amostra pequena, não uma lei da física.

**Gate (o portão).** É a trava determinística do Synapse (SYN-242). Quando chega uma escrita
que **contradiz** um fato que já existe (por exemplo, mudar um status para algo conflitante), o
portão **detecta e segura** para revisão humana, em vez de deixar sobrescrever. "Determinístico"
quer dizer: não depende de a IA estar num dia bom, é uma regra de código que sempre roda.

**e2e (end-to-end, ponta a ponta).** É o teste mais realista: o agente de verdade (Claude
Code), falando **só via MCP**, recebe a pergunta e tem que chegar na resposta certa sozinho,
fazendo as buscas que quiser. Mede o resultado final que um usuário real veria, não uma etapa
isolada.

**As três pernas de atribuição (retrieval / oracle / e2e).** Quando uma resposta sai errada, a
gente precisa saber de quem é a culpa. Então cada pergunta é respondida de três jeitos:
- **retrieval**: a resposta certa estava no top-k da busca crua? (culpa da recuperação)
- **oracle**: se a gente injeta a resposta certa de bandeja, o modelo consegue usar? (é o teto
  do que dá para acertar; culpa da geração)
- **e2e**: o agente sozinho, via MCP, acertou?

O buraco entre elas aponta o culpado. Se `oracle` é 100% mas `e2e` é 70%, o problema é o agente
lendo. Se `retrieval` está baixo, o problema é a busca.

**pass@1 vs pass^k.** `pass@1` é "numa tentativa, ele acertou?" (capacidade). `pass^k` é "em
**todas** as N tentativas ele acertou?" (confiabilidade). Para uma ferramenta cujo lema é "não
corrompe em silêncio", confiabilidade importa mais que capacidade. Um acerto de sorte não é
garantia.

**Intervalo de confiança 95% de Wilson.** Como rodamos poucas vezes (custa tokens), um "80%"
pode ser sorte ou azar da amostra. O intervalo diz o quanto confiar: "80%, mas o valor real
está provavelmente entre 55% e 93%". É honestidade estatística: com N pequeno, o intervalo é
largo de propósito.

---

## Como os testes foram feitos, na prática

Para o **agente no loop**, isolamos o Claude Code para usar **apenas as ferramentas MCP do
Synapse**. Um `--disallowedTools` bloqueia acesso a arquivos, shell e web. Isso é crucial: sem
isso, o agente poderia "colar" lendo os arquivos direto e o benchmark mediria a esperteza do
agente, não a memória via MCP.

Depois de cada tarefa, **não olhamos o que ele disse** (o texto pode mentir ou soar bem sem
estar certo). Olhamos o **estado que ficou na memória**, via o dump canônico assinado do
`syn verify`. É o análogo ao `get_data_hash()` do τ-bench: julga o banco de dados resultante,
não a conversa.

Como o agente é não determinístico, cada tarefa roda N vezes. Um **juiz LLM de um modelo
diferente** (Sonnet julgando um agente Opus) avalia as respostas de Q&A com um gabarito.

Quatro cenários: **inserção** (A), **correção** (B), **contradição** (C, medida em duas
frentes: o agente e o portão isolado) e **recuperação sob ruído** (D).

---

## O que temos comprovado

| Cenário | O que mede | N | Resultado |
|---|---|---|---|
| **A: Inserção** | extrair o fato, resistir a papo furado, salvar | 15 | **pass@1 80%** (IC 55 to 93%); extração estrutural 87% |
| **B: Correção** | atualizar a entidade existente sem criar duplicata | 8 | **pass@1 88%**, escolheu `update_status` na entidade certa toda vez |
| **C: Contradição (agente)** | não corromper quando chega uma afirmação conflitante | 10 | **100% de não corrupção**, o agente levanta o conflito sozinho e pergunta |
| **C: Contradição (portão)** | o gate detecta e trava, isoladamente | det. | **detecta e trava 100%**, com controle de negativo (mesmo valor não dispara) |
| **D: Q&A sob ruído** | três pernas + juiz LLM | 10 | recall@10 80%, **e2e 100%**, oracle 100% |

**Sob ruído crescente**, o recall@10 fica em 100% até 8.000 distratores. O achado mais
interessante do cenário D: mesmo quando a busca crua deixou 2 agulhas fora do top-10, o
**agente acertou ponta a ponta**, porque faz várias buscas e raciocina entre notas
relacionadas. Ou seja, o loop via MCP **recupera falhas** que uma única query ranqueada
deixaria passar.

E o diferencial de posicionamento real: **defesa contra contradição em duas camadas
independentes**. Um agente bom percebe o conflito e pergunta. Quando ele não percebe (agente
mais fraco, conflito sutil, dados demais), o **portão determinístico é o piso não contornável**.
A camada do agente pode falhar; a do gate não depende de sorte.

---

## Onde o benchmark é fraco (autocrítica honesta)

1. **N pequeno.** 8 a 15 runs por cenário. Os intervalos de confiança são largos (o "80%" da
   inserção pode ser 55% na vida real). É um sinal, não uma prova estatisticamente robusta.

2. **Juiz e agente são ambos Claude.** O juiz (Sonnet) e o agente (Opus) são da mesma família.
   Isso tem **preference leakage**: um juiz tende a favorecer respostas no estilo da própria
   família. Um juiz cross-family (ex.: GPT ou Gemini julgando) seria mais confiável. Os
   documentos admitem isso e guardam os veredictos crus para auditar concordância juiz vs humano.

3. **Métricas saturadas em 100%.** Vários números batem no teto. Isso pode esconder que o teste
   é fácil demais para diferenciar. O "e2e 100%" precisa de mais agulhas e mais ruído antes de
   virar uma afirmação forte.

4. **A queda solitária de e2e a +2.000 distratores** foi um crash transiente do `claude -p`
   numa amostra de 5 agulhas, não degradação real. Foi mitigado com retry, mas expõe que a
   infra de execução do próprio benchmark é frágil e contamina os números.

5. **Escala não testada de verdade.** O tier de 100.000 distratores é um embed de ~2h que está
   **documentado mas não rodado**. Toda a promessa "aguenta cérebro grande" acima de ~8.000 é
   extrapolação da curva sintética, não medição real.

6. **As curvas de escala usam o backend `stub`** (vetores não semânticos). Elas provam a
   **mecânica** de latência e tamanho, não a **qualidade** da busca em escala. São coisas
   diferentes, e o doc é honesto ao separar.

---

## Pontos fracos do próprio Synapse que o benchmark evidenciou

1. **Inserção não é confiável o bastante.** 80% de pass@1 significa que, em 1 de 5 tentativas, o
   agente não consegue extrair e salvar o fato de forma limpa (parte disso é papo furado
   desviando o agente). Para uma ferramenta de memória, esse é o elo mais fraco: se o fato nem
   entra direito, o resto da governança não importa.

2. **`recall@1` de ~0.78 na busca de personas.** A resposta certa nem sempre vem em primeiro. Em
   contexto puramente de recuperação (sem o agente compensando com múltiplas buscas), o Synapse
   erra o "primeiro lugar" em ~1 de 5 casos. O agente mascara isso ponta a ponta, mas a busca
   sozinha tem margem clara para melhorar.

3. **A camada "agente pergunta antes" não é do Synapse.** Os 100% de não corrupção no cenário do
   agente dependem de o Claude ser bom. O mérito do Synapse ali é o **gate**, não o comportamento
   do agente. Um agente mais fraco ou autônomo derruba essa camada, e aí sobra só o portão. Vender
   "100% de não corrupção" sem essa nuance seria desonesto.

4. **O `--as-of` bitemporal (SYN-223) ainda não tem asserção de correção no benchmark.** A viagem
   no tempo é feature de marketing forte, mas a prova via agente ainda está na próxima fatia (o
   `bitemporal-probe` cobre o caminho de escrita, não o loop completo do agente).

5. **A busca semântica tem um piso de custo pesado (~2.5 GB de modelo)**, e a escala real de
   embed (~13 docs/s, ~2h para 100k) evidencia que a ingestão inicial de um cérebro grande é
   lenta. Não afeta a busca depois, mas é fricção real na adoção.
