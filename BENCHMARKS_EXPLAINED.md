<a id="o-benchmark-do-synapse-explicado-para-leigos"></a>

# The Synapse benchmark, explained for non-experts

This guide interprets historical internal evaluations. It does not establish universal reliability, independently measured team ROI or identical behavior in every published binary. Pin the evaluated code, models, corpus and harness before comparing a new result.

<a id="a-pergunta-que-ele-tenta-responder"></a>

## The question it tries to answer

Can an agent retrieve useful context, propose an intended update and preserve the existing record when a conflicting claim arrives? These are separate observable behaviors. General truth, all natural-language contradictions and complete historical integrity need different evidence.

The historical reports include retrieval experiments, bounded agent scenarios and deterministic guard checks. Their samples and scoring procedures must remain distinct.

<a id="glossário-em-linguagem-de-gente"></a>

## Glossary, in human terms

| Term | Meaning | Limit |
| :-- | :-- | :-- |
| Recall@k | Whether the relevant reference appears in the first k retrieval results | Retrieval availability is different from answer correctness. |
| Distractors | Deliberately added irrelevant records | A synthetic noise test does not establish performance on every real corpus. |
| End-to-end | The agent performs its supported retrieval/task loop | Repeated searches can recover a miss in a single ranking. |
| Oracle context | The evaluation supplies the reference context directly | This estimates a different condition from ordinary retrieval. |
| pass@1 | Success in one evaluated attempt | Small samples do not establish stable deployment reliability. |
| Repeated-run success | Success over repeated attempts under a stated definition | Report actual run counts and dependence between samples. |
| Guard | A deterministic check for a supported structured conflict or invariant | It does not understand every natural-language disagreement. |

<a id="como-os-testes-foram-feitos-na-prática"></a>

## How the tests were actually run

The historical agent scenarios restricted Claude Code to the Synapse MCP interface, with file/shell/web tools excluded by the harness. Evaluation inspected resulting state as well as task answers. Reference-based Q&A used an LLM judge; agent and judge were both from the Claude family, which limits independence.

The retrieval corpus included 463 entities and 20 synthetic-persona questions. Synthetic personas and internally authored questions are not independent customer data or a cross-product benchmark. Retrieval, model answer quality and deterministic stored-state checks measure different properties.

<a id="what-we-have-actually-proven"></a>
<a id="o-que-temos-comprovado"></a>

## Historical observations

| Scenario | Observed result | What can be concluded |
| :-- | :-- | :-- |
| Insertion | 12 of 15 attempts succeeded | Extraction and clean insertion were imperfect in these cases. |
| Correction | 7 of 8 attempts succeeded | The tested update workflow often succeeded, with a remaining failure. |
| Contradiction agent scenario | Existing fact preserved in 10 of 10 tested runs | The previous value survived these inputs; this is not universal conflict detection. |
| Structured guard controls | Tested conflict cases were held; same-value controls did not flag | The exercised guard cases behaved as asserted, within their recognized field/transition rules. |
| Retrieval and Q&A | Separate ranked-retrieval, oracle and agent-loop results were recorded | A correct final answer can coexist with a miss in one retrieval ranking. |

Keep the denominator visible. A result of 10/10 is a small observation, not a guarantee. A confidence interval cannot establish behavior for a different task distribution. Do not combine the 20-question retrieval evaluation with the differently sized agent scenarios into a single success rate.

The historical reports also explored distractor growth through a bounded executed tier. Stub-vector scaling experiments exercised mechanics rather than semantic quality. A larger proposed tier was documented but not run; it cannot be presented as measured capacity. Consult the [development benchmark record](https://romulofebasi.github.io/synapse/docs/BENCHMARKS.html) for the dated evidence, exact configurations and newer work.

<a id="onde-o-benchmark-é-fraco-autocrítica-honesta"></a>

## Where the benchmark is weak (honest self-critique)

1. Small scenario counts and internally authored inputs limit generalization.
2. Same-family agent/judge evaluation can share style preferences and blind spots.
3. Saturated small-case metrics can indicate an easy test rather than a robust system.
4. Harness crashes, retries and missing runs affect the reported experiment and must remain visible.
5. Stub-vector latency/size measurements cannot establish real-model retrieval quality.
6. Unexecuted large-corpus tiers are plans, not observations.
7. Historical binary/model/harness results do not automatically transfer to newer or older releases.

<a id="pontos-fracos-do-próprio-synapse-que-o-benchmark-evidenciou"></a>

## Weaknesses of Synapse itself that the benchmark exposed

Insertion failures matter before any later memory workflow can help. Ranking misses require better retrieval or explicit abstention, even when a capable agent compensates with more queries. A model noticing a contradiction is separate from the native structured guard. Temporal correctness, broader architectural contradictions, privacy boundaries and production adoption require their own tests and independent review.

Model storage and initial indexing also impose real resource costs. The default multilingual model footprint is about 2.5 GB; no universal ingestion throughput or first-run duration is established by this guide.

## How to use this evidence

Use the historical data to design a bounded pilot: select representative tasks, preserve inputs and evaluated revisions, separate retrieval/state/review outcomes, record failed attempts and compare against an appropriate baseline. Add independent labels and reviewers before making comparative or reliability claims.

The evidence supports continued evaluation of governed operational memory. It does not establish a universal claim that memory cannot be corrupted, every change is reversible, or every contradiction will be caught.
