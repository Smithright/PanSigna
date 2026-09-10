# v0.3B calibration protocol

Frozen locally before the first graph-model training run; not an external preregistration.
This instantiates the competence rung of `next-experiment-v03.md`.

- Corpus seed 1041; 800 training, 160 development and 160 test graph worlds.
  Eight named entities; each graph is a permutation successor function. The
  designated root, intermediate and two-step answer are distinct. Graphs are
  globally unique. Partition the root/intermediate/answer triple by a fixed
  arithmetic bucket before rendering; verify all component edges occur in training.
- Two training surface templates; a third held-out surface template for transfer.
  Ten statements per input: eight links and two distracting gestures. The parser
  distinguishes `points to` (link) from `points at` (gesture) using raw text.
  A deterministic parser and same-author generator are calibration instruments,
  not evidence for unrestricted word-sense annotation.
- Per graph/template: one two-step query and one separate one-step query. Both
  are evaluated independently. Whole-graph grouping prevents paraphrase leakage.
- Arms: text, explicitly sense-tagged text, atomic PanSigna. All share worlds and
  ordinary three-layer, width-48, four-head causal transformers. Vocabulary size
  and hence parameter count can differ. Include untrained vocabulary entries for
  held-out surface words; no held-out examples enter training.
- PanSigna catalog extends the v0.2 catalog without reassigning its identifiers.
  Every raw input is parsed, assigned to predicates/entities, serialized through
  the null-skipping bit codec, and decoded into atomic tokens. This tests atomic
  notion training; literal bit-token training remains a separate arm of the programme.
- Calibration seed 41; full next-token objective including prompt tokens;
  AdamW 0.003, batch 64. Check development after 2,000 steps. If either query type
  is below 95%, continue to the predeclared ceiling of 6,000 total steps. Check
  again, then stop. Do not tune using test performance. Report both evaluations.
- Evaluate greedy answers and termination after the training schedule finishes.
  Report test composition accuracy, unseen surface transfer, first/last-name and
  last-edge shortcuts, token exposure, elapsed time and parameter counts.
- No intervention interpretation for a model that fails the development
  competence gate. If all arms fail, this rung identifies a training/task problem;
  it does not refute causal legibility. Do not launch a larger seed sweep as rescue.
- Comparisons here are exposure-matched calibration, not compute-matched,
  statistically powered confirmation. The two paraphrases and repeated queries
  on one graph are not independent experimental units.

The eventual intermediate intervention is z := donor_middle, followed by
answer := base_graph[z]. Copying the donor's final answer is the wrong oracle.
This calibration does not yet implement the necessity/restoration and path-bypass
diagnostics proposed in the broader v0.3 design.
