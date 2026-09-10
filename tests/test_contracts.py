import itertools
import pytest
from pansigna.codec import valid, encode, decode, notion_ids
from pansigna.world import Scene, scenes, split, render, counterfactual, registry

def test_user_bit_examples():
    assert valid("100000001")
    assert not valid("1000000001")
    assert valid("010001") is False
    assert valid("1010000000011") is False  # unaligned null

def test_all_short_bit_strings_match_rule():
    for n in range(1, 13):
        for bits in itertools.product("01", repeat=n):
            s = "".join(bits)
            assert valid(s) == (s[0] == s[-1] == "1" and "00000000" not in s)

def test_sequence_round_trip_and_strict_framing():
    ids = notion_ids(100)
    assert len(set(ids)) == 100
    assert [int(x, 2) for x in ids] == sorted(int(x, 2) for x in ids)
    assert decode(encode(ids)) == ids
    assert decode(encode([])) == []
    for malformed in ["0", "00000000", "100000000", "000000001", "1x1"]:
        with pytest.raises(ValueError):
            decode(malformed)

def test_invalid_id_rejected():
    with pytest.raises(ValueError):
        encode(["1000000001"])

def test_split_has_no_semantic_overlap():
    groups = [{s for s in scenes() if split(s) == name} for name in ("train", "dev", "test")]
    assert all(groups)
    assert not any(a & b for a, b in itertools.combinations(groups, 2))
    assert set.union(*groups) == set(scenes())

def test_counterfactual_preserves_nonrecipient_fields():
    s = Scene("alice", "delegate", "bob")
    assert counterfactual(s, "carol") == Scene("alice", "delegate", "carol")
    with pytest.raises(ValueError):
        counterfactual(s, "not-an-entity")

def test_ps_permutation_is_bijective_and_consistent():
    a, b = registry(False), registry(True)
    assert set(a) == set(b)
    assert set(a.values()) == set(b.values())
    assert a != b
    s = Scene("alice", "delegate", "bob")
    assert render(s, "ps", 0) == render(s, "ps", 1)
    assert render(s, "nl", 0) != render(s, "nl", 1)
    assert render(s, "ps", 0) != render(s, "permuted", 0)
