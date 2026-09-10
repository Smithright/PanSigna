# v0.4 one-hop objective control

Status: protocol written before training. This is exploratory calibration on reused synthetic worlds, not a claim of public novelty or independent confirmation.

## Question

Does answer-only supervision resolve the one-hop retrieval failure when the model, data, representation and optimizer are otherwise held fixed? This tests objective dilution as one possible explanation. It does not establish the reason for any earlier failure by itself.

## Fixed design

- Use `graphs.worlds(800, 160, 160, seed=1041)` and unchanged parser, catalog and `rows_for`; retain only `next` queries and templates 0/1. Preserve graph partitions and row order. The resulting data are 1600 training, 320 development and 320 test records per representation.
- Representations: text and atomic. Within each representation, pair full next-token loss against answer-only loss with the exact same initial model state, vocabulary, batches, optimizer and input records. Cross-representation inputs have different lengths and vocabularies; their compute and parameter counts are not identical.
- TinyLM: width 48, three layers, four heads, maximum length 256, dropout zero. AdamW at learning rate 0.003 and its recorded library defaults; batch 64. Model seed 43; sampling seed 143. Generate one entire 6000-step sample schedule and reuse it for both objectives.
- Full loss averages all nonpadding next-token targets. Answer-only loss averages the entire answer and EOS, excluding prompt and padding. Both losses are measured for both objectives. Changing the normalization and gradient contribution is the experimental treatment.
- At step 2000, save the checkpoint and evaluate development exact greedy answer accuracy. If accuracy is at least 95%, stop that objective. Otherwise continue to step 6000 and stop there regardless of outcome. No additional tuning or curriculum in this control.
- Complete and durably record both objectives' stopping decisions within each representation before any retrospective training/development/test evaluation. This barrier prevents the first objective's test results from preceding the second objective's stopping decision. Preserve checkpoint-specific training/development/test generations and diagnostics at every scheduled checkpoint. The test split cannot select a model or change the stopping decision.

## Comparisons and failure gate

The paired primary descriptive comparison is at the common 2000-step checkpoint. A 6000-step comparison is paired only if both objectives extend. Unequal stopped endpoints must never be described as compute matched. Equal steps and samples within a representation control exposure; answer-only supervision still has different supervised-token counts.

Report exact counts, both losses, input/target/answer exposures, initialization and batch-schedule hashes, checkpoint hashes and elapsed time. Record all greedy outputs, including failures to terminate. Records sharing a graph/template and this single seed are correlated: no unqualified significance claim.

If development accuracy remains below 95% at the declared ceiling, retrieval competence is unqualified. Stop progression to causal intermediate-reasoning claims for that arm/objective. If it passes, reserve any causal experiment and new seed/corpus confirmation for a separately declared next stage. Passing one-hop retrieval does not establish two-hop composition, useful natural-language WSD, or a PanSigna-specific advantage.

## Executable protocol

`python -m pansigna.learning_controls --out runs/v04-onehop` runs the declared design. Output directories must be new. `--initial-steps`, `--max-steps`, `--ntrain`, `--ndev`, `--ntest`, and `--batch` support explicitly labeled smoke runs; deviations are written into the configuration. Smoke results are not the declared experiment.

All older source files, corpora, runs and papers remain immutable. This control reuses the same-author synthetic grammar and oracle; it is not independent annotation validation. No long training run is authorized by this implementation subtask; the parent researcher reviews the implementation and starts the run.
