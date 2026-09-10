"""v0.3A: frozen-network, counterfactual-trained orthogonal alignment pilot."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import time
import torch
from .model import TinyLM, fit_subspace
from .native import load_corpus, examples, tensors, generate, parse_response
from .pipeline import annotate
from .world import ENTITIES

def basis(raw):
    return torch.linalg.qr(raw,mode='reduced').Q

def position(row,arm,site):
    if site=='readout': return len(row['prompt'])-1
    if arm=='atomic': return 6
    if arm=='bits':
        stream=''.join(row['prompt'][1:-1])
        identifiers=stream.split('00000000')
        return sum(map(len,identifiers[:6]))+5*8  # final bit of recipient ID; BOS offset included
    span=next(s for s in annotate(row['raw'])['spans'] if s['role']=='recipient')
    tokens=list(re.finditer(r'\w+|[^\w\s]',row['raw'].lower()))
    return 1+next(i for i,t in enumerate(tokens) if t.start()==span['start'])

def pairs(rows,pool,mode):
    result=[]
    for b in rows:
        candidates=[d for d in pool if d['field']==b['field'] and d['raw'].startswith('To ')==b['raw'].startswith('To ')
                    and d['frame']['recipient']!=b['frame']['recipient']
                    and all((d['frame'][f]==b['frame'][f]) if mode=='minimal' else (d['frame'][f]!=b['frame'][f]) for f in ('actor','action'))]
        if not candidates: raise ValueError('no donor')
        candidates.sort(key=lambda d:d['id'])
        index=int(hashlib.sha256(b['id'].split(':')[0].encode()).hexdigest()[:8],16)%len(candidates)
        d=candidates[index]
        target=d if b['field']=='recipient' else b
        result.append({'base':b,'donor':d,'answer':target['answer'],'expected':target['frame'][target['field']]})
    return result

@torch.no_grad()
def hidden(model,rows,vocab,arm,layer,site):
    x,lengths=tensors([r['prompt'] for r in rows],vocab)
    _,h=model(x,lengths,capture_layer=layer)
    return h[torch.arange(len(rows)),torch.tensor([position(r,arm,site) for r in rows])]

def answer_logprob(logits,tokens,prompt_lengths,total_lengths):
    scores=logits[:,:-1].log_softmax(-1).gather(-1,tokens[:,1:,None]).squeeze(-1)
    t=torch.arange(scores.shape[1])[None,:]
    mask=(t>=prompt_lengths[:,None]-1)&(t<total_lengths[:,None]-1)
    return (scores*mask).sum(-1)

def prepared(ps,vocab,arm,site,original=False):
    sequences=[p['base']['prompt']+(p['base']['answer'] if original else p['answer']) for p in ps]
    x,lengths=tensors(sequences,vocab)
    starts=torch.tensor([len(p['base']['prompt']) for p in ps])
    positions=torch.tensor([position(p['base'],arm,site) for p in ps])
    return x,lengths,starts,positions

def fit(model,ps,vocab,arm,layer,site,rank,steps,seed,shuffle=False):
    torch.manual_seed(seed)
    donor=hidden(model,[p['donor'] for p in ps],vocab,arm,layer,site)
    x,lengths,starts,positions=prepared(ps,vocab,arm,site)
    if shuffle:
        # Corrupt donor assignments while preserving all answer and padding lengths.
        donor=donor[torch.randperm(len(donor))]
    raw=torch.nn.Parameter(torch.randn(48,rank))
    opt=torch.optim.Adam([raw],lr=.03)
    generator=torch.Generator().manual_seed(seed+5)
    for _ in range(steps):
        idx=torch.randint(len(ps),(32,),generator=generator)
        q=basis(raw)
        logits,_=model(x[idx],lengths[idx],intervention=(layer,donor[idx],q,positions[idx]))
        loss=-answer_logprob(logits,x[idx],starts[idx],lengths[idx]).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return basis(raw).detach()

@torch.no_grad()
def assess(model,ps,vocab,cat,arm,layer,site,q):
    donor=hidden(model,[p['donor'] for p in ps],vocab,arm,layer,site)
    positions=torch.tensor([position(p['base'],arm,site) for p in ps])
    intervention=(layer,donor,q,positions)
    outputs,done=generate(model,[p['base'] for p in ps],vocab,intervention=intervention)
    predictions=[parse_response(o,arm,cat) if d else None for o,d in zip(outputs,done)]
    scores=[]
    for original in (False,True):
        x,lengths,starts,pos=prepared(ps,vocab,arm,site,original)
        logits,_=model(x,lengths,intervention=intervention)
        scores.append(answer_logprob(logits,x,starts,lengths))
    details=[]
    for i,(p,value) in enumerate(zip(ps,predictions)):
        details.append({'id':p['base']['id'],'donor_id':p['donor']['id'],'field':p['base']['field'],
                        'decoded':value,'expected':p['expected'],'correct':value==p['expected'],
                        'log_margin':float(scores[0][i]-scores[1][i]),'generated':outputs[i]})
    recipient=[d for d in details if d['field']=='recipient']
    other=[d for d in details if d['field']!='recipient']
    grouped={}
    for d in details: grouped.setdefault(d['id'].split(':')[0],[]).append(d['correct'])
    return {'recipient_success':sum(d['correct'] for d in recipient),'recipient_n':len(recipient),
            'other_correct':sum(d['correct'] for d in other),'other_n':len(other),
            'joint_success':sum(all(v) for v in grouped.values()),'joint_n':len(grouped),
            'recipient_margin':sum(d['log_margin'] for d in recipient)/len(recipient)},details

def weight_hash(model):
    h=hashlib.sha256()
    for name,p in model.state_dict().items(): h.update(name.encode()+p.cpu().numpy().tobytes())
    return h.hexdigest()

def run(checkpoint,corpus,out,steps=200,randomized=False):
    out=Path(out); out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(2)
    c=torch.load(checkpoint,map_location='cpu',weights_only=True)
    arm=c['manifest']['arm']; seed=c['manifest']['seed']; vocab=c['manifest']['vocab']
    torch.manual_seed(seed+3000)
    model=TinyLM(len(vocab)).eval()
    if not randomized: model.load_state_dict(c['state_dict'])
    for p in model.parameters(): p.requires_grad_(False)
    before=weight_hash(model)
    raw,cat,_=load_corpus(corpus)
    all_rows=examples(raw,arm,cat)
    rows={p:[r for r in all_rows if r['partition']==p] for p in ('train','dev','test')}
    # Minimal diagnostic donors need a different split because each held-out actor
    # has only one held-out recipient in v0.2. Training fit still uses train-only donors.
    train=pairs(rows['train'],rows['train'],'minimal')+pairs(rows['train'],rows['train'],'crossed')
    dev=pairs(rows['dev'],all_rows,'minimal')+pairs(rows['dev'],all_rows,'crossed')
    started=time.time(); candidates=[]
    for layer in (0,1):
        for site in ('readout','source'):
            for rank in (2,7):
                q=fit(model,train,vocab,arm,layer,site,rank,steps,seed+17)
                m,_=assess(model,dev,vocab,cat,arm,layer,site,q)
                score=(m['recipient_success']/m['recipient_n']+m['other_correct']/m['other_n'])/2
                candidates.append((score,layer,site,rank,q,m))
    _,layer,site,rank,q,_=max(candidates,key=lambda c:c[0])
    train_h=hidden(model,rows['train'],vocab,arm,layer,site)
    labels=torch.tensor([ENTITIES.index(r['frame']['recipient']) for r in rows['train']])
    ridge=fit_subspace(train_h,labels,len(ENTITIES))
    torch.manual_seed(seed+900)
    rand=basis(torch.randn(48,rank))
    shuffled=fit(model,train,vocab,arm,layer,site,rank,steps,seed+17,shuffle=True)
    controls={'none':torch.zeros(48,0),'aligned':q,'ridge':ridge,'random':rand,'shuffled_donor':shuffled,'full_state':torch.eye(48)}
    tests={}; logs={}
    for mode in ('minimal','crossed'):
        ps=pairs(rows['test'],all_rows,mode)
        tests[mode]={}; logs[mode]={}
        for name,mapping in controls.items():
            tests[mode][name],logs[mode][name]=assess(model,ps,vocab,cat,arm,layer,site,mapping)
    assert weight_hash(model)==before,'base model changed during alignment'
    result={'phase':'v03A_exploratory_reused_corpus','arm':arm,'seed':seed,'randomized':randomized,
            'steps_per_mapping':steps,'selected':{'layer':layer,'site':site,'rank':rank},'tests':tests,
            'candidates':[{'score':s,'layer':l,'site':loc,'rank':r,'metrics':m} for s,l,loc,r,_,m in candidates],
            'seconds':time.time()-started,'base_weights_sha256':before,'weights_unchanged':True,
            'donor_scope':'fit uses train only; diagnostic dev/test donor pool spans v0.2 partitions',
            'checkpoint_sha256':hashlib.sha256(Path(checkpoint).read_bytes()).hexdigest(),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'pairs.json').write_text(json.dumps(logs,indent=2)+'\n')
    torch.save({'basis':q,'selected':result['selected']},out/'mapping.pt')
    print(json.dumps({'arm':arm,'seed':seed,'randomized':randomized,'selected':result['selected'],'crossed':tests['crossed'],'seconds':result['seconds']}),flush=True)
    return result

def main():
    p=argparse.ArgumentParser(); p.add_argument('--models',required=True); p.add_argument('--corpus',required=True); p.add_argument('--out',required=True)
    p.add_argument('--steps',type=int,default=200); p.add_argument('--arms',nargs='+',default=['text','atomic','bits']); p.add_argument('--seeds',nargs='+',type=int,default=[3,11,29])
    p.add_argument('--randomized',action='store_true'); a=p.parse_args()
    targets=[(arm,seed,Path(a.out)/f'{arm}-seed{seed}') for arm in a.arms for seed in a.seeds]
    if a.steps<1 or any(dest.exists() for _,_,dest in targets): p.error('positive steps and fresh output paths required')
    for arm,seed,dest in targets: run(Path(a.models)/f'{arm}-seed{seed}'/'checkpoint.pt',a.corpus,dest,a.steps,a.randomized)

if __name__=='__main__': main()
