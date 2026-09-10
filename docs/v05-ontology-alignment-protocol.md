# v0.5: a causally testable ontology-to-model interface

2026-09-10. Proposed protocol, not an implemented experiment or result. The v0.4
objective control is still running at this document's design point; its results
must be read before selecting the next frozen training manifest. One coherent
publication remains the target.

## North star and smallest defensible demonstration

Ryan's explicit objective is to discover or develop and demonstrate a language
model and training method yielding precise intermediate representation mapping
between a formal ontology and the model's internal notion sense representations.
This protocol keeps that objective primary. It permits changes to learning and
architecture if ordinary preprocessing alone is insufficient, with the source
of any benefit identified explicitly.

Separate three objects throughout:

- **Notion/operator sense:** LINK versus GESTURE, or a typed computational
  operator with a public definition. This is the semantic distinction of interest.
- **Referent identity:** `entity:alice` versus `entity:bob`. A stable name for a
  particular entity is not a word sense.
- **Bound computational value:** the entity currently occupying intermediate
  role `middle`. Its identity can vary while the role and operator sense remain.

A graph pointer experiment tests the third object. It can qualify an instrument
or architecture; it cannot alone demonstrate ontology/word-sense alignment.
The decisive scope includes a mapped sense that selects a computation while
keeping the referent/binding representation separately controllable.

## Formal model and observation surfaces

Start with eight entities and a successor map G. One hop computes `y = G(root)`;
two hops compute `z = G(root); y = G(z)`. Graphs, edge order and queried roots vary,
and held-out compositions retain component coverage. A learned first lookup must
produce z; never feed the gold z to the model at inference. For a binding patch:

```
z := z_donor
y_counterfactual := G_base(z_donor)
```

After competence, extend to two independently generated relation maps L and T,
representing LINK and GESTURE respectively. A toy language has contextual senses
of “points”: controlled “points to” and “points at” expressions, plus separately
split paraphrase families. Both relations have defined results, so a branch swap
changes computation rather than merely making one output invalid. This toy
operational semantics is a stipulated benchmark, not a full linguistic theory.

```
s1, s2 : RelationSense = {LINK, GESTURE}
root, z, y : Entity
R(LINK) = L; R(GESTURE) = T
z = R(s1)(root)
y = R(s2)(z)
```

Swapping s1 recomputes z and y; swapping s2 changes only the second lookup;
swapping z preserves base s2 and requires `R_base(s2)(z_donor)`. Construct cases
where these predictions differ from copying the donor answer or entity. Evaluate
an unrelated query on the same graph to measure locality. Randomize identities
and relation tables independently so the model cannot use names as branch labels.

The public interface is versioned:
`ontology_version, notion_type, variable_role, model_hash, site, map_version`.
It provides `decode(hidden_site) → typed value` and
`write(hidden_site, typed value) → edited hidden_site`, with documented residual
state preserved where possible. A distributed subspace is acceptable. Orthogonal
rotations and slot permutations are not failures when a documented map resolves
them. Raw coordinates have no privileged universal semantics by assumption.

## Staged execution and bounds

**Stage A — factual competence.** Freeze the ordinary LM recipe after inspecting
v0.4's training-versus-held-out evidence. Use a new calibration seed 71 and fresh
train/dev/test manifests. Check one-hop development exact-answer accuracy at
2,000 updates; if below 95%, extend to 6,000 total, then stop that recipe.
No test-driven rescue. A failed one-hop recipe is not evidence against semantic
mapping. Record whether insufficient fitting or generalization caused failure.
If O fails, S/I/D may undergo their own declared one-hop calibration from common
initial weights within the same ceiling. They need not wait for O to succeed;
an ordinary-model failure remains an explicit comparison limit.

**Stage B — two-hop mechanism.** Reuse the qualified one-hop initialization within
each matched comparison, with fresh two-hop examples and balanced roots. Apply
the same 2,000/6,000-update development schedule and require at least 95% ordinary
accuracy separately for one-hop retention and two-hop queries. A discrete model
may qualify independently if the ordinary model fails; then its architectural
effect is the result, with the ordinary causal comparison marked unqualified.

**Stage C — actual sense/binding alignment.** Run the two-relation polysemy task
with the same staged ceiling. Require ordinary competence on each sense, hop
count and held-out composition family before interpreting causal comparisons.
Use fresh dev/test donor pools wholly within their respective partitions.
Report decisive pairs whose required counterfactual differs from the base output
separately from unchanged-output pairs. Define at least 128 base worlds and four
balanced donors per base/variable for a bounded calibration evaluation, with
donors reused only as explicitly grouped observations.

Stage A/B can proceed as mechanism calibration. The primary notion-sense claim
requires Stage C. Calibration is seed 71; after freezing the recipe, fresh seeds
73, 79 and 83 assess repeatability. All failures remain in the report. These are
bounded pilot counts, not a powered population-level confirmation; a final
study needs fresh fixtures, effect margins and uncertainty-driven sample sizing.

## Training arms and information controls

| Arm | Training intervention | What comparison can establish |
|---|---|---|
| O: ordinary LM | Factual autoregressive answer objective chosen and frozen from objective calibration | What the model acquires without intermediate/counterfactual supervision |
| S: intermediate supervision | O plus typed sense and binding readout losses | Whether extra concept labels suffice; probe accuracy alone does not establish causal use |
| I: causal intervention training | O plus losses on internally patched base/donor counterfactuals | Whether training causal behavior creates a more faithful internal interface |
| A: symbolic data augmentation | O trained on explicit `do(variable=value)` examples with the same symbolic counterfactual labels | Whether additional examples/labels explain I's benefit without internal intervention |
| D: discrete typed bottleneck | Neural sense/binding predictors and neural continuation with hard typed values as the only declared bridge | Whether an architectural public interface achieves the objective, with restrictions and capacity costs disclosed |

O/S/I/A share the same LM architecture, vocabulary, structural slot tokens,
initialization and factual example order wherever applicable. Heads needed only
by S/I are allocated identically or counted separately; report active/trainable
parameters and effective computation rather than asserting equality from a
similar parameter count. Freeze at most two candidate continuous sites and ranks
2/7 on development; apply the same discovery budget to frozen baselines. Do not
optimize on test pairs. Initially compare all five arms on the calibration seed;
replicate the retained recipe and its necessary controls after the gate.

Use `L_I = L_factual + lambda * L_counterfactual`, starting with lambda 1 as a
declared calibration choice. Patches must propagate gradients through both base
and donor paths; the symbolic oracle is not differentiated. For S, typed losses
and their weights are declared separately. The A arm receives the same sampled
counterfactual labels but via observable augmented input, so its inference
interface differs and is disclosed. Match factual exposure, then report total
passes, labels, tokens, updates and measured compute. Add compute-matched O/S
runs if I wins; equal optimizer steps alone are not a fair compute claim.

IIT already trains internal interventions against a causal model, and the primary
paper includes typed interventions between compatible variables. Its full-domain
zero-loss relationship must not be reinterpreted as a guarantee from sampled
high accuracy. Our candidate contribution is an explicit, versioned notion-sense
interface with separated binding and its measured limits, not inventing IIT.
[Geiger et al., 2022, section 3 and typed-IIT passages](https://proceedings.mlr.press/v162/geiger22a/geiger22a.pdf).

Separate the representation factor from the training factor. First use the same
canonical typed corpus for all arms. Compare atomic PanSigna IDs against a
bijection of readable canonical symbols using the same vocabulary size, input
structure and information. A permutation-consistent embedding/output remapping
is an exact invariance control. Then compare raw controlled language, explicitly
sense-annotated text and canonical PanSigna; these have different preprocessing
information and sequence lengths, so report those differences. Reserve bit-stream
training for a separately qualified stage with competent whole-notion-span
interventions. Passing an atomic-token study does not validate bit-native training.

For lexical transfer, every test token must have actually appeared in a neutral
training context for each compared arm; vocabulary membership alone is insufficient.
Hold out sense-bearing combinations
and paraphrase families, not wholly untrained token embeddings. Freeze a shared
vocabulary and list its exposure by arm. Canonicalizing an unseen paraphrase
with a hand-written parser proves parser transfer, not neural disambiguation.
Test learned raw-language sense extraction separately from oracle-annotated input.

## Discrete architecture and bypass audit

D uses typed slots for operator sense and entity binding. A first neural stage
reads context and emits hard categorical values. A second neural stage receives
the relevant base relation tables and those values; it receives neither the
original root nor unrestricted first-stage residuals for the binding-only lookup.
For the sense test it must use the declared sense to select a relation. Evaluate
free-running predictions; teacher-forced gold intermediates are diagnostics only.
The second lookup must remain learned if claiming a language model learned the
calculus; a deterministic executor is an oracle/control, not that result.

Hard values mean actual discrete IDs at evaluation. Softmax probabilities,
confidence, hidden ordering, timing or residual vectors must not silently carry
undeclared input information into the continuation. Report any straight-through
training estimator and its discrepancy from hard evaluation. Balance all roots
per graph and use fresh graphs so the graph alone cannot identify the query.
Instrument the exact tensors crossing the stage boundary and test that changing
excluded source information with fixed declared inputs leaves the continuation
unchanged. This is a separate architecture, not a same-model regularizer.

Discoverable slots are a subsequent variant: learn site/basis assignment on
training data, align slot roles with a fixed public ontology using development
data, and freeze that map for test. Compare against declared fixed slots under
the same capacity. Stable interface naming can coexist with discovered internal
bases; no claim of uniquely identifying the model's only semantic decomposition.

## Mapping tests: precision means an operational contract

1. **Decode.** Recover held-out s1, s2 and z separately, including same entity in
   different roles and different entities under the same sense. Report conditional
   confusion matrices. A decoder receives only the declared internal site.
2. **Causal sufficiency.** Replace the mapped variable using a donor or typed write;
   require the exact symbolic counterfactual with other base variables retained.
   A public typed write must work across multiple donors sharing that value, not
   rely on one donor's unrelated hidden features.
3. **Necessity and bypass.** Remove or randomize the mapped information while
   preserving the declared complement, using matched-rank unrelated controls.
   Measure target impairment, not just generic network damage. Test restoration
   and redundant alternative paths before inferring necessity. If the model
   recomputes from raw context, the slot may be sufficient but is not established
   as the required route. Quantify that limitation rather than moving the claim.
4. **Locality.** Patching s2 must preserve z; patching z must preserve decoded
   senses and unrelated answers. Patching s1 may legitimately change both z and y.
   Define allowed causal descendants in the symbolic DAG before tests.
5. **Restoration.** Save the unedited variable, apply a destructive edit, then
   restore it in the same base context. Require recovery of the original answer
   and unaffected variables. Decode-after-write must recover the requested typed
   value. This is reversible at the public interface, not necessarily recovery
   of every original latent bit.
6. **Cross-seed transfer.** Train maps on fixed calibration data for each seed;
   transfer an ontology value decoded from seed A through seed B's typed writer
   without task-specific retraining. Compare with a bounded alignment-only
   adapter trained on common calibration values. Report each directed pairing,
   adapter labels/cost and held-out success. Direct raw-vector transplantation is
   a diagnostic, not the definition of semantic interoperability.

All tests include no-op/same-value, wrong-type, shuffled-value, random-subspace,
full-state and randomized-model controls where meaningful. Same-sense donors
with different bindings test contamination. Different-sense donors with the same
binding test genuine branch control. A control that has a positive effect is
reported quantitatively rather than labeled a null by design.

For calibration, target at least 95% held-out factual, decode and decisive
counterfactual exact match, 95% restoration, and at most a two-percentage-point
drop in unrelated-answer accuracy. Report uncertainty and denominators; these
thresholds are engineering admission criteria, not proof of exact semantics.
Necessity is a separate measured effect with restoration/random-site controls,
not inferred from those thresholds. A sampled pass supports only the tested
finite domain; even 100% on it does not establish universal mapping.

## Ambiguity, capacity and expansion

After the crisp two-sense case, add examples whose context does not decide a
sense. The target is an explicit typed candidate set or unknown state, followed
by a clarification-conditioned branch when additional evidence arrives. Do not
force one correct synset where the fixture deliberately permits alternatives.
Score set preservation and resulting branch changes separately from confidence.

Expand one factor at a time: entities 8→16, senses 2→4, hop depth 2→3, repeated
entity bindings in different roles, and parallel queries. Measure accuracy,
mapping rank/slot count, training labels, compute, sequence cost and residual
leakage. A fixed slot budget that fails to represent composition reveals a
capacity tradeoff. A model may need structured tuples, variable binding or
recursive records rather than one flat vector per word sense. These are design
questions to resolve empirically, not reasons to abandon the public interface.

## Deliverable and claim boundaries

Release exact corpus/oracle manifests, notion catalog and version, model recipes,
checkpoints, typed read/write maps, raw interventions, failed controls and generated
reports. Link findings to the source ledger without upgrading original-note review
status. Preserve Ryan's originating conception and distinguish this protocol's
assistant-authored operational details. The 2025 framework attribution remains
as documented in the [continuity contract](semantic-continuity-evaluation-contract.md).

A successful minimal publication demonstrates a trained language model whose
internal operator senses and bound values implement a small declared calculus
through tested, transferable mappings. A discrete-only success is meaningful if
the neural components learn and the causal restrictions are explicit. Failure
of all calibrated arms means the target has not been demonstrated; handoff or
codec success cannot be used as its substitute. Safe parameter editing, broad
natural-language ontology coverage and universal optimality remain unproven.

Review depth: Geiger et al. (2022) abstract, section 3 definitions/loss/pseudocode,
and typed-IIT passages were read from the primary PDF on 2026-09-10. The appendix
proof and complete experimental sections were not fully reviewed or replicated.
Current v0.3 facts are historical context; no v0.4 outcome was inferred. This
document performs no model calls, implementation, submission or live action.
