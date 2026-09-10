---
name: pansigna-bit-index
description: Assign and validate null-skipping, 1-framed notion identifiers.
---

# pansigna-bit-index

Think like: Encoding engineer and property-testing specialist. These are methodological influences, not endorsements.

Input: A frozen ordered catalog and existing assignments.

Output: index.json with unique bit IDs and catalog hash.

IDs start and end with 1 and exclude any eight consecutive zeros at any bit offset. 100000001 is valid; 1000000001 is invalid. Preserve prior assignments. Do not confuse a categorical token address with numeric semantic geometry. Use the reference codec and exhaustive short-string tests.

Run commands and artifact contracts are documented in ../../docs/full-chain-protocol.md. Validate the relevant stage with the repository tests. The skills specify agent behavior; their presence does not establish that an independent agent or human has performed that review.
