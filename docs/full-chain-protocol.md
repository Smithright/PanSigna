# Full-chain native response pilot v0.2

Status: exploratory, fixed configuration before the v0.2 run; not externally
preregistered. This extends rather than replaces the preserved v0.1 pilot.

## Executed transforms and agent skills

`raw corpus -> contextual sense spans -> typed assignments -> catalog -> bit index
-> encoded corpus -> native-response training -> free generation and vector tests`

Each transform has a corresponding `skills/pansigna-*/SKILL.md`. These are portable
agent instructions in the repository; they are not globally installed and do not
claim independent agent execution. The current reference implementation is a
deterministic parser and compiler. Agent proposals can later use the same contracts.

```sh
.venv/bin/python -m pansigna.pipeline --out runs/full-chain-v02/corpus
.venv/bin/python -m pansigna.native --corpus runs/full-chain-v02/corpus \
  --steps 1200 --seeds 3 11 29 --out runs/full-chain-v02/models
```

The corpus has 384 generated raw English statements, two word-order variants of
192 semantic scenes, and three unresolvable negative controls. Raw records do not
carry gold senses. The parser reads only text; a separate oracle artifact scores
its assignments. Both grammar and oracle are assistant-authored, so agreement is
an engineering check, not independent linguistic annotation validation. All
statements remain in source artifacts; unresolved inputs are quarantined.

Annotations record exact surface spans and contextual predicate senses. Ontology
assignment constructs an actor-action-recipient frame. The catalog separates
entities, predicates, roles and a query operator in an experimental namespace.
Index enumeration is stable and excludes any internal run of eight zero bits.
Transcoding must roundtrip to the semantic frame. It does not recover original
word order or every surface word. The trainer checks artifact hashes before use.

## Native training and responses

Three arms: text, atomic PanSigna notions, and individual PanSigna bits. All use
the same known experimental vocabulary and 2-layer width-48 transformer. Each
seed receives the same sampled example indices. Seeds 3,11,29; 1,200 updates;
batch 64; AdamW .003; full next-token loss; CPU. This is exposure matched, not
compute matched. Actual input-token count and elapsed time are recorded.

Unlike v0.1, native arms predict native notion tokens or bit strings as answers.
Both prompt and answer are derived from the verified encoded-corpus artifact.
The only non-notion controls are the transport envelope tokens BOS, ANSWER, EOS,
and padding. Each accepted statement produces three field questions. Actor-recipient
combinations are held out with all their variants/actions: 864 training records,
144 development, 144 test. Catalog definitions are not given as natural-language
training prompts, and no pretrained model is used.

Responses use unconstrained greedy generation, capped at 16 new tokens. A response
must terminate, parse as exactly one registered notion, and match the expected
field value to count as semantically correct. Catalog legibility is reported
separately from semantic correctness. No correction, constrained decoder, English
fallback or teacher-forced answer is substituted for generated responses.

## Vector tests

The final prompt readout is collected at each layer. A training-only ridge probe
decodes recipient identity; its column space defines a candidate causal subspace.
Select the layer on development counterfactual/locality scores only. Test learned,
random same-rank, shuffled-label and no-patch conditions on held-out prompts.
Recipient donors differ in actor/action/recipient but match the queried field.

The selected readout position is patched on every generation step. Its location
remains fixed at the original prompt boundary as the response grows. This prevents
mistakenly patching a different response position at each step. Unchanged context
paths may still bypass the patch; null effects do not falsify all possible mappings.
There is no claim that a final-layer patch controls the full bit continuation.

Count every failed or nonterminated generation. Report unconditional effect and
locality with denominators; no significance claim from three correlated synthetic
runs. A future study needs natural text, independent annotations, richer semantics,
intervention-optimized alignment, fresh held-out data and a power calculation.

## Publication boundary

Draft a methods/results manuscript from observed artifacts, with a separate AI
contribution disclosure. The user subsequently made autonomous Stalwart/arXiv
identity registration and submission a stretch goal conditional on verified #906
delivery. No registration, endorsement, account eligibility or publication is
implied by the draft. Current authorship and proxy requirements must be verified
at that time; no identity or affiliation may be fabricated.
