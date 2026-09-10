---
name: pansigna-corpus-ingest
description: Admit and partition raw corpora for PanSigna experiments.
---

# pansigna-corpus-ingest

Think like: Corpus provenance specialist. These are methodological influences, not endorsements.

Input: Raw UTF-8 documents with source, revision and reuse terms.

Output: Immutable raw.jsonl, explicit exclusions, content hashes and a semantic-family split.

Keep gold annotations in a separate artifact. Group paraphrases and translations before splitting. Do not publish private source text merely because local research access exists. For the controlled pilot, use pipeline.build; do not describe its generated text as a natural corpus.

Run commands and artifact contracts are documented in ../../docs/full-chain-protocol.md. Validate the relevant stage with the repository tests. The skills specify agent behavior; their presence does not establish that an independent agent or human has performed that review.
