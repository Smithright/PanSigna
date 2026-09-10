# Initial findings and next discriminating experiment

This is a pilot implementation result, not a verdict on PanSigna.

Twelve full-corpus training runs (four categorical arms, three seeds) reached 100%
accuracy on the synthetic held-out answer task. Training-only recipient probes
recovered substantial recipient information, but the selected ridge subspaces
produced **zero successful recipient swaps** in every arm. Actor/action answers
remained correct. Random and shuffled-label controls also produced zero swaps.
Full final-state replacement reproduced donor recipient answers, verifying that
the intervention path can affect predictions. Exact values appear in
[pilot-results.md](pilot-results.md); raw metrics include conditional denominators.

The results support neither a causal advantage for PanSigna nor the conclusion
that such an advantage is impossible. The task, mapping family and patch location
are narrow. A representation can carry linearly decodable information without the
decoder's subspace being a causal mediator. At an earlier layer, later attention
can recover information from unchanged context; at the final layer, ridge directions
may recover information that is not aligned with the output-driving directions.
These are explanations to test, not findings established by this pilot.

The separately run bit arm is substantially below perfect task accuracy under the
same number of example exposures. It has longer sequences and greater compute cost.
Its small nonzero swap rate is uninterpretable as an advantage without ordinary
task competence, selectivity and negative-control comparisons. See bit-results.md.

The next experimental design should compare training-only intervention-optimized
alignment against ridge on a fresh split/seeds, add input-path mediation/ablation,
and introduce derived answers requiring composition rather than direct field recall.
Keep representation-only training separate from concept-supervised architectures.
Freeze that design prospectively: do not search held-out scores until something wins.

## Audit trail

- Core tests first failed for missing implementation; codec/oracle implementation
  then passed seven contract tests.
- Intervention tests first failed for missing model implementation, then passed.
- Initial pilot runs are retained separately from runs adding the positive control.
- No training/evaluation source changed between the positive-control categorical
  runs and the separate bit runs. Source hashes are recorded in every metrics file.
- Existing upstream README and MIT LICENSE were restored byte-for-byte from the
  fetched base commit before adding any research files.
- Local CI-equivalent tests were run; hosted CI execution is a separate claim.
