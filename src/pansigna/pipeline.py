"""Auditable reference transforms for a declared, controlled English fragment."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from .codec import encode, decode, notion_ids, valid
from .world import ENTITIES, ACTIONS, FIELDS, Scene, scenes, split

VERSION = "controlled-english-v0.2"
DEFINITIONS = {**{e: ("entity", "Named individual " + e) for e in ENTITIES},
    "delegate": ("predicate", "Actor passes authority to recipient in the controlled world"),
    "give": ("predicate", "Actor passes a parcel to recipient in the controlled world"),
    "inform": ("predicate", "Actor sends information to recipient in the controlled world"),
    **{f: ("role", "Event slot " + f) for f in FIELDS},
    "query": ("operator", "Request the value of the following event slot")}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def annotate(text):
    """Accept only the declared grammar. No gold labels, model or metadata input."""
    patterns = [r"(?P<actor>\w+) (?P<verb>passes|sends) (?P<object>authority|a parcel|information) to (?P<recipient>\w+)\.",
                r"To (?P<recipient>\w+), (?P<actor>\w+) (?P<verb>passes|sends) (?P<object>authority|a parcel|information)\."]
    match = next((m for p in patterns if (m := re.fullmatch(p, text, re.I))), None)
    result = {"text":text, "text_sha256":hashlib.sha256(text.encode()).hexdigest(),
              "annotator":"deterministic-reference-parser", "version":VERSION, "spans":[]}
    if not match:
        return {**result, "status":"unresolved", "reason":"outside declared grammar; no sense fabricated"}
    a, r = (match.group(k).lower() for k in ("actor", "recipient"))
    pair = (match.group("verb").lower(), match.group("object").lower())
    senses = {("passes","authority"):"delegate", ("passes","a parcel"):"give", ("sends","information"):"inform"}
    if a not in ENTITIES or r not in ENTITIES or pair not in senses:
        return {**result, "status":"unresolved", "reason":"unregistered entity or unresolved predicate sense"}
    action = senses[pair]
    for group, sense in (("actor",a), ("verb",action), ("object","context:"+action), ("recipient",r)):
        start, end = match.span(group)
        result["spans"].append({"role":group,"surface":text[start:end],"start":start,"end":end,"sense":sense})
    result["status"] = "annotated"
    return result

def assign(annotation):
    if annotation["status"] != "annotated":
        raise ValueError("unresolved annotation cannot enter the accepted corpus")
    by_role = {s["role"]:s["sense"] for s in annotation["spans"]}
    frame = {"actor":by_role["actor"], "action":by_role["verb"], "recipient":by_role["recipient"]}
    if frame["actor"] not in ENTITIES or frame["recipient"] not in ENTITIES or frame["action"] not in ACTIONS:
        raise ValueError("invalid assignment")
    return frame

def catalog(existing=None):
    entries = [] if existing is None else [dict(e) for e in existing]
    if len({e["key"] for e in entries}) != len(entries) or len({e["bits"] for e in entries}) != len(entries):
        raise ValueError("duplicate identity")
    for e in entries:
        if not valid(e["bits"]) or e["key"] not in DEFINITIONS or (e["kind"], e["definition"]) != DEFINITIONS[e["key"]]:
            raise ValueError("invalid index or changed definition without version migration")
    known = {e["key"] for e in entries}
    used = {e["bits"] for e in entries}
    available = (b for b in notion_ids(len(DEFINITIONS)+len(entries)) if b not in used)
    for key, (kind, definition) in DEFINITIONS.items():
        if key not in known:
            entries.append({"key":key,"kind":kind,"definition":definition,"version":"0.2",
                            "namespace":"pansigna:experimental:controlled-world", "bits":next(available)})
    return entries

def transcode(frame, entries):
    ids = {e["key"]:e["bits"] for e in entries}
    if set(frame) != set(FIELDS):
        raise ValueError("unexpected frame slots")
    if frame["actor"] not in ENTITIES or frame["recipient"] not in ENTITIES or frame["action"] not in ACTIONS:
        raise ValueError("frame type mismatch")
    return encode([ids[x] for f in FIELDS for x in (f, frame[f])])

def read_encoding(bits, entries):
    inverse = {e["bits"]:e["key"] for e in entries}
    try:
        symbols = [inverse[b] for b in decode(bits)]
    except KeyError as exc:
        raise ValueError("unregistered identifier") from exc
    if len(symbols) != 6 or symbols[::2] != list(FIELDS):
        raise ValueError("invalid event syntax")
    frame = dict(zip(FIELDS, symbols[1::2]))
    transcode(frame, entries)  # type validation
    return frame

def canonical_text(frame):
    verb, obj = {"delegate":("passes","authority"),"give":("passes","a parcel"),"inform":("sends","information")}[frame["action"]]
    return f"{frame['actor'].title()} {verb} {obj} to {frame['recipient'].title()}."

def build(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    raw, gold = [], []
    for scene in scenes():
        frame = {f:getattr(scene,f) for f in FIELDS}
        normal = canonical_text(frame)
        for variant in range(2):
            text = normal if variant == 0 else f"To {scene.recipient.title()}, " + normal.split(" to ")[0] + "."
            ident = f"controlled-{len(raw):04d}"
            raw.append({"id":ident,"text":text,"source":"assistant-authored synthetic grammar","license":"MIT"})
            gold.append({"id":ident,"frame":frame})
    for i, text in enumerate(("Alice passes something to Bob.","Alice thinks about Bob.","Alice passes authority to Zoe.")):
        raw.append({"id":f"challenge-{i}","text":text,"source":"assistant-authored negative control","license":"MIT"})
    annotations, assignments, encoded = [], [], []
    entries = catalog()
    catalog_hash = digest(entries)
    for record in raw:
        a = {"id":record["id"], **annotate(record["text"])}
        annotations.append(a)
        if a["status"] != "annotated":
            continue
        frame = assign(a)
        assignment = {"id":record["id"],"frame":frame,"annotation_sha256":digest(a),"catalog_sha256":catalog_hash}
        assignments.append(assignment)
        stream = transcode(frame, entries)
        assert read_encoding(stream, entries) == frame
        encoded.append({"id":record["id"],"bits":stream,"frame":frame,"raw_text":record["text"],
                        "partition":split(Scene(**frame)),"assignment_sha256":digest(assignment),"catalog_sha256":catalog_hash})
    actual = {a["id"]:a["frame"] for a in assignments}
    accuracy = sum(actual.get(g["id"]) == g["frame"] for g in gold)/len(gold)
    stages = {"raw.jsonl":raw,"gold.jsonl":gold,"annotations.jsonl":annotations,"assignments.jsonl":assignments,"encoded.jsonl":encoded}
    for name, rows in stages.items():
        (out/name).write_text("".join(json.dumps(row,sort_keys=True)+"\n" for row in rows))
    (out/"catalog.json").write_text(json.dumps(entries,indent=2)+"\n")
    (out/"index.json").write_text(json.dumps({"catalog_sha256":catalog_hash,"items":{e["key"]:e["bits"] for e in entries}},indent=2)+"\n")
    manifest = {"version":VERSION,"corpus_scope":"controlled synthetic English only","accepted":len(encoded),
                "quarantined":len(raw)-len(encoded),"annotation_accuracy":accuracy,
                "annotation_accuracy_scope":"same-author generated oracle, not independent human evaluation",
                "semantic_roundtrip_count":len(encoded),"catalog_sha256":catalog_hash,
                "files":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())}}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    print(json.dumps(build(p.parse_args().out), indent=2))

if __name__ == "__main__":
    main()
