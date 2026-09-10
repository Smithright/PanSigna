# v0.3 design: causal accessibility after semantic canonicalization

Status: proposed design, not implemented, run or externally preregistered.
Grounded in source commit 9f542c286e187097e0e916798b2ff03c743781c1.

## Question and competing explanations

Does PanSigna canonicalization make useful internal variables more causally
accessible, beyond making input and output identifiers readable?

The v0.2 result cannot separate three explanations: the ridge decoder finds a
noncausal correlate; the intervention targets an ineffective location; or later
attention recovers the original information from unchanged context. Equal swap
counts also conceal possible probability shifts below the greedy decision boundary.
Do not describe v0.2 as evidence that no causal mapping exists.

## Phase A: diagnose the existing checkpoints

Freeze model weights and retain v0.2 as exploratory data. No retraining is needed.

1. Build paired prompts with an exact symbolic counterfactual. Minimal donors
   change only the recipient; crossed donors also change nuisance fields. Report
   these conditions separately. The symbolic oracle supplies expected outputs,
   not an assistant's explanation of what the model should do.
2. On training/development prompts, map intervention effects across both layers,
   the final prompt position, and role/value source spans. Align spans through
   pipeline provenance rather than assuming equal token positions across arms.
   Validate approximate attribution results with actual activation patches.
3. Compare ridge with a distributed-alignment-search-style orthogonal mapping
   fitted on training counterfactual outcomes. Freeze the language model: this
   trains the interpretability map, not the base model. Predetermine a small rank
   grid and equal optimizer/search budgets; select once on development data.
4. Include random subspaces, shuffled concept labels, no patch, identity patch,
   whole-state positive controls and the same alignment fit on a randomized model.
   An expressive mapping that succeeds equally on a randomized model is weak
   evidence for a learned semantic mechanism.
5. Measure whether later states restore the original concept after a patch.
   Use matched path patches/restorations to test the suspected attention route.
   Context masking is a diagnostic intervention and may be out of distribution;
   do not present success after masking as success in the unmodified architecture.

Metrics: before/after change in the log-probability difference between the entire
counterfactual answer and original answer, including EOS; unconstrained generated
semantic answers; and preservation of unrelated fields. Report complete sequences
for bits, not just the first bit (which is always 1 for valid identifiers). Log-score
changes are within-model/within-pair diagnostics, not cross-tokenizer perplexities.
Publish pair-level results so positive and negative effects cannot cancel invisibly
inside one aggregate count.

This phase chooses and validates an instrument. Reusing v0.2 prompts cannot provide
a fresh confirmatory test of the hypothesis. Preserve all failures and choices.

## Phase B: fresh compositional experiment

Create a new finite graph world with explicit typed `edge` and `follow2` semantics.
The query follows exactly two directed edges from a specified node. Include
distractor edges, shuffled statement order and several possible query starts.
The answer must depend on the requested path, not the last mentioned entity.
These are defined toy operations, not claims that real-world delegation is transitive.

Create the graph split before rendering language or PanSigna. Hold out composed
edge pairs while retaining their component relations in training. Keep every
paraphrase/alias of one graph in one partition. Add a separately held-out surface
template set. Tests should verify that first/last-name and last-edge baselines fail.

Compare three main conditions from the same semantic worlds:

- Natural text with contextual sense selection required.
- Sense-annotated text preserving ordinary sentence structure.
- Fully canonical PanSigna with explicit roles/operators and notion identities.

Add a structured human-readable serialization control to distinguish explicit
structure from notion labelling. Where it is a token-for-token renaming of atomic
PanSigna, use the exact embedding/output permutation equivalence test: no intrinsic
benefit can be attributed to the numeric spelling of categorical IDs. Do not count
bijectively renamed conditions as independent semantic innovations.

Primary experiment uses atomic notions to avoid conflating a semantic hypothesis
with learning long bit strings. The exact null-skipping stream remains the reference
transport representation and must roundtrip. A subsequent literal-bit arm tests
serialization, with separate competence and compute accounting. It is not omitted
from the programme, but a poorly trained bit model cannot settle semantic legibility.

Train ordinary models without concept losses first. Match architecture and data
content; report both exposure-matched and compute-matched comparisons. Architecture
changes (explicit concept bottlenecks, auxiliary concept losses or interchange
intervention training of the base model) form a separate follow-on study. Their
success would support designed interpretability, not encoding alone.

## Primary causal outcome

Patch the hypothesized intermediate node representation in a two-step computation.
Success requires the output to follow the symbolic counterfactual path, while
unrelated query answers remain correct. Preselect the counterfactual graph pairs
and unrelated-query set before evaluating held-out model outputs. A recipient
label visible at input or a final answer direction is insufficient evidence of an
intermediate computation.

Report unconditional joint success and eligibility-conditioned success. Eligibility
requires correct unpatched base, donor and counterfactual inputs; report denominators
and a shared eligible subset across arms as well as each arm's own subset. Do not
hide poor competence by filtering away its failures. Use both sufficiency (patch
causes predicted change) and necessity/restoration tests; no single ablation alone
establishes a complete causal mechanism.

## Decision and uncertainty

Suggested engineering gate, to freeze before training: at least 95% development
task accuracy before interpreting a model's null intervention result as meaningful.
This is a proposed adequacy threshold, not a literature standard or significance
criterion. Report all runs, including those below it. Allocate any extra training
under a predefined development-only rule rather than test-driven rescue.

Use a separate calibration pilot to estimate between-seed and between-graph
variation. Then freeze sample sizes, minimum meaningful effect, equivalence margin,
mapping capacity, stopping rules and a fresh confirmatory seed/data set. Analyze
paired arm differences across seeds and graph families; do not treat templates or
all interventions on one graph as independent observations. Correct for the small
predeclared comparison family and report confidence intervals, including nulls.

Possible interpretations:

- DAS beats ridge equally in all arms: the earlier map was weak, without a PanSigna
  advantage.
- Effects appear only after restricting context access: bypass or architecture
  matters; encoding-alone support remains absent.
- PanSigna improves held-out joint causal success at comparable competence/cost,
  beyond sense and structure controls: bounded evidence for semantic canonicalization.
- Only a trained concept bottleneck succeeds: evidence for an architectural change.
- No method exceeds controls: retain a negative result with the tested scope.

## Methodological influences and primary sources

- Chris Olah, Wes Gurnee and Anthropic's circuit-tracing collaborators: distinguish
  readable features from validated causal mechanisms. Their work is an influence,
  not an endorsement: https://www.transformer-circuits.pub/2025/attribution-graphs/methods.html
- Neel Nanda: cheaply localize candidate mechanisms, then validate approximations
  through real patches: https://www.neelnanda.io/mechanistic-interpretability/attribution-patching
- Samuel Marks and the Anthropic CHIVE team: explanations must predict measured
  counterfactual effects, and tools must beat a strong baseline. CHIVE studies prompt
  edits; adapting that evaluation principle to internal patches is our proposal:
  https://alignment.anthropic.com/2026/chive/
- Atticus Geiger, Zhengxuan Wu, Christopher Potts, Thomas Icard and Noah Goodman:
  distributed causal alignment, the central method for this design:
  https://proceedings.mlr.press/v236/geiger24a.html

No frontier-lab affiliation or endorsement is claimed for this project. Scientific
credit depends on the reproducible result, including an informative negative result.
