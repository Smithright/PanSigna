import math
import json

import torch
from pansigna import learning_controls

from pansigna.learning_controls import loss_terms, sample_schedule, make_inputs, state_hash, run
from pansigna.model import TinyLM


def test_answer_loss_includes_whole_answer_and_eos_only():
    # Full sequence: BOS, prompt, boundary, answer1, answer2, EOS, pad.
    tokens = torch.tensor([[1, 2, 3, 4, 5, 6, 0]])
    logits = torch.zeros(1, 6, 7, requires_grad=True)
    full, answer, counts = loss_terms(logits, tokens, torch.tensor([3]), torch.tensor([6]))
    assert counts == {'full_targets': 5, 'answer_targets': 3}
    assert abs(answer.item() - math.log(7)) < 1e-6
    answer.backward()
    assert logits.grad[0, :2].abs().sum() == 0
    assert logits.grad[0, 2:5].abs().sum() > 0
    assert logits.grad[0, 5].abs().sum() == 0
    assert all(logits.grad[0, i, target] < 0 for i, target in ((2,4),(3,5),(4,6)))


def test_full_loss_includes_prompt_targets_and_excludes_padding():
    tokens = torch.tensor([[1, 2, 3, 0], [1, 2, 3, 4]])
    logits = torch.zeros(2, 3, 5, requires_grad=True)
    full, _, counts = loss_terms(logits, tokens, torch.tensor([2,2]), torch.tensor([3,4]))
    assert counts == {'full_targets': 5, 'answer_targets': 3}
    full.backward()
    assert logits.grad[0,2].abs().sum() == 0
    assert logits.grad[0,0].abs().sum() > 0
    assert logits.grad[1,2].abs().sum() > 0


def test_schedule_is_reproducible_and_independent_of_objective_rng():
    a = sample_schedule(10, 3, 4, 143)
    torch.rand(400)
    b = sample_schedule(10, 3, 4, 143)
    assert torch.equal(a,b)
    assert a.shape == (3,4)
    assert (a >= 0).all() and (a < 10).all()


def test_inputs_retain_only_next_and_original_variants_and_paired_identity():
    rows, groups, vocab, cat, data = make_inputs('atomic', 8, 2, 2)
    assert len(rows) == 24
    assert all(r['field']=='next' and r['variant'] in (0,1) for r in rows)
    assert {p:len(rs) for p,rs in groups.items()} == dict(train=16,dev=4,test=4)
    assert vocab['<pad>'] == 0
    torch.manual_seed(43)
    model = TinyLM(len(vocab),width=48,layers=3,heads=4)
    clone = TinyLM(len(vocab),width=48,layers=3,heads=4)
    clone.load_state_dict(model.state_dict())
    assert state_hash(model.state_dict()) == state_hash(clone.state_dict())


def test_smoke_preserves_pairing_outputs_and_marks_nonprotocol_run(tmp_path):
    summary = run(tmp_path/'smoke','atomic',initial_steps=1,max_steps=2,
                  ntrain=4,ndev=2,ntest=2,batch=2)
    assert summary['config']['declared_design'] is False
    results = {name:json.loads((tmp_path/'smoke'/name/'metrics.json').read_text())
               for name in ('full','answer_only')}
    assert results['full']['initial_state_sha256'] == results['answer_only']['initial_state_sha256']
    assert results['full']['schedule_sha256'] == results['answer_only']['schedule_sha256']
    assert results['full']['rows_sha256'] == results['answer_only']['rows_sha256']
    for result in results.values():
        first = result['checkpoints'][0]
        assert first['step'] == 1
        assert first['exposures']['records'] == 2
        assert first['exposures']['answer_targets'] == 4
        assert first['evaluation']['test']['exact']['n'] == 4
        generations = json.loads((tmp_path/'smoke'/result['objective']/'generations-1.json').read_text())
        assert len(generations['train']) == 8
        assert len(generations['dev']) == len(generations['test']) == 4
    f = results['full']['checkpoints'][0]['exposures']
    a = results['answer_only']['checkpoints'][0]['exposures']
    assert f['input_tokens'] == a['input_tokens']
    assert f['supervised_targets'] == f['full_targets']
    assert a['supervised_targets'] == a['answer_targets']


def test_both_stopping_decisions_precede_first_test_evaluation(tmp_path,monkeypatch):
    root = tmp_path/'ordering'
    original = learning_controls.diagnostics
    events = []

    def witnessed(model,rows,*args,**kwargs):
        partition = rows[0]['partition']
        events.append(partition)
        if partition == 'test':
            for objective in ('full','answer_only'):
                decision = root/objective/'stopping.json'
                assert decision.exists(), f'test accessed before {objective} stopped'
                assert json.loads(decision.read_text())['test_accessed'] is False
        return original(model,rows,*args,**kwargs)

    monkeypatch.setattr(learning_controls,'diagnostics',witnessed)
    run(root,'atomic',initial_steps=1,max_steps=1,ntrain=4,ndev=2,ntest=2,batch=2)
    assert events.count('test') == 2
    assert events[:2] == ['dev','dev']
