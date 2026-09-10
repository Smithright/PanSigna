# PanSigna publication claim map

2026-09-10. Working research record for Qthonic ticket #919. Claims below have
different evidentiary status; this is not a submission-ready manuscript.

## The contribution worth testing

PanSigna proposes stable public notion identities, human aliases, an executable
semantic subset, and a distinction between public definitions and contextual
meanings. The publication programme should test which parts improve learning,
communication and correction, and identify the cost of making those distinctions
explicit. A universal aspiration does not require a universal first experiment.

The user has explicitly fixed the primary north star: discover or develop and
demonstrate a language model and training method yielding precise intermediate
representation mappings between a formal ontology and the model's internal
notion-sense representations. Semantic continuity across agent replacement is
supporting infrastructure. It must not displace the primary neural research
question merely because its initial evaluation is easier.

The required evidence combines faithful decoding with predicted counterfactual
effects of interventions, locality, necessity, restoration and generalization.
Publicly specified concept slots are an architectural treatment, not evidence
that arbitrary ordinary-model coordinates inherit ontology IDs. Neither the
primary hypothesis nor a semantic-continuity benefit has yet been established
by the experiments in this repository.

Three objects must remain distinct: a notion/sense (for example a directed link
versus a gesture), a referent identity (which entity), and a bound intermediate
value (the entity reached after one step). The current graph calibration targets
the last of these. Its success would not by itself demonstrate word-sense
alignment. Confirmation needs polysemy, independently checked annotation, held-out
paraphrases and compositions, and interventions that change the intended sense
while preserving unrelated bindings.

The operational meaning of precision is a declared correspondence: executing a
symbolic intervention and then the formal computation should agree with applying
its mapped neural intervention and decoding the model's result, over a specified
test domain. Report errors and coverage. A versioned map into a distributed
subspace is admissible; identical raw coordinates across independently trained
models are not required. A decoder alone does not establish this causal relation.

## Claim-to-evidence map

| Claim | Evidence now | What the evidence does not establish | Decisive next evidence |
|---|---|---|---|
| Bit-level 1-framed identifiers excluding every internal run of eight zero bits can be separated by eight zero bits | Reference codec and conformance tests; all identifiers begin/end in 1, so an exact eight-zero delimiter cannot overlap their edges | General corruption recovery, optimal code length, encryption, or line-rate efficiency | Formal framing statement; adversarial corruption tests and complete transport accounting if transport becomes a paper |
| A finite controlled grammar can be transformed through annotations and a catalog into PanSigna sequences | Existing raw-text parser, sense annotations, catalog and round-trip checks | Natural-language sense annotation accuracy or ontology completeness | Independently annotated real examples with disagreement, residual text and unresolved senses preserved |
| Atomic notion sequences can be learned and decoded by a small language model | v0.1/v0.2 and v0.3 legible generations, with detailed run-specific limits | General reasoning, privileged neural coordinates, or safe weight editing | Competence-matched fresh tasks, representation controls and causal tests |
| Earlier probing missed causally usable source information | v0.3 aligned swaps work for both text and atomic models | An encoding-specific advantage or an internal two-step reasoning mechanism | Intermediate intervention, necessity, restoration and bypass controls on competent models |
| Full next-token supervision may obscure answer learning | A plausible explanation for v0.3 failure; v0.4 pairs objectives with shared initialization and sample schedules | A demonstrated cause until the fixed run finishes; explanation of every v0.3 difference | v0.4 result, then independent seeds and fresh worlds if warranted |
| Explicit semantic commitments improve agent handoffs | Design and evaluation contract only | Measured model benefit or novelty over existing typed state | Information-matched JSON comparison, independently checked action-trace oracle, actual heterogeneous model episodes |
| Persistent corrections can be consolidated into parameters | User hypothesis and proposed staged research route | A safe sleep process, direct weight addresses, or preserved unrelated behavior | Scope-controlled memory correction first; then independently tested distillation and rollback |

## Where the public ontology adds an obligation

A bijection between IDs and notion names makes the interface addressable. It does
not force an ordinary transformer's hidden coordinates to inherit that indexing.
An explicit bottleneck can make a named variable externally inspectable, but its
architectural restriction is part of the treatment and must be tested separately.

Likewise, a lossless codec preserves the supplied formal record. It cannot prove
that an annotator chose the right meaning. Annotation, reference resolution,
semantic validation and serialization need separate error measurements. Unresolved
alternatives are legitimate data, not automatically failures to compress.

For execution, a useful contract should preserve both candidate interpretations
and the constraints on permitted action traces. Silent sense collapse can remove
the intended interpretation; silent authority expansion can introduce an unintended
effect. A later repair of final state does not erase an earlier wrong grant.

The consortium's valuable product would include versioned definitions, examples,
counterexamples, migrations and conformance tests. Agreement on a definition's use
does not prove it true, and proof under a definition does not establish its social
appropriateness. This operationalizes the user's definitions/meanings distinction.

## Attribution and source continuity

The current conversation attributes the overarching PanSigna conception and its
null-skipping framing, comma-prefixed aliases, glyph surface, calculus and native
training hypotheses to Ryan. This records the conversation's attribution; it is
not an independently established priority claim against all prior literature.

The root researcher re-read the complete current readable text of **DRV-067,
PanSigna Agent - Training Framework**, created 2025-01-13 and modified 2025-02-15,
through the connected Drive source. Its five modules already cover local/universal
ontology mapping, ambiguity and proactive inquiry, iterative feedback, and workflow
execution. The handoff programme develops testable consequences of that earlier
corpus, rather than replacing it with a newly attributed origin story. The source
contains assistant-style text; direct human versus assistant authorship remains
unresolved. Original source text was not copied into this public repository.

The project source ledger retains its existing DRV-067 review status. A current
readable-text re-read does not certify a new native-document visual inspection.
The publication strategy review and handoff evaluation contract are explicitly
assistant-authored proposals. Implementation and experiment receipts establish
only the operations and observations they actually record.

## Manuscript route

1. **Motivation and originating conception:** a causal interface between formal
   ontology and learned internal notion representations, with dated provenance.
2. **Model and learning method:** ordinary baseline, explicit alignment objectives
   and architectural bottlenecks compared with clearly stated interventions.
3. **Evaluation:** matched competence and information, fresh compositional cases,
   causal sufficiency/necessity/locality/restoration and transfer. Semantic
   handoff and execution traces provide supporting downstream evaluation.
4. **Results:** only completed measurements; report parity, failures and transfer
   limits. Current toy experiments belong in calibration or a methods appendix
   unless subsequent evidence makes them a substantive independent contribution.
5. **Reproduction and limits:** released fixtures, protocol, code, hashes, model
   revisions, uncertainty analysis and independently checked evaluation.

No abstract should presently claim demonstrated semantic continuity, universal
compression, neural addressability or safe continual learning. The next publication
decision should follow evidence that changes what another researcher can build or
believe. Venue and submission eligibility remain separate from scientific merit.
