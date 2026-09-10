"""Finite causal oracle; experimental vocabulary, not PanSigna standard IDs."""
from dataclasses import dataclass, replace
import itertools
import random
from .codec import notion_ids

ENTITIES = ("alice", "bob", "carol", "dana", "erin", "frank", "grace", "hana")
ACTIONS = ("delegate", "give", "inform")
FIELDS = ("actor", "action", "recipient")
ARMS = ("nl", "sense", "ps", "permuted", "bits")

@dataclass(frozen=True)
class Scene:
    actor: str
    action: str
    recipient: str

def scenes():
    return [Scene(a, v, r) for a, v, r in itertools.product(ENTITIES, ACTIONS, ENTITIES)]

def split(s):
    # Withhold whole actor-recipient combinations across every action/paraphrase.
    bucket = (ENTITIES.index(s.actor) + 3 * ENTITIES.index(s.recipient)) % 8
    return "test" if bucket == 0 else "dev" if bucket == 1 else "train"

def counterfactual(s, recipient):
    if recipient not in ENTITIES:
        raise ValueError("unknown recipient")
    return replace(s, recipient=recipient)

def registry(permuted=False):
    names = [*ENTITIES, *ACTIONS, *FIELDS]
    ids = notion_ids(len(names))
    if permuted:
        random.Random(991).shuffle(ids)
    return dict(zip(names, ids))

def render(s, arm, variant=0):
    if arm in ("nl", "sense"):
        verb, obj = {"delegate": ("passes", "authority"), "give": ("passes", "a parcel"), "inform": ("sends", "information")}[s.action]
        if arm == "sense":
            verb += "#" + s.action
        if variant % 2:
            return f"to {s.recipient} {s.actor} {verb} {obj}".split()
        return f"{s.actor} {verb} {obj} to {s.recipient}".split()
    if arm not in ARMS:
        raise ValueError(arm)
    ids = registry(arm == "permuted")
    seq = [ids[x] for x in ("actor", s.actor, "action", s.action, "recipient", s.recipient)]
    if arm == "bits":
        from .codec import encode
        return list(encode(seq))
    return ["ps:" + i for i in seq]

def records(arm, partition):
    return [(s, variant, field, render(s, arm, variant) + ["ask:" + field, "readout"])
            for s in scenes() if split(s) == partition
            for variant in range(2) for field in FIELDS]
