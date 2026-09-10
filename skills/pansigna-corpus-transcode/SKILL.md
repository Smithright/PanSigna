---
name: pansigna-corpus-transcode
description: Compile ontology assignments into auditable PanSigna corpora.
---

# pansigna-corpus-transcode

Think like: Compiler engineer. These are methodological influences, not endorsements.

Input: Typed assignments, frozen catalog and index.

Output: encoded.jsonl with bit streams, hashes and decoded semantic readback.

Require semantic roundtrip to the accepted assignment and reject unknown IDs. Retain source links separately because semantic normalization is not exact recovery of original wording. Keep transport control tokens separate from notion bits. Do not claim compression or encryption from this codec.

Run commands and artifact contracts are documented in ../../docs/full-chain-protocol.md. Validate the relevant stage with the repository tests. The skills specify agent behavior; their presence does not establish that an independent agent or human has performed that review.
