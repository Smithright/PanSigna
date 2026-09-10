import pytest
from pansigna.pipeline import annotate, assign, catalog, transcode, read_encoding, build

def test_raw_text_disambiguation_uses_context_and_spans():
    authority = annotate("Alice passes authority to Bob.")
    parcel = annotate("Alice passes a parcel to Bob.")
    assert assign(authority)["action"] == "delegate"
    assert assign(parcel)["action"] == "give"
    for a in (authority, parcel):
        for span in a["spans"]:
            assert a["text"][span["start"]:span["end"]] == span["surface"]

def test_annotation_abstains_on_unresolved_or_unknown_content():
    for text in ("Alice passes something to Bob.", "Alice thinks about Bob.", "Alice passes authority to Zoe."):
        a = annotate(text)
        assert a["status"] == "unresolved"
        with pytest.raises(ValueError):
            assign(a)

def test_catalog_encoding_roundtrip_and_stability():
    c = catalog()
    frame = assign(annotate("To Carol, Alice passes authority."))
    assert read_encoding(transcode(frame, c), c) == frame
    assert catalog(existing=c) == c
    altered = [dict(x) for x in c]
    altered[0]["bits"] = "1000000001"
    with pytest.raises(ValueError):
        catalog(existing=altered)

def test_full_chain_exports_all_stages_and_gold_is_separate(tmp_path):
    manifest = build(tmp_path/"corpus")
    assert manifest["annotation_accuracy"] == 1.0
    assert manifest["accepted"] == 384
    assert manifest["quarantined"] == 3
    for name in ("raw.jsonl", "annotations.jsonl", "assignments.jsonl", "catalog.json", "index.json", "encoded.jsonl", "gold.jsonl", "manifest.json"):
        assert (tmp_path/"corpus"/name).exists()
    with pytest.raises(FileExistsError):
        build(tmp_path/"corpus")
