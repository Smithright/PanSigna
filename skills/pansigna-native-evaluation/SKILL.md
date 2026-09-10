---
name: pansigna-native-evaluation
description: Train on transformed PanSigna and evaluate generated outputs and vectors.
---

# pansigna-native-evaluation

Think like: Geiger and Olah style experimentalist. These are methodological influences, not endorsements.

Input: Frozen corpus artifacts, preregistered or explicitly exploratory configuration.

Output: Checkpoints, free generations, catalog-validity and semantic-accuracy counts, probes and intervention controls.

Load verified encoded artifacts, not hidden gold fields. Score unconstrained greedy output before repairs; malformed or nonterminated outputs fail. Fit mappings on train, select layers on dev, evaluate test once. Distinguish decoding from causation and transient activation patches from weight edits. Report model capacity, exposure and token cost separately. Do not tune on test failures until a new exploratory protocol is named.

Run commands and artifact contracts are documented in ../../docs/full-chain-protocol.md. Validate the relevant stage with the repository tests. The skills specify agent behavior; their presence does not establish that an independent agent or human has performed that review.
