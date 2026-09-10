---
name: pansigna-catalog-maintenance
description: Maintain stable PanSigna notion identities and definition versions.
---

# pansigna-catalog-maintenance

Think like: Public vocabulary steward. These are methodological influences, not endorsements.

Input: Proposed notions, definitions, existing catalog and provenance.

Output: Versioned catalog.json, additions and explicit definition migrations.

Reuse an existing compatible notion. Append new notions without renumbering existing IDs. A changed definition is a versioned semantic change, not a silent replacement. Experimental namespace entries are not consortium-ratified public notions. Current catalog() rejects unversioned definition changes.

Run commands and artifact contracts are documented in ../../docs/full-chain-protocol.md. Validate the relevant stage with the repository tests. The skills specify agent behavior; their presence does not establish that an independent agent or human has performed that review.
