import torch
from pansigna.alignment import basis, answer_logprob, position
from pansigna.model import TinyLM
from pansigna.pipeline import catalog, transcode
from pansigna.native import examples
from pansigna.alignment import pairs

def test_alignment_basis_is_orthonormal_and_differentiable():
    raw=torch.randn(12,3,requires_grad=True)
    q=basis(raw)
    assert torch.allclose(q.T@q,torch.eye(3),atol=1e-5)
    ((q@q.T)[0,1]).backward()
    assert raw.grad is not None and raw.grad.abs().sum()>0

def test_answer_likelihood_ignores_prompt_and_padding():
    logits=torch.zeros(2,5,10)
    tokens=torch.tensor([[1,2,3,4,0],[1,2,3,4,5]])
    scores=answer_logprob(logits,tokens,torch.tensor([2,3]),torch.tensor([4,5]))
    assert torch.allclose(scores,torch.full((2,),-2*torch.log(torch.tensor(10.))))

def test_source_position_uses_recipient_span_not_first_same_name():
    row={'raw':'Alice passes authority to Alice.','prompt':['<bos>','alice','passes','authority','to','alice','.','query','recipient','<answer>']}
    assert position(row,'text','source')==5
    assert position(row,'text','readout')==9

def test_bit_source_position_is_recipient_final_bit():
    cat=catalog()
    frame=dict(actor='alice',action='delegate',recipient='hana')
    bits=transcode(frame,cat)
    row=examples([dict(id='x',partition='train',frame=frame,bits=bits,
                      raw_text='Alice passes authority to Hana.')],'bits',cat)[0]
    pos=position(row,'bits','source')
    assert pos==len(bits)
    assert row['prompt'][pos]=='1'
    assert ''.join(row['prompt'][pos+1:pos+9])=='00000000'

def test_counterfactual_donor_semantics_agree_across_queries():
    cat=catalog()
    raw=[]
    for i,(actor,action,recipient) in enumerate([('alice','delegate','bob'),('carol','give','dana'),('erin','inform','frank')]):
        frame=dict(actor=actor,action=action,recipient=recipient)
        # Pair construction only needs the template flag from raw_text.
        raw.append(dict(id=f'x{i}',partition='train',frame=frame,bits=transcode(frame,cat),raw_text='plain template'))
    rows=examples(raw,'atomic',cat)
    paired=pairs(rows,rows,'crossed')
    for ident in ('x0','x1','x2'):
        group=[p for p in paired if p['base']['id'].split(':')[0]==ident]
        assert len({p['donor']['id'].split(':')[0] for p in group})==1
        assert all(p['expected']==(p['donor']['frame']['recipient'] if p['base']['field']=='recipient'
                                  else p['base']['frame'][p['base']['field']]) for p in group)
