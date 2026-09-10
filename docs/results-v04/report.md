# PanSigna v0.4: paired one-hop objective control

Exploratory calibration on reused synthetic graph worlds, seed 43. The protocol
and implementation were committed at `5a09b70` before the declared run.
This isolates the objective within each representation; it does not replicate
all v0.3 conditions or establish a PanSigna-specific advantage.

## Measured checkpoints

| Representation | Objective | Steps | Train exact | Dev exact | Test exact | Dev gate |
|---|---|---:|---:|---:|---:|---|
| text | full | 2000 | 671/1600 (41.9%) | 35/320 (10.9%) | 43/320 (13.4%) | fail |
| text | full | 6000 | 1433/1600 (89.6%) | 40/320 (12.5%) | 47/320 (14.7%) | fail |
| text | answer_only | 2000 | 1527/1600 (95.4%) | 42/320 (13.1%) | 48/320 (15.0%) | fail |
| text | answer_only | 6000 | 1600/1600 (100.0%) | 35/320 (10.9%) | 42/320 (13.1%) | fail |
| atomic | full | 2000 | 1452/1600 (90.8%) | 40/320 (12.5%) | 48/320 (15.0%) | fail |
| atomic | full | 6000 | 1594/1600 (99.6%) | 42/320 (13.1%) | 30/320 (9.4%) | fail |
| atomic | answer_only | 2000 | 1600/1600 (100.0%) | 46/320 (14.4%) | 36/320 (11.2%) | fail |
| atomic | answer_only | 6000 | 1600/1600 (100.0%) | 46/320 (14.4%) | 40/320 (12.5%) | fail |

**Outcome:** all four models failed development competence. Both
answer-only models fit all 1600 training records at the final checkpoint,
while held-out accuracy remained near the eight-choice chance reference.
Answer-only supervision improves fitting here but is insufficient for
generalization. No intermediate causal mapping was evaluated on these
unqualified models. This is a negative result for this recipe, not a
general impossibility result for PanSigna or causal training.

## What was controlled

Within each representation the objectives received identical initial parameters,
rows, vocabulary, optimizer defaults and precomputed sample schedules. Common
checkpoints have identical record/input-token exposures. Full loss supervises
all nonpadding next tokens; answer-only supervises the answer and EOS.
Both stopping decisions were recorded before test evaluation for either member
of each pair. The 95% development gate selected stopping at 2000 or 6000 steps.

| Representation | Common comparison steps | Full stopped | Answer-only stopped |
|---|---|---:|---:|
| text | [2000, 6000] | 6000 | 6000 |
| atomic | [2000, 6000] | 6000 | 6000 |

Unequal stopping endpoints are not compute matched. Cross-representation
comparisons also differ in sequence lengths, vocabulary, parameter counts and
canonicalization. Full and answer losses are recorded for both objectives in
`summary.json`; full-sequence losses across tokenizations are not comparable
perplexities. Each template shares its underlying graph, and atomic templates
collapse to the same input. Counts are descriptive, not independent trials.

## Claim boundary and reproduction

Passing one-hop retrieval qualifies only that task for this calibration run.
It does not establish two-hop reasoning, real-language word-sense annotation,
causally legible intermediates or safe parameter editing. Failure blocks those
downstream claims for the affected model. New seeds and fresh worlds belong
in a separately declared confirmation, not a rescue selected by these tests.

All manifest file hashes/sizes matched. Reloading each of the four final
checkpoints reproduced its 320 held-out greedy generations and exact counts.
The paired initialization, rows, full schedule and common exposure hashes
were checked. These are local reproducibility checks, not external replication.

```sh
.venv/bin/python -m pansigna.learning_controls --out runs/v04-onehop
.venv/bin/python tools/report_v04.py --runs runs/v04-onehop --out docs/results-v04
```

Use fresh output directories. The archive includes model checkpoints, optimizer
states, data, schedules, catalog, every checkpoint generation and diagnostics.
