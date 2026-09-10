"""Fresh, controlled graph calibration: raw language -> sense/IR -> native LM.

This is a same-author synthetic parser/oracle, not natural-language WSD validation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import time

import torch

from .codec import encode, decode, notion_ids
from .model import TinyLM
from .native import tensors, generate, parse_response
from .pipeline import catalog as old_catalog, digest
from .world import ENTITIES


def worlds(ntrain=800, ndev=160, ntest=160, seed=1041):
    rng = random.Random(seed)
    desired = dict(train=ntrain, dev=ndev, test=ntest)
    counts = dict.fromkeys(desired, 0)
    seen, result = set(), []
    for attempt in range(1000000):
        if counts == desired:
            return result
        targets = rng.sample(list(ENTITIES), len(ENTITIES))
        edges = dict(zip(ENTITIES, targets))
        signature = tuple(targets)
        if signature in seen:
            continue
        root = rng.choice(ENTITIES)
        middle, target = edges[root], edges[edges[root]]
        if len({root, middle, target}) != 3:
            continue
        bucket = (ENTITIES.index(root) + 2*ENTITIES.index(middle) + 3*ENTITIES.index(target)) % 10
        partition = 'train' if bucket < 7 else 'dev' if bucket == 7 else 'test'
        if counts[partition] == desired[partition]:
            continue
        seen.add(signature)
        counts[partition] += 1
        result.append(dict(id=f'graph-{len(result):05d}', partition=partition, edges=edges,
                           root=root, middle=middle, target=target,
                           other=rng.choice([e for e in ENTITIES if e not in (root, middle)]),
                           order=rng.sample(list(ENTITIES), len(ENTITIES)),
                           gestures=[rng.sample(list(ENTITIES), 2) for _ in range(2)]))
    raise ValueError('requested graph split exceeds generation budget')


def render(world, variant=0):
    patterns = [('{} points to {}.', '{} points at {}.'),
                ('from {} a link reaches {}.', 'from {} a gesture indicates {}.'),
                ('{} has a link ending at {}.', '{} makes a gesture toward {}.')]
    edge, gesture = patterns[variant]
    statements = [edge.format(a, world['edges'][a]) for a in world['order']]
    for i, (a, b) in enumerate(world['gestures']):
        statements.insert(2+3*i, gesture.format(a, b))
    return ' '.join(statements)


def parse(raw):
    links, gestures = {}, []
    patterns = [(r'(\w+) points to (\w+)', 'edge'), (r'(\w+) points at (\w+)', 'gesture'),
                (r'from (\w+) a link reaches (\w+)', 'edge'),
                (r'from (\w+) a gesture indicates (\w+)', 'gesture'),
                (r'(\w+) has a link ending at (\w+)', 'edge'),
                (r'(\w+) makes a gesture toward (\w+)', 'gesture')]
    for statement in raw.lower().split('.'):
        statement = statement.strip()
        if not statement:
            continue
        found = False
        for pattern, kind in patterns:
            m = re.fullmatch(pattern, statement)
            if m:
                a, b = m.groups()
                if a not in ENTITIES or b not in ENTITIES:
                    raise ValueError('unregistered graph entity')
                if kind == 'edge':
                    if a in links:
                        raise ValueError('duplicate outgoing edge')
                    links[a] = b
                else:
                    gestures.append((a,b))
                found = True
                break
        if not found:
            raise ValueError('outside declared graph grammar')
    return links, gestures


def catalog():
    entries = old_catalog()
    definitions = {'edge':'Directed functional link from first entity to second entity',
                   'gesture':'Non-link gesture by first entity toward second entity',
                   'follow2':'Apply the graph successor function exactly twice to the query entity',
                   'next':'Apply the graph successor function once to the query entity'}
    used = {e['bits'] for e in entries}
    available = iter(b for b in notion_ids(len(entries)+len(definitions)) if b not in used)
    for key, definition in definitions.items():
        entries.append(dict(key=key, kind='operator' if key in ('follow2','next') else 'predicate',
                            definition=definition, version='0.3',
                            namespace='pansigna:experimental:graph', bits=next(available)))
    return entries


def counterfactual(base_edges, donor_middle):
    """Intervene on z after z=G(root), then compute G_base(z); not donor's answer."""
    return base_edges[donor_middle]


def rows_for(data, arm, cat, variants=(0,1)):
    if arm not in ('text','sense','atomic'):
        raise ValueError('unsupported graph arm')
    ids = {e['key']:e['bits'] for e in cat}
    rows = []
    for w in data:
        for variant in variants:
            raw = render(w,variant)
            edges, gestures = parse(raw)  # ingress reads raw text, not oracle metadata
            assert edges == w['edges']
            for query in ('follow2','next'):
                start = w['root'] if query == 'follow2' else w['other']
                answer = edges[edges[start]] if query == 'follow2' else edges[start]
                symbols = [s for a,b in edges.items() for s in ('edge',a,b)]
                symbols += [s for a,b in gestures for s in ('gesture',a,b)]
                symbols += ['query',query,start]
                stream = encode([ids[s] for s in symbols])
                assert [ids[s] for s in symbols] == decode(stream)
                if arm == 'atomic':
                    prompt = ['ps:'+b for b in decode(stream)]
                    response = ['ps:'+ids[answer]]
                else:
                    prompt_raw = raw
                    if arm == 'sense':
                        for phrase, tag in [('points to','points edge_sense to'), ('points at','points gesture_sense at'),
                                            ('a link','a edge_sense link'), ('a gesture','a gesture_sense gesture')]:
                            prompt_raw = prompt_raw.replace(phrase,tag)
                    prompt = re.findall(r'\w+|[^\w\s]',prompt_raw)+['query',query,start]
                    response = [answer]
                rows.append(dict(id=f"{w['id']}:v{variant}:{query}", graph_id=w['id'],
                                 partition=w['partition'], variant=variant, field=query,
                                 prompt=['<bos>']+prompt+['<answer>'], answer=response+['<eos>'],
                                 expected=answer, raw=raw, bits=stream,
                                 annotation=dict(edges=edges,gestures=gestures),
                                 frame=dict(root=start,middle=edges[start],target=answer),
                                 catalog_sha256=digest(cat)))
    return rows


@torch.no_grad()
def evaluate(model, rows, vocab, arm, cat):
    samples=[]
    for offset in range(0,len(rows),64):
        batch=rows[offset:offset+64]
        outputs,stopped=generate(model,batch,vocab,max_new=3)
        for row,tokens,end in zip(batch,outputs,stopped):
            value=parse_response(tokens,'atomic' if arm=='atomic' else 'text',cat) if end else None
            samples.append(dict(id=row['id'],field=row['field'],expected=row['expected'],
                                generated=tokens,terminated=end,decoded=value,correct=value==row['expected']))
    metrics={f:dict(n=sum(s['field']==f for s in samples),
                    correct=sum(s['correct'] for s in samples if s['field']==f)) for f in ('follow2','next')}
    metrics['legible']=sum(s['decoded'] is not None for s in samples)
    metrics['terminated']=sum(s['terminated'] for s in samples)
    return metrics,samples


def competent(metrics):
    return all(metrics[f]['correct']/metrics[f]['n'] >= .95 for f in ('follow2','next'))


def run(out, arm, seed=41, initial_steps=2000, max_steps=6000):
    out=Path(out)
    out.mkdir(parents=True,exist_ok=False)
    cat=catalog()
    data=worlds()
    train_edges={(a,b) for w in data if w['partition']=='train' for a,b in w['edges'].items()}
    assert all((a,b) in train_edges for w in data for a,b in w['edges'].items())
    rows=rows_for(data,arm,cat)
    groups={p:[r for r in rows if r['partition']==p] for p in ('train','dev','test')}
    surface=rows_for([w for w in data if w['partition']=='test'],arm,cat,variants=(2,))
    # The declared vocabulary includes held-out template words; those embeddings are untrained.
    words=set(t for r in rows+surface for t in r['prompt']+r['answer'])
    vocab={w:i for i,w in enumerate(['<pad>']+sorted(words))}
    config=dict(version='graph-calibration-v0.3B',arm=arm,seed=seed,width=48,layers=3,heads=4,
                initial_steps=initial_steps,max_steps=max_steps,gate=.95,batch=64,lr=.003,
                objective='full next-token loss including prompts',
                comparison='exposure-matched calibration; not compute matched or confirmatory',
                split='triple bucket before rendering; whole graph unique; templates 0/1 seen, 2 unseen',
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                data_sha256=digest(data),catalog_sha256=digest(cat),vocab=vocab,
                torch_version=str(torch.__version__))
    (out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    (out/'worlds.json').write_text(json.dumps(data,indent=2)+'\n')
    (out/'catalog.json').write_text(json.dumps(cat,indent=2)+'\n')
    (out/'rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows+surface))
    torch.set_num_threads(2)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    model=TinyLM(len(vocab),width=48,layers=3,heads=4)
    optimizer=torch.optim.AdamW(model.parameters(),lr=.003)
    rng=torch.Generator().manual_seed(seed+100)
    full,lengths=tensors([r['prompt']+r['answer'] for r in groups['train']],vocab)
    started=time.time()
    logs,dev_checks=[],[]
    tokens_seen=0
    for step in range(1,max_steps+1):
        ix=torch.randint(len(full),(64,),generator=rng)
        batch=full[ix,:-1]
        logits,_=model(batch,lengths[ix]-1)
        loss=torch.nn.functional.cross_entropy(logits.reshape(-1,len(vocab)),full[ix,1:].reshape(-1),ignore_index=0)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        tokens_seen+=int((lengths[ix]-1).sum())
        if step==1 or step%200==0:
            log=dict(arm=arm,step=step,loss=loss.item(),seconds=time.time()-started)
            logs.append(log)
            print(json.dumps(log),flush=True)
        if step in (initial_steps,max_steps):
            model.eval()
            metrics,_=evaluate(model,groups['dev'],vocab,arm,cat)
            dev_checks.append(dict(step=step,metrics=metrics,gate_pass=competent(metrics)))
            print(json.dumps(dict(arm=arm,development=dev_checks[-1])),flush=True)
            if competent(metrics):
                break
            model.train()
    model.eval()
    test,samples=evaluate(model,groups['test'],vocab,arm,cat)
    unseen,unseen_samples=evaluate(model,surface,vocab,arm,cat)
    baselines={}
    for name in ('first_name','last_name','last_edge_target'):
        predicted=[]
        for r in groups['test']:
            names=[t for t in re.findall(r'\w+',r['raw']) if t in ENTITIES]
            guess=names[0] if name=='first_name' else names[-1] if name=='last_name' else list(r['annotation']['edges'].values())[-1]
            predicted.append(guess==r['expected'])
        baselines[name]=dict(correct=sum(predicted),n=len(predicted))
    result=dict(config=config,steps=step,parameters=sum(p.numel() for p in model.parameters()),
                tokens_seen=tokens_seen,seconds=time.time()-started,logs=logs,development=dev_checks,
                competence_gate_pass=competent(dev_checks[-1]['metrics']),test=test,unseen_surface=unseen,
                shortcut_baselines=baselines,
                scope='Single seed calibration. Deterministic same-author synthetic sense annotation; no causal result yet.')
    torch.save(dict(state_dict=model.state_dict(),config=config,catalog=cat),out/'model.pt')
    (out/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'generations.json').write_text(json.dumps(dict(test=samples,unseen_surface=unseen_samples),indent=2)+'\n')
    print(json.dumps(dict(arm=arm,gate=result['competence_gate_pass'],test=test,unseen_surface=unseen)),flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',required=True)
    p.add_argument('--arms',nargs='+',default=['text','sense','atomic'])
    p.add_argument('--seed',type=int,default=41)
    p.add_argument('--initial-steps',type=int,default=2000)
    p.add_argument('--max-steps',type=int,default=6000)
    args=p.parse_args()
    for arm in args.arms:
        run(Path(args.out)/f'{arm}-seed{args.seed}',arm,args.seed,args.initial_steps,args.max_steps)
