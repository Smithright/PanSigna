# PanSigna publication strategy: earn the strongest claim

2026-09-10. Assistant-authored research and editorial recommendation. This is a
bounded local review, not a canonical Qthonic task, submission, or claim that a
global optimum has been found. Ryan Smith's conception, assistant proposals,
implemented mechanisms, and measured effects retain separate attribution.

## Primary objective, updated by Ryan's explicit steering

**Discover or develop and demonstrate a language model and training method
yielding precise intermediate representation mapping between a formal ontology
and the model's internal notion sense representations.**

This is the user's north star. The earlier assistant recommendation to prioritize
semantic handoff was an editorial proposal and is superseded. Handoff remains a
supporting application and validation surface; it must not substitute for the
requested internal-representation result or divert its experiment budget.

One coherent publication should explain a model, training method and evidence
for a public ontology-to-internal-representation interface. Precision requires
recovering a notion and intervening through its mapping with predicted effects,
including bindings and composition. A readable output label alone is insufficient.
The interface may be precise up to an identified change of basis; matching raw
neuron coordinates across independently trained models is not a prerequisite.

Candidate title, conditional on results: **PanSigna: Learning Causally Testable
Interfaces Between Ontologies and Language Model Representations**. The decisive
next design is [v0.5 ontology alignment](v05-ontology-alignment-protocol.md). No
v0.4 result is claimed here while that experiment is running. A venue remains
unselected until the contribution and its evidence are established.

## Ranked routes and what would earn them

| Rank | Publication route | Evidence that earns the claim | Result that changes the route |
|---|---|---|---|
| 1 | Primary: learned ontology-to-model interface | Competent one-hop then two-hop models; decoded typed variables; fresh counterfactual pairs; necessity, sufficiency, locality, restoration and cross-seed mapping tests | Ordinary training fails: test causal training and an explicit discrete architecture; do not replace the objective with handoff |
| 2 | Result-dependent architecture route within the same publication | Discrete notion/binding slots pass causal and capacity tests where continuous mappings fail; all architectural restrictions disclosed | Benefit comes from a bottleneck or supervision: credit that mechanism, not the integer index |
| 3 | Supporting communication/application evidence | The qualified interface transfers notion edits to another model or executable task with rich typed baselines and uncertainty retained | Rich JSON parity limits a serialization claim; it does not invalidate a demonstrated internal interface |
| 4 | Supporting encoding and research resource | Verified codec, public notion subset and alignment artifacts, full transport accounting and attributable sources | No codec advantage: retain it as an exchange implementation without claiming optimality |

Avoid dividing one toy experiment into multiple thin papers. A second paper must
answer an independently meaningful question using substantial new evidence.
Prizes are not a planning variable; reproducibility, usefulness, and explanatory
scope are controllable.

## Falsifiable contribution contract

**H1 — internal mapping, primary.** A specified language model and training method
produce a decodable, writable mapping from formal typed notion variables into
its computation, with counterfactual sufficiency, necessity, locality, restoration
and cross-seed transfer on held-out cases. Test the smallest competent symbolic
composition first, then expand sense and binding capacity. Compare ordinary,
intermediate-supervised and causal training before attributing the effect.

**H2 — continuity, supporting.** Explicitly carrying alternatives, evidence, temporal scope and
catalog versions improves correct eventual outcomes under handoff compared with
budget-matched conversational transfer. Primary outcome must jointly require a
correct effect and appropriate treatment of unresolved meaning. A schema-valid
message or harmless refusal alone cannot pass.

**H3 — serialization, supporting.** PanSigna's serialization has an advantage over rich typed
JSON with exactly the same information, validator, tools, and catalog access.
Evaluate accuracy, wrong effects, clarification burden, total bytes/tokens and
cost separately. A null H3 alongside positive H1 supports an internal interface
without a unique wire-format advantage. Test equality only through a
predeclared equivalence/noninferiority margin and adequate precision; a
nonsignificant difference is not evidence of equivalence.

**H4 — correction, extension.** A localized correction transfers to a replacement agent and
new task instances while preserving unrelated commitments. Require held-out
cases, explicit scope, conflicting/stale correction cases, and observed recovery.
Do not describe activation patching, catalog edits and parameter updates as the
same operation. Parameter consolidation is a later independent experiment.

**H5 — preprocessing mechanism.** Semantic preprocessing improves causal alignment of
task-relevant internal variables at comparable competence and resources. Require
fresh data, competent controls, consistent search budgets, and a counterfactual
oracle that evaluates the base computation after an intermediate substitution.
For graph reasoning that is G_base(donor_middle), not the donor's final answer.

## Baselines to borrow and strengthen

1. **Ordinary and supervised neural controls are primary.** Use the same LM
   architecture, initialization schedule and factual examples for ordinary,
   intermediate-supervised and intervention-trained arms. Add data-augmentation
   controls for the extra symbolic information. Keep discrete bottlenecks in a
   separate architecture comparison. A deterministic interpreter checks the
   oracle; it is not evidence that a language model learned the computation.
   Rich typed JSON remains a strong supporting application baseline with IDs, version,
   alternatives, source spans, residual raw text, time and intended effect. Use
   identical validators and state access. An arbitrary token renaming is a
   bijection, not a new semantic mechanism. Include readable canonical symbols
   as a renaming control in neural experiments.
2. **Tool-agent evaluation should reuse established practices.** τ-bench uses
   deterministic database transitions and checks final state, and measures
   consistency across repeated trials. Its reward discussion explicitly notes
   that correct final state can miss a policy violation. Borrow this evaluation
   structure while adding action-trace and unresolved-intent checks. A proposed
   distinction is treating ambiguity as a legitimate target state under handoff;
   novelty against the full literature remains unverified.
   [τ-bench paper](https://arxiv.org/pdf/2406.12045).
3. **Provenance should align with existing vocabulary.** PROV-O already supplies
   entities, activities, agents, attribution and derivation. Map the contract to
   these terms where appropriate; provenance is evidence history, not truth or
   permission. [W3C PROV-O](https://www.w3.org/TR/prov-o/).
4. **Use established causal alignment as a comparator.** DAS already searches
   distributed subspaces and reports structure missed by earlier methods. Our
   source-position recovery is useful calibration but is not by itself a novel
   general discovery. Compare against the published method before making a new
   methods claim. [Geiger et al., 2024](https://proceedings.mlr.press/v236/geiger24a.html).
5. **Include executor and information ceilings.** A deterministic oracle checks
   that tasks are solvable. A no-handoff agent estimates the replacement penalty.
   Oracle-produced and agent-produced handoffs separate serialization loss from
   extraction errors. Always-clarify and always-refuse expose reward shortcuts.

## What current evidence actually supports

The [v0.3 report](results-v03/report.md) was read completely for this review.
Text recipient swaps were 48/48 for all three seeds; atomic swaps were 42/48,
48/48 and 48/48, with unrelated answers preserved. This improves the instrument;
it demonstrates neither PanSigna superiority nor an intermediate reasoning
circuit. Development/test donors crossed the reused corpus's partitions.

All graph arms failed the ordinary-competence gate. Atomic training accuracy near
92% accompanied held-out accuracy near chance, including one-step retrieval.
Sequence length, repeated canonical input and loss weighting are confounds.
There is no adequate causal comparison of learned graph reasoning yet.

The [Plenum synthesis](plenum-semantic-continuity.md) was also read completely.
Its handoff, correction and architecture proposals have no reported model-run
evidence in the two reviewed documents. They must be tested, not promoted into
the abstract as established findings. Original scattered notes were not reviewed
in this bounded subtask; their existing ledger status must not change because
their downstream synthesis was read.

## Ladder and submission readiness gates

**G0 — claim and source audit.** Freeze a claim-to-evidence table and contribution
history. Complete primary-source reading for causal abstraction, intervention
training, concept bottlenecks, binding and related ontology alignment. Record
exact review depth; count neither abstracts nor generated
summaries as fully reviewed papers. Identify reuse licenses and private-source
publication permissions. Treat the present synthesis as scoped research mapping;
statistical meta-analysis requires comparable studies and a defined synthesis
method that are not present here.

**G1 — evaluation validity.** Independently check symbolic oracles, data splits,
intervention locations and gradient paths. Qualify one-hop then two-hop competence
before interpreting alignment failure. Keep worlds/paraphrases grouped; separate
information and architecture changes. Freeze budgets before calls. Calibration
validates the harness and estimates variance; it does not establish the final effect.

**G2 — confirmatory study.** Use fresh hidden cases after calibration, predeclare
primary contrast, practical effect margin, exclusions, analysis and stop rule.
Choose sample size from pilot uncertainty. Randomize condition order; account
for shared scenario, model and repeated-run dependence. Use paired or clustered
analysis, report family-level effects and intervals, and disclose model revisions.
Do not select a successful family after seeing results and call it primary.

**G3 — mechanism and external relevance.** Measure decode, sufficiency, necessity,
locality and restoration; test bypass paths, type/binding errors, notion renaming
and mappings between independently trained seeds. Increase relational and sense
capacity before broad ontology claims. Include a second domain and a held-out
model pairing before cross-agent generality. Seek independent reproduction from the released
artifact. Independent collaborators are not currently recruited or authorized
to receive messages by this document.

**G4 — complete manuscript and human accountability.** Every result links to
exact artifacts and a reproducible analysis. Verify every citation, derived
number, license, limitation and failure claim. Ryan should have the opportunity
to critically revise and approve the final paper, explain its central experiment,
and approve exact name, affiliation, author order and contribution statement.
Preserve his originating conception and years of source work with attributable
dates, without claiming priority beyond the evidence. Record AI contributions
to design, coding, analysis and drafting explicitly. Institutional affiliation,
ORCID, endorsement and legal identity are never inferred from an email domain.

**G5 — venue and submission admission.** Select a venue for the actual result,
then check its live scope, authorship/disclosure, anonymity, artifact and prior
publication rules. arXiv acceptance is distinct from peer review. The existing
arXiv stretch remains conditional on verified #906 delivery; this review does
not resolve that dependency or initiate registration/submission.

## Current publication-policy consequences

arXiv's CS moderation update requires reviews and position papers to have
completed successful peer review and acceptance before submission; workshop
review generally does not suffice. A substantive original empirical paper is a
different route, but adding a token experiment to a position paper is not a
sound way to change its content type. Research articles should be complete final
drafts, and proposals for future research are generally not accepted.
[CS policy update](https://blog.arxiv.org/2025/10/31/attention-authors-updated-practice-for-review-articles-and-position-papers-in-arxiv-cs-category/),
[content types](https://info.arxiv.org/help/policies/content-types.html).

arXiv's agreement requires an original author or preapproved proxy, authority
and coauthor consent. Its endorsement process applies to first papers/new
categories; a self-issued email does not establish endorsement. The inspected
arXiv pages do not settle whether Astra can satisfy the proposed authorship and
account arrangement. Do not imply that they explicitly ban AI coauthorship.
[Agreement](https://info.arxiv.org/help/policies/submission_agreement.html),
[endorsement](https://info.arxiv.org/help/endorsement.html).

For an ACL route, the rule is explicit: generative AI tools cannot be named as
authors, and their substantive use must be disclosed. That venue choice would
require an eligible human byline with transparent AI contribution credit. It
does not erase Astra's contributions or justify attributing them to Ryan.
[ACL publication ethics](https://www.aclweb.org/adminwiki/index.php/ACL_Policy_on_Publication_Ethics).

## Review-depth receipt

All web sources below were verified on 2026-09-10. This is a targeted review,
not an exhaustive frontier search or independent experimental replication.

| Source | Actual review depth | Use |
|---|---|---|
| v0.3 report and Plenum synthesis, linked above | Complete text read | Internal evidence and proposal boundaries |
| τ-bench, linked above | Abstract and targeted sections 3–4/reward/reliability in PDF; not all 50 pages | Evaluation baseline and known final-state limitation |
| DAS, linked above | Official abstract/bibliography; paper introduction excerpt | Closest methodological precedent; full methods review still needed |
| PROV-O, linked above | Introduction/starting-point and relevant expanded-term passages | Borrowed provenance vocabulary; not full conformance review |
| arXiv CS update and content types, linked above | Relevant policy bodies read | Distinguish empirical paper from review/position route |
| arXiv agreement and endorsement, linked above | Relevant policy bodies read | Submission identity, consent and endorsement gates |
| ACL publication ethics, linked above | Authorship and generative-assistance sections | Human authorship and AI disclosure for ACL route |

**Immediate recommendation:** finish and interpret the running v0.4 objective
control, then execute the competence-gated v0.5 ontology-alignment protocol.
Allocate the next learning budget to the unresolved mapping mechanism. Retain
handoff work as a supporting artifact; do not let a convenient systems benchmark
replace the user's primary language-model research objective.
