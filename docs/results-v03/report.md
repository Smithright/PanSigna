# PanSigna v0.3: causal alignment and graph calibration

Exploratory local results. No external preregistration, independent replication,
or arXiv submission. The raw notes and earlier v0.1/v0.2 findings are preserved.

## Phase A — improved intervention on frozen v0.2 models

We optimized an orthogonal subspace against symbolic counterfactual answers,
with model parameters frozen. Eight mapping candidates per model: two layers,
source versus readout, ranks 2 and 7; 200 optimization steps each. Selection
used development counterfactual accuracy and preservation of unrelated fields.
This is a simplified distributed-alignment-search-style instrument, not a
replication of the full published method.

Crossed donors change actor, action and recipient. Each row has 48 recipient
queries and 96 unrelated queries. Numbers below are descriptive within-run
counts; do not pool seeds or paraphrases as independent observations.

| Arm | Seed | No patch | Aligned | Ridge | Random | Shuffled donor | Full state | Aligned unrelated |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text | 3 | 0/48 | 48/48 | 0/48 | 0/48 | 23/48 | 48/48 | 96/96 |
| text | 11 | 0/48 | 48/48 | 0/48 | 0/48 | 16/48 | 47/48 | 96/96 |
| text | 29 | 0/48 | 48/48 | 1/48 | 0/48 | 15/48 | 48/48 | 96/96 |
| atomic | 3 | 0/48 | 42/48 | 2/48 | 0/48 | 25/48 | 39/48 | 96/96 |
| atomic | 11 | 0/48 | 48/48 | 8/48 | 0/48 | 32/48 | 48/48 | 96/96 |
| atomic | 29 | 0/48 | 48/48 | 7/48 | 0/48 | 21/48 | 48/48 | 96/96 |
| bits | 3 | 3/48 | 3/48 | 3/48 | 3/48 | 3/48 | 3/48 | 50/96 |
| bits | 11 | 4/48 | 4/48 | 4/48 | 4/48 | 4/48 | 4/48 | 38/96 |
| bits | 29 | 3/48 | 3/48 | 3/48 | 3/48 | 3/48 | 3/48 | 41/96 |

Minimal donors change only the recipient:

| Arm | Seed | Aligned swaps | Counterfactual log margin before → after |
|---|---:|---:|---:|
| text | 3 | 48/48 | -7.602 → 5.532 |
| text | 11 | 48/48 | -7.836 → 5.060 |
| text | 29 | 48/48 | -7.942 → 6.094 |
| atomic | 3 | 42/48 | -7.062 → 4.893 |
| atomic | 11 | 48/48 | -7.685 → 5.438 |
| atomic | 29 | 48/48 | -7.932 → 5.161 |
| bits | 3 | 3/48 | -8.258 → -7.813 |
| bits | 11 | 4/48 | -7.959 → -7.570 |
| bits | 29 | 3/48 | -9.579 → -8.726 |

The log margin compares complete counterfactual and original answers including
EOS. It is a within-model diagnostic; it is not cross-tokenizer perplexity.

**Interpretation:** source-position alignment exposes strong recipient control
in both text and atomic PanSigna. The earlier ridge/readout null result was
instrument-dependent. There is no demonstrated PanSigna-specific advantage.
These patches can replace lexical information at its source; they do not yet
locate an intermediate multi-step reasoning variable.

All categorical models selected layer 0, source position, rank 7. Bit models
selected layer 0: source/rank 7 for seeds 3 and 29, readout/rank 2 for seed 11.
The bit source intervention covers the final bit of the notion, not its whole
span. The bit models were already below task competence in v0.2. Their unchanged
swap counts cannot settle the semantic hypothesis.

Randomized-model controls (seed 3, all three arms, same alignment search budget)
produced zero correct recipient counterfactual generations. This checks that
the mapping alone did not turn these untrained networks into competent answerers;
it does not prove uniqueness or completeness of the proposed mechanism.

**Limits:** training donors stay in training. Development/test donor pools span
the reused v0.2 corpus because its split lacks minimal donors within held-out
partitions. This is instrument calibration, not fresh confirmation. The shuffled
donor control has substantial positive effects in categorical models and is
not an empirical zero baseline. It shuffles donor states, not concept labels.
Ridge uses up to rank 7 and can differ from a selected rank-2 mapping. The full
state control has rank 48. Equal rank/search-budget claims do not apply to every
control. Path bypass, necessity and restoration tests remain unimplemented.

## Phase B — fresh two-step graph calibration

800 training, 160 development and 160 test graph worlds; two seen templates
and one unseen template. Hold out composed root/intermediate/target triples
while retaining component edges. Keep whole graphs and paraphrases together.
Each graph supplies a two-step query and an unrelated one-step query.

The full chain parses controlled raw text, distinguishes links from gestures,
assigns catalog notions, extends the existing null-skipping index and roundtrips
the stream before atomic token training. Parser/oracle accuracy in this toy
grammar is not independent evidence for natural-language word-sense annotation.

The protocol was written before training: calibration seed 41, ordinary
three-layer width-48 models, full next-token loss. Check development at 2,000
steps; continue to 6,000 if either query is below 95%. No test-driven rescue.

Greedy graph generation allows at most three new tokens: one entity and EOS
are sufficient for a correct response. Termination means termination within
that cap; failure to terminate is not a claim about an unlimited continuation.

| Arm | Steps | Parameters | Development two-step | Development one-step | Test two-step | Test one-step | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
| text | 6000 | 72077 | 23/320 (7.2%) | 35/320 (10.9%) | 44/320 (13.8%) | 40/320 (12.5%) | fail |
| sense | 6000 | 72271 | 32/320 (10.0%) | 42/320 (13.1%) | 47/320 (14.7%) | 43/320 (13.4%) | fail |
| atomic | 6000 | 70913 | 28/320 (8.8%) | 36/320 (11.2%) | 38/320 (11.9%) | 44/320 (13.8%) | fail |

| Arm | Test legible | Test terminated | Unseen surface two-step | Unseen surface one-step | Input token exposures | Seconds |
|---|---:|---:|---:|---:|---:|---:|
| text | 640/640 | 640/640 | 0/160 (0.0%) | 0/160 (0.0%) | 25337220 | 214.4 |
| sense | 640/640 | 640/640 | 0/160 (0.0%) | 0/160 (0.0%) | 29177220 | 261.7 |
| atomic | 640/640 | 640/640 | 19/160 (11.9%) | 22/160 (13.8%) | 13824000 | 123.5 |

The atomic unseen-template input collapses to the same IR as the seen
templates: that is deterministic parser transfer, not independently learned
neural surface-language generalization. Text/sense held-out template words
exist in the vocabulary but their embeddings receive no training examples.

Shortcut baselines on 640 test queries: first_name 74/640, last_name 80/640, last_edge_target 80/640.

Exposure-matched does not mean compute-matched: sequence lengths and vocabulary
sizes differ, and the development stopping rule can yield different exposures.
The catalog preserves prior identities; categorical ID renaming remains a
bijection, covered by the embedding/output permutation equivalence test.

**Gate outcome:** all arms failed ordinary task competence. We therefore
did not fit intermediate-node interventions to these models. That would
confound failure to compute with failure to interpret. Validly named outputs
are insufficient evidence of correct graph reasoning or legible computation.

Post-hoc checkpoint readback reproduced all 640 saved test generations
for each graph arm. Training-set competence (no further fitting or selection):

| Arm | Training two-step | Training one-step |
|---|---:|---:|
| text | 477/1600 (29.8%) | 423/1600 (26.4%) |
| sense | 527/1600 (32.9%) | 403/1600 (25.2%) |
| atomic | 1468/1600 (91.8%) | 1476/1600 (92.2%) |

Atomic PanSigna fits these training examples much better, yet fails held-out
one-step retrieval as well as composition. This is a learning/generalization
failure, not an isolated failure of two-step reasoning. Shorter sequences,
different loss weighting per answer and repeated canonical inputs are confounds;
the training accuracy gap is not evidence for an intrinsic semantic ID advantage.

## Next rung and claim boundary

Check training-versus-held-out competence, then test a separately declared
answer-weighted objective or task curriculum. Keep ordinary LM, auxiliary
concept-loss and explicit symbolic-interpreter models separate. A symbolic
executor is also a useful Qthonic integration baseline. Only competent models
can support the next causal comparison: patch z := donor_middle and require
answer := base_graph[z], while preserving unrelated queries.

No result here establishes direct safe weight editing, an interpretable vector
database of all meanings, encryption, universal optimality or AGI. The positive
finding is narrower and reproducible: the intervention method and location
materially changed what causal control could be demonstrated.

## Reproduction and evidence

Run from the repository root with the archived v0.2 checkpoints/corpus:

```sh
.venv/bin/python -m pansigna.alignment --models runs/full-chain-v02/models --corpus runs/full-chain-v02/corpus --out runs/v03A/aligned --steps 200
.venv/bin/python -m pansigna.alignment --models runs/full-chain-v02/models --corpus runs/full-chain-v02/corpus --out runs/v03A/randomized --steps 200 --randomized --seeds 3
.venv/bin/python -m pansigna.graphs --out runs/v03B/calibration --arms text sense atomic
.venv/bin/python tools/check_graph_checkpoint.py runs/v03B/calibration/text-seed41 runs/v03B/calibration/sense-seed41 runs/v03B/calibration/atomic-seed41
.venv/bin/python tools/report_v03.py --runs runs --out docs/results-v03
```

Output directories must be fresh. `summary.json` records exact input metric
hashes and all numeric development/model results. The Drive archive includes
per-pair outputs, fitted mappings, graph checkpoints, corpus records and hashes.
Base-model hashes were unchanged throughout alignment. Reloading the saved
atomic-seed3 model and mapping reproduced all 144 crossed-pair generations
and exact recorded metrics. Local checks: 35 passed, including codec boundaries,
semantic roundtrips, split isolation, component-edge coverage, stable catalog
identity, causal masking, patch locality and categorical renaming equivalence.

Methodological sources and the broader design are linked in
`docs/next-experiment-v03.md`. This report is assistant-authored experimental
analysis of Ryan Smith's motivating PanSigna hypothesis; no affiliation or
endorsement by the cited researchers is implied.
