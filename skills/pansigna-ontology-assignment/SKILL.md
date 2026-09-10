---
name: pansigna-ontology-assignment
description: Map accepted sense annotations into a typed experimental ontology.
---

# pansigna-ontology-assignment

Think like: Ontology engineer. These are methodological influences, not endorsements.

Input: Accepted annotations, versioned definitions and role constraints.

Output: Typed assignments.jsonl linked to annotation and catalog hashes.

Shared spelling does not establish identity. Separate entities, predicates and roles. Refuse unresolved annotations. Preserve negation, binding and scope if present; the current fragment does not support them, so route such inputs to quarantine. Do not force them into the three-slot frame.

Run commands and artifact contracts are documented in ../../docs/full-chain-protocol.md. Validate the relevant stage with the repository tests. The skills specify agent behavior; their presence does not establish that an independent agent or human has performed that review.
