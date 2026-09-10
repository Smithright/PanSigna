# PanSigna

An executable research testbed for **semantic canonicalization and causal legibility**.
This repository implements a bounded synthetic pilot. It does not establish that
PanSigna makes all model internals interpretable or weights safely editable.

## Run

Python 3.12+; CPU is the reproducible default. No paid API or model download is used.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest -q
.venv/bin/python -m pansigna.experiment --steps 300 --seeds 0 1 2 --out runs/pilot
.venv/bin/python -m pansigna.summarize runs/pilot --out runs/pilot-summary.md
.venv/bin/python tools/export_mapping.py runs/pilot/ps-seed0 --out runs/mapping-ps-seed0
```

The default `corpus` objective predicts every next token in synthetic statement,
question, answer records. `--objective answers` trains only the answer token and
is a separate diagnostic. Use separate output directories for different objectives.
Existing run directories are refused. `--arms bits` selects the separate bit-stream
arm; it costs more per example and must not be called compute matched.
The mapping exporter writes labelled decoder coefficients and patch directions;
these are diagnostic maps, not evidence that those directions causally control notions.
`requirements-lock.txt` records the exact installed pilot environment. Use it before
the editable install to reproduce dependency versions on a compatible platform.

## What is implemented

- Strict bit-level codec: IDs begin/end in 1 and contain no eight-zero substring.
  Eight zero bits delimit notions, independent of byte boundaries.
- Parallel finite-world corpora: natural text, sense-tagged text, structured
  experimental PanSigna, permuted IDs, and optional raw bits.
- Small causal transformers trained from scratch with a common vocabulary and
  architecture, identical sampled example indices per seed, and no concept loss.
- Whole actor-recipient combinations held out across all actions/paraphrases.
- Training-only linear subspace fitting; development-only layer selection;
  held-out recipient interventions and actor/action preservation measurements.
- Random subspace, shuffled-label and no-intervention controls.
- Per-run weights, mapping, vocabulary, dataset/source hashes, environment,
  losses, exposure counts and explicit metric denominators.

Start with [the experimental protocol](docs/protocol.md),
[encoding specification](docs/encoding.md), and [research sources](docs/sources.md).

The subsequent [full-chain protocol](docs/full-chain-protocol.md) executes raw text
through annotation, ontology/catalog/index and encoding before native-response
training. See [its results](docs/full-chain-results.md) and the repository `skills/`
directory for eight stage-specific agent contracts. The initial draft manuscript
is under `paper/`; it is not an arXiv submission or a confirmed hypothesis.

The next rung implements [frozen causal alignment and fresh graph calibration](docs/next-experiment-v03.md).
The [graph calibration protocol](docs/v03B-calibration-protocol.md) fixes a competence
gate before interpreting internal graph interventions. Its implementation is
`pansigna.graphs`; frozen v0.2 intervention fitting is `pansigna.alignment`.
The [v0.3 results](docs/results-v03/report.md) preserve positive findings, failed
competence gates, controls and the limits of the comparison.

## Ownership and scope

Ryan Smith's PanSigna conception motivates the hypothesis. The synthetic vocabulary,
enumeration convention, experiment and code in this repository are assistant-authored
research implementations, not ratified PanSigna definitions or a public standard.
The existing repository's MIT license and original README are preserved unchanged.

The original research notes remain unchanged. Shared research artifacts and
checkpoints are archived separately in the project Drive folder. Private source
corpora and credentials do not belong in this repository.
