---
name: pansigna-sense-annotation
description: Annotate contextual senses and spans before ontology assignment.
---

# pansigna-sense-annotation

Think like: Corpus linguist using the Potts and Fellbaum distinction between sense and reference. These are methodological influences, not endorsements.

Input: Raw text and a versioned annotation inventory; no hidden gold labels.

Output: annotations.jsonl with exact character spans, candidate senses, annotator and version.

Use context to distinguish passes-authority from passes-parcel. Unknown names or unresolved senses remain unresolved. The current executor is a deterministic grammar, not an LLM annotator. An agent extension must emit candidates and evidence in the same schema; test against independently labelled held-out text before replacing the reference.

Run commands and artifact contracts are documented in ../../docs/full-chain-protocol.md. Validate the relevant stage with the repository tests. The skills specify agent behavior; their presence does not establish that an independent agent or human has performed that review.
