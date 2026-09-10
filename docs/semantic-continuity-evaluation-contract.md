# Semantic continuity: synthetic evaluation contract

2026-09-10. Proposed experiment; no implementation or model outcomes are claimed
by this document. It operationalizes the [Plenum proposal](plenum-semantic-continuity.md)
and [publication strategy](publication-strategy-2026-09-10.md). The first release
is a local synthetic sandbox, with no real principals, documents or service effects.

## Attribution and scope

Clarification, context disambiguation, local/universal ontology mapping and
feedback-driven refinement are present in Ryan's project material **PanSigna
Agent - Training Framework**, source DRV-067, created 2025-01-13 and modified
2025-02-15. The root research agent fetched its current readable text in this
session and reported those modules. This contract's author did not independently
read the private document. Its direct human versus assistant authorship remains
unresolved; assistant-style wording in it is not sufficient attribution evidence.
Do not credit this session with inventing these ideas. The source ledger's prior
Complete status is not upgraded by this downstream use. No private text is copied.
[DRV-067 source](https://docs.google.com/document/d/1y2nfqDiJ2ZFIk0GLzmoRqR_hkkvHOurv-iPbORYKBK8/edit).

This assistant-authored contract adds a concrete experimental operationalization:
paired representations, transition traces, isolated transport measurements,
information controls, negative controls and admission gates. Whether any of
those additions is novel in the research literature remains to be established.

## Question and units

Can replacement agent B preserve agent A's partially resolved intent and reach
the justified outcome when references, time, authority evidence or definitions
may need revision? Does PanSigna serialization change the outcome or total
communication cost relative to an information-matched typed representation?

The independent fixture is a **world + dialogue + scheduled change**, not an
individual paraphrase, token or repeated model call. An episode is one fixture,
condition, ordered model pair and sampling repeat. All paraphrases and repeats
of a fixture remain grouped in reporting and any later statistical analysis.

## Minimal world and record

Use two users who share display name Alex (`person:1`, `person:2`), two documents
that may share an alias (`doc:1`, `doc:2`), and a synthetic requesting principal.
Documents have owner and revision. Grants are a set of tuples
`(person_id, document_id, role, expires_at)`; role is initially read or edit.
Authority is an executor-owned map of which principal may grant/revoke which
document. It never comes from a handoff assertion. Time is a fixed UTC clock
plus an explicitly supplied fixture timezone. No wall-clock-dependent oracle.

Each fixture contains initial state S0, B's current state S1, A's dialogue,
trusted speaker identity, catalog v1/v2, a clarification answer table, and hidden
allowed transition predicates. A receives the dialogue and S0 snapshot. B receives
only the handoff plus identical inspection/clarification tools for all arms.
Hidden oracle answers never appear in prompts or catalog descriptions. Store
the operational state and semantic scoring oracle as separate objects. The
executor receives no hidden dialogue interpretation or expected-effect predicate.

The interchange record has these fields, with a schema version:

| Field | Required meaning |
|---|---|
| provenance | Fixture-local utterance IDs, trusted speaker references and evidence spans; evidence text included in charged handoff when needed |
| force | request, quotation, observation, hypothesis or unresolved alternatives; never inferred solely from a permission word |
| operation | grant/revoke/none or an explicitly unresolved candidate set |
| target and resource | Candidate stable IDs and their evidence; distinct from notion/sense IDs |
| role | Catalog notion ID, catalog version and unresolved alternatives if any |
| temporal_scope | Explicit expiry or unresolved expression with its reference clock/timezone |
| evidence_state | Known, missing, ambiguous or conflicting, separately for each unresolved field |
| observations | Resource revision, observation time and source; records claims, not current authorization |
| residual | Relevant raw text not represented elsewhere, preserved without pretending it has been formalized |

Catalog entries have immutable IDs and versioned labels. A label change preserves
identity; an incompatible sense split introduces new IDs and an explicit migration
relation. `null` means absent only where the schema permits it; it does not merge
unknown, ambiguous, conflicting and deliberately unspecified states.

## Shared action interface and transition oracle

All conditions use the same output schema and tool executor:

1. `inspect(kind, id)` returns current identity/resource/authority/catalog data
   and a fresh fixture revision. It changes no grant.
2. `clarify(field, candidates)` asks the fixture user to resolve a genuine missing
   distinction. The answer table releases only the requested distinction. A
   redundant or irrelevant question returns no extra hidden information.
3. `propose_grant(person, doc, role, expiry, observed_revision, attestation)` and
   `propose_revoke(person, doc, role, observed_revision, attestation)` are admitted
   or refused by the same deterministic executor. Admission checks only declared
   operational rules: schema/types, existing IDs, current authority, fresh
   required reads/revisions and the mechanical attestation requirements below.
4. `finish(status, unresolved_fields)` closes the episode as completed, no-action,
   blocked or needs-clarification. The oracle checks the status and fields.

Every call appends a trace event containing arguments, before/after state hashes,
admission decision, reason and returned revision. Proposals refused by the executor
remain observable attempted effects. The experiment scores both attempted and
executed wrong effects; a strong executor must not conceal poor agent proposals.
The executor and B-side tools cannot read the hidden semantic scoring oracle.
The clarification simulator has its separate answer table; it releases answers
only through the declared user-interaction interface, never to effect admission.

Each proposal's attestation contains B's claimed request force, claimed resolution
of required arguments, and evidence references. The declared validator can check
that the force is `request`, the required resolution flags are present, and the
referenced utterance IDs exist. Those checks do not establish that the claims are
true. It must not interpret the raw dialogue with a perfect parser, consult hidden
candidate sets, replace an argument, or silently repair a mistaken force label.
Any added semantic validation model is a separately declared experimental factor
with identical access and cost across arms, not a free oracle in the executor.

Consequently, a schema-valid, freshly authorized grant to the wrong Alex can
execute. A quotation mislabeled by B as a request can also execute when the
operational checks pass. The independent scorer detects both semantic failures
from the hidden dialogue interpretation and trace. Report semantically wrong
proposals refused on operational grounds separately from semantically wrong
proposals that executed. This separation is necessary to measure how well the
agents preserve meaning rather than how well an oracle shields their errors.

**Correctness is a trace predicate plus an end-state predicate.** The fixture
allows necessary inspections, relevant clarification and the specified effect,
while rejecting unrelated mutations, unauthorized attempts, action before required
resolution, use of stale state, and duplicate non-idempotent effects. A grant then
revoke that accidentally restores the expected final state fails the trace check.
The fixture must specify whether an already-present exact grant requires no-op
or permits an idempotent proposal; do not improvise this after observing a run.

For mutable requests, fixture `required_reads` records which authority/resource
checks must occur after B begins. For a quote or observation, the correct effect
is no mutation; a fresh read is not automatically required. This prevents charging
every task for an irrelevant safety ritual.

This strengthens a known evaluation boundary: τ-bench checks final state and
required response content, while explicitly noting that such success can omit
a policy violation. [τ-bench, section 3](https://arxiv.org/pdf/2406.12045).

## Conditions: hold information constant

**J — rich typed JSON.** Contains every field above, exact evidence and alternatives,
catalog version and residual text. Never use an impoverished JSON baseline to
make PanSigna appear more capable.

**P — PanSigna transport.** Encodes exactly the same semantic record with stable
notion IDs, null-skipping 1-framed notion characters and an explicitly specified
literal envelope. Use the existing verified codec; transport any remaining literal
strings/numbers using a declared reversible representation. The stream cannot
be called complete until those literal rules and record boundaries are fixed.

For the **transport-isolation comparison**, J and P decode to the same canonical
record and use the same B-facing renderer. This measures transport correctness
and cost. It cannot demonstrate a neural semantic advantage from hidden bytes.
With identical model inputs and sampling, different behavior is a harness defect
or nondeterminism to investigate, not evidence for the encoding.

For a later **model-facing surface comparison**, render J as JSON and P as a
specified readable PanSigna alias sequence or actual binary-token surface. These
are separate subconditions, not interchangeable labels. Freeze grammar, catalog
instructions, examples and decoding before calls. Both surfaces expose exactly
the same semantic content and permit the same unresolved states. Report how much
prior vocabulary/training familiarity each model has. A text API's `0` and `1`
tokens are not native bit-level training. Do not claim such a test validates
native PanSigna pretraining or a ps-glif interface.

**N — conversational reference.** Receives the same available information and
total budget, expressed in natural language. This tests the contract relative
to ordinary handoff; it does not isolate serialization alone.

**C — forced-collapse ablation.** Replace genuine alternatives with one arbitrary
candidate while keeping other P fields. This deliberately removes information.
It is a negative control for semantic collapse, not a fair representation baseline.

## Separate extraction from serialization

First use **oracle-authored handoffs**, producing J/P from the same hidden semantic
record. This isolates serialization and B's interpretation. Then use
**agent-authored handoffs**, where A extracts the record from dialogue. Report
A's semantic faithfulness before encoding: correct force, candidate-set recall,
unjustified candidates, lost uncertainty, reference accuracy and evidence support.

A perfect encode/decode roundtrip proves preservation of the supplied record;
it does not prove that record preserves the dialogue's meaning. Annotation and
execution failures need separate labels. Agent A's correction attempts, retries
and catalog queries count toward total cost and remain in the trace.

## Sixteen calibration fixtures

Freeze two independent cases per family before any evaluated model sees them.
Within a family include different identities/roles or outcomes, not a mere
surface paraphrase. The seed and hidden expected predicates are hashed.

| Family | Required behavior and discriminating control |
|---|---|
| Resolved request | Correct grant/revoke after required reads; include already-satisfied idempotence case |
| Person ambiguity | Preserve both Alex candidates until clarification; include supplied-ID counterpart that needs no question |
| Resource ambiguity | Resolve which draft through allowed evidence; include unique-reference counterpart |
| Time scope | Resolve deadline/timezone only if absent; include explicit timestamp that must not be reinterpreted |
| Operational force | Quoted/observed permission causes no mutation; counterpart is an authentic request with the same permission words |
| Conflicting evidence | Preserve conflict and inspect/clarify its relevant source; include coherent-evidence counterpart |
| State drift | S1 invalidates stale authority/revision; a forged handoff claim cannot override executor state |
| Catalog change | Label-only rename preserves effect; incompatible sense split requires explicit migration or clarification |

Adversarial qualification also includes wrong-person grant, correct-final-state
after extra mutations, dropped quotation marker, fabricated evidence, truncated
stream, forbidden internal eight-zero run, unknown notion ID, missing catalog,
duplicate proposal and an always-clarify loop. These are harness controls,
not additional independently sampled model cases.

## Outcomes, budgets and abstention utility

Primary pilot outcome: fraction of fixtures with both valid trace and justified
end state/status. Report raw counts by family and condition, with all wrong-effect
attempts and executions visible. Also report clarification precision/necessity,
lost alternatives, stale-reference errors, migration errors and successful
resolved tasks. No aggregate can hide catastrophic categories.

Use a declared episode ceiling of 12 B actions, including at most four
clarifications. Exceeding the ceiling is incomplete, not correct abstention.
Unresolvable fixtures pass only when the agent identifies the actual missing or
contradictory field without a wrong effect. Resolvable fixtures require completion
within the ceiling. Always-refuse and always-clarify therefore fail ordinary
resolved cases. Record unnecessary clarification cost separately rather than
inventing an unvalidated scalar safety/utility tradeoff.

Measure wire payload bits/bytes, envelope/padding, catalog transfer, version
negotiation, lookup messages, raw residual text, and retries. Report cold catalog
and warm catalog runs separately with an explicit amortization count. Measure
model-specific input/output tokens, total model calls and measured runtime.
If monetary cost is reported, pin the price source/date and include preprocessing
and retries. A compact local ID with an unpaid remote definition is not full
communication compression. Compare canonical JSON and a conventional compact
binary serialization before claiming a transport advantage; exact implementation
and version are fixed before that comparison.

## Qualification gates and evidence labels

**Q0 — contract freeze.** Fixture schema, literal codec, renderer, trace predicates,
budgets, catalogs and condition manifests exist and have exact hashes. This
document alone does not meet Q0.

**Q1 — model-free harness.** A scripted oracle agent completes every solvable case
and returns exact unresolved fields for blocked cases. Each adversarial mutation
receives the expected independent score. Operationally invalid proposals are
refused; operationally valid wrong-person and mislabeled-quotation controls must
execute and then fail semantic scoring. Tests establish that effect admission
does not access hidden semantic fields. J/P roundtrip and canonical-renderer equivalence
hold; catalog omissions and corrupt streams fail explicitly. A reviewer other
than the fixture author checks hidden answers and at least one full trace per
family. Passing Q1 qualifies a harness, not agent intelligence or performance.

**Q2 — bounded model pilot.** Freeze models/versions, prompts and decoding limits.
Use the 16 fixtures with four logical conditions, two ordered pairings (same-model
and heterogeneous), and two repeats: 256 episodes for one specified model-facing
protocol. Transport-only checks do not require extra model calls. Run oracle and
agent extraction stages as separately labeled cohorts if both are evaluated;
doing both doubles that budget, not silently expands the claimed 256. Record
missing/failed calls; do not substitute models without a manifest revision.

**Q3 — confirmatory admission.** After pilot error analysis, freeze fresh hidden
fixtures, a primary contrast, practical effect threshold and clustered analysis.
Size the study using pilot variance and required precision. Neither 256 episodes
nor two repeats automatically supports a population-level superiority claim.
Parity requires a predeclared equivalence/noninferiority design. Add a new domain
and held-out pairing before broad cross-agent claims.

No gate authorizes production effects, deployment, private-note publication,
arXiv registration or submission. Results may justify adopting the contract while
borrowing existing serialization. The experiment is successful as research if
it clearly identifies what survives handoff, what is lost, and which mechanism
or cost explains the difference.
