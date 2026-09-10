import json
import pytest
from pansigna.pipeline import build
from pansigna.native import load_corpus, examples, parse_response, run

def test_native_response_has_to_parse_and_resolve_catalog(tmp_path):
    build(tmp_path/"corpus")
    rows, cat, manifest = load_corpus(tmp_path/"corpus")
    ids = {e["key"]:e["bits"] for e in cat}
    assert parse_response(list(ids["alice"]), "bits", cat) == "alice"
    assert parse_response(["ps:"+ids["alice"]], "atomic", cat) == "alice"
    for bad in (["0"], ["1","0"], ["x"]):
        assert parse_response(bad, "bits", cat) is None
    assert examples(rows, "bits", cat)[0]["prompt"] != examples(rows, "atomic", cat)[0]["prompt"]

def test_corpus_tampering_is_rejected(tmp_path):
    build(tmp_path/"corpus")
    p = tmp_path/"corpus/encoded.jsonl"
    p.write_text(p.read_text()+"\n")
    with pytest.raises(ValueError, match="hash"):
        load_corpus(tmp_path/"corpus")

def test_native_training_and_free_generation_smoke(tmp_path):
    build(tmp_path/"corpus")
    result = run(tmp_path/"corpus", "atomic", 8, 2, tmp_path/"model")
    assert result["test"]["none"]["n"] == 144
    assert len(json.loads((tmp_path/"model/responses.json").read_text())) == 144
    assert result["training_objective"] == "full_next_token_native_response"
