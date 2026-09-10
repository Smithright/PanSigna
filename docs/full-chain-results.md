# Full-chain native response results

The v0.2 experiment ran the complete declared transform sequence, then trained
nine models from scratch. All 23 software tests pass locally. The eight agent
skills pass structural validation; independent agent/human annotation review is
not implied. The corpus is controlled synthetic English, not unrestricted prose.

| Representation | Seeds | Correct generated answers per seed | Catalog-legible answers per seed |
| --- | --- | --- | --- |
| Text | 3, 11, 29 | 144/144, 144/144, 144/144 | 144/144, 144/144, 144/144 |
| Atomic PanSigna | 3, 11, 29 | 144/144, 144/144, 144/144 | 144/144, 144/144, 144/144 |
| PanSigna bits | 3, 11, 29 | 70/144, 66/144, 70/144 | 138/144, 126/144, 126/144 |

All outputs terminated within the generation cap. Learned recipient patches did
not increase donor-recipient matches over unpatched generation in any run. The
small nonzero bit-arm matches also occur without patches. They are not evidence
of causal control. Probe results vary; no consistent PanSigna advantage is shown.

## A recorded response, not a constructed example

Selection: first held-out recipient query containing Bob, seed 3 in each arm.
All held-out responses, including failures, are preserved in `responses.json`.

Input: **Bob passes authority to Frank.** Question: recipient.

- Text generated `frank`: correct.
- Atomic PanSigna generated `ps:1011`, decoded as `frank`: correct.
- Bit PanSigna generated `1001`, decoded as `erin`: legible but incorrect.

This distinction is essential: an output can be a valid registered notion while
communicating the wrong meaning. Semantic validation remains necessary.

## Reproduction and artifacts

See [full-chain-protocol.md](full-chain-protocol.md) for exact commands and scope.
The shared archive contains the eight corpus artifacts, nine native model
checkpoints, metrics, response logs, labelled vector CSVs and the draft manuscript.
To rebuild the manuscript, install `.[paper]` and run
`python tools/draft_preprint.py --runs runs/full-chain-v02/models --out paper/rebuilt`
using a fresh output directory. All nine recorded training-source hashes were
checked against the delivered source, and the reloaded bit-seed3 checkpoint
reproduced all 144 saved free generations exactly in the local environment.
The original v0.1 runs remain intact. No private source documents were modified.
Publication is deferred under the user-requested dependency, not claimed complete.
