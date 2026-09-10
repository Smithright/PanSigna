from pansigna.graphs import worlds, parse, render, rows_for, catalog, counterfactual
import pytest
from pansigna.pipeline import catalog as prior_catalog
from pansigna.codec import decode

def test_graph_split_holds_out_compositions_and_all_variants():
    data=worlds(80,20,20)
    triples={p:{(r['root'],r['middle'],r['target']) for r in data if r['partition']==p} for p in ('train','dev','test')}
    assert not triples['train']&triples['test']
    assert not triples['train']&triples['dev']
    assert len({tuple(sorted(r['edges'].items())) for r in data})==len(data)

def test_parser_distinguishes_link_from_gesture():
    links,gestures=parse('alice points to bob. bob points at carol.')
    assert links=={'alice':'bob'}
    assert gestures==[('bob','carol')]

def test_graph_render_roundtrip_and_native_target():
    data=worlds(10,5,5)
    for w in data:
        for variant in (0,1):
            links,_=parse(render(w,variant))
            assert links==w['edges']
            assert links[links[w['root']]]==w['target']
    rows=rows_for(data,'atomic',catalog())
    assert all(r['answer'][0].startswith('ps:') for r in rows)

def test_intermediate_swap_uses_base_graph_not_donor_answer():
    assert counterfactual({'a':'b','b':'c','d':'e'},'d')=='e'

def test_production_split_retains_component_edges_without_graph_leakage():
    data=worlds()
    edges={p:{(a,b) for w in data if w['partition']==p for a,b in w['edges'].items()}
           for p in ('train','dev','test')}
    assert edges['test']<=edges['train']
    assert edges['dev']<=edges['train']
    rows=rows_for(data,'atomic',catalog())
    assert {p:sum(r['partition']==p for r in rows) for p in edges}==dict(train=3200,dev=640,test=640)
    graph_parts={}
    for r in rows:
        graph_parts.setdefault(r['graph_id'],set()).add(r['partition'])
    assert all(len(v)==1 for v in graph_parts.values())

def test_catalog_extension_and_transcoded_symbols_preserve_identity():
    cat=catalog()
    assert cat[:len(prior_catalog())]==prior_catalog()
    for r in rows_for(worlds(1,1,1),'atomic',cat):
        assert r['prompt'][1:-1]==['ps:'+b for b in decode(r['bits'])]

def test_unknown_and_duplicate_links_are_quarantined():
    for raw in ('alice implies bob.', 'zoe points to bob.',
                'alice points to bob. alice points to carol.'):
        with pytest.raises(ValueError):
            parse(raw)
