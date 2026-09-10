# Semantic canonicalization and causal legibility: pilot v0.1

Status: prospective local design for exploratory runs; **not externally preregistered**.
No empirical success thresholds or power calculation are claimed. A confirmatory
study must freeze a protocol and new seeds/data before collecting its results.

## Research question

Does canonical semantic training produce representations that support more accurate
recipient interchange interventions, while retaining actor/action answers, than
matched natural-language or sense-disambiguated training?

The first test concerns internal activations. Input embedding addresses are known
by construction. Neither a good linear probe nor a successful activation patch
establishes direct control over persistent model weights.

## Arms

| Arm | Input | Question addressed |
| --- | --- | --- |
| nl | Two natural-language templates | Baseline |
| sense | Same templates with sense-labelled verbs | Disambiguation contribution |
| ps | Explicit role/notion sequence, atomic notion tokens | Canonical structure contribution |
| permuted | Same sequence with a fixed bijective ID permutation | Categorical ID control |
| bits | ps sequence serialized with null delimiter, one token per bit | Separate encoding ablation |

All share an explicitly known alphabet and common natural-language answer labels.
This avoids variable output-task definitions but is an asymmetry: raw language has
input/output lexical overlap, while ps requires a learned mapping to answer labels.
The ps corpus duplicates each example to match the two nl template exposures.
Duplication is not extra semantic diversity. The sense arm supplies clearer labels;
the comparison measures a representation intervention, not information equivalence
of arbitrary real-language corpora. ID permutation is categorically symmetric when
embedding/output rows are correspondingly permuted; differences under independent
initial rows are optimization noise, not numeric semantic meaning.

## World, partitions and objective

Eight entities × three actions × eight recipients = 192 semantic scenes.
Each has two surface variants and three field questions = 1,152 records.
Actor-recipient pairs, including self-pairs, are assigned by a deterministic modular
rule: 144 train scenes, 24 development, 24 test. No action or template of a held-out
pair enters training. All entities and actions remain represented in training.

This is a single-event world. Negation, quantifiers, binding, multi-hop inference,
real-world ambiguity, human annotations and natural multilingual corpora remain
future extensions, not capabilities of this pilot. Answers can be obtained by
retrieval/copying from the statement. A positive result would demonstrate a causal
handle on simple role information, not general semantic reasoning.

Train a 2-layer, width-48, four-head causal transformer from scratch on CPU.
Dropout 0; AdamW, lr .003; batch 64; 300 updates per pilot seed, seeds 0/1/2.
Default loss is full next-token corpus cross entropy excluding padding. A separately
named answer-only diagnostic is supported. Training length/steps are fixed, not
selected using test accuracy. There is no concept bottleneck or concept loss.

Comparison is **exposure matched**, not FLOP or wall-time matched. A common vocabulary
keeps parameter counts equal; actual sampled input-token counts, padded lengths and
elapsed times are recorded. Losses/perplexities across different tokenizations are
not directly comparable. No cost-matched effect is estimated in this pilot.

## Mapping and causal intervention

For each candidate layer, collect the hidden state at the final readout token across
training records. Fit a ridge linear decoder to recipient labels, pooling question
types. Its orthonormal column basis (rank ≤7) defines the recipient subspace.
Ridge .01 and rank cutoff 1e-8 are fixed. The mapping is not trained on held-out data.

For each base record, choose a deterministic donor from the same partition, template
and question type, with **different actor, action and recipient**. Project the donor
state into the learned recipient subspace and replace only those base coordinates:

`patched = base + ((donor - base) @ Q) @ Q.T`

Resume the original network. Recipient questions should switch to the donor's
recipient; actor/action questions should retain the base answer. The intervention
is at the final readout position, never an input embedding or output token. This is
a distributed-alignment baseline using ridge, not a replication of DAS or IIT.

Select between the two layers using development data only, maximizing the equal
mean of recipient counterfactual accuracy and actor/action correctness. Break ties
toward the earlier layer. Freeze this choice before test evaluation. Comparing final
layer and earlier layer is informative, but a final-layer success can reflect a
decision/output representation; it does not prove a deep reusable reasoning circuit.

Controls at the same selected layer: random orthonormal subspace of matched rank,
subspace fit to shuffled training labels, and a rank-zero no-patch intervention.
No test-driven tuning or selection of controls. All are reported, including failures.
After the initial exploratory run returned zero selective swaps, a full-state
replacement positive control was added at the final layer. Its purpose is to verify
that the intervention path reproduces donor decisions; it should also change donor
actor/action information and is therefore not a selective semantic intervention.
The original runs are retained in the shared archive; no learned mapping or selection
rule was changed in response to their results.

## Outcomes and interpretation

Primary joint outcomes: unconditional recipient counterfactual accuracy and
actor/action correctness under intervention, reported separately. Also report
each on pairs where both original base and donor answers are correct; always report
denominators because eligibility varies across models. These conditional scores
must never conceal low ordinary task accuracy. Null eligible sets return null.

Diagnostic: held-out recipient accuracy of a training-only linear ridge probe.
Random/shuffled controls reveal whether decodability or broad state replacement
alone explains apparent success. The symbolic counterfactual oracle is exact for
this finite world, but it does not certify neural faithfulness in arbitrary contexts.

Summaries show seed-level results and paired differences. Three seeds and correlated
synthetic templates do not support a strong significance or frontier-scale claim.
Do not bootstrap each template as if it were an independent semantic example.

## Follow-on gates

1. Check implementation, task learning and negative controls on fresh runs.
2. Freeze a confirmatory protocol: task-performance tolerance, effect-size target,
   pilot-based power calculation, compute-matched controls, fresh data and seeds.
3. Extend to composition/binding/negation and independently annotated real text.
4. Test explicit notion supervision as a separate architectural intervention.
5. Only then investigate persistent edits, retention, collateral effects and sleep.

Thinking disciplines: Geiger/Potts/Icard for causal abstraction; Olah's team for
intervention validation; Marcus for compositional counterexamples; Kent Beck and
John Hughes for executable contracts and property tests. These are methodological
influences, not affiliations or endorsements.
