"""Paired one-hop objective calibration; see docs/v04-learning-control-protocol.md."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import torch
import torch.nn.functional as F

from . import graphs, model as model_module, native
from .graphs import worlds, rows_for, catalog, evaluate
from .model import TinyLM
from .native import tensors
from .pipeline import digest


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tensor_hash(value):
    value = value.detach().cpu().contiguous()
    h = hashlib.sha256(str((str(value.dtype), tuple(value.shape))).encode())
    h.update(value.numpy().tobytes())
    return h.hexdigest()


def state_hash(state):
    return digest({key: tensor_hash(value) for key, value in sorted(state.items())})


def sample_schedule(nrows, steps, batch, seed):
    return torch.randint(nrows, (steps, batch), generator=torch.Generator().manual_seed(seed))


def make_inputs(arm, ntrain=800, ndev=160, ntest=160, data_seed=1041):
    if arm not in ('text', 'atomic'):
        raise ValueError('this control is restricted to text and atomic')
    data, cat = worlds(ntrain, ndev, ntest, seed=data_seed), catalog()
    rows = [r for r in rows_for(data, arm, cat, variants=(0,1)) if r['field'] == 'next']
    groups = {p:[r for r in rows if r['partition']==p] for p in ('train','dev','test')}
    # Vocabulary is the declared grammar, not a learned statistic of test answers.
    words = sorted({t for r in rows for t in r['prompt']+r['answer']})
    vocab = {w:i for i,w in enumerate(['<pad>']+words)}
    return rows, groups, vocab, cat, data


def loss_terms(logits, sequences, prompt_lengths, lengths):
    """Shifted target j belongs to answer iff j+1 >= prompt length; include EOS."""
    targets = sequences[:,1:]
    positions = torch.arange(1,sequences.shape[1],device=sequences.device)[None,:]
    valid = (positions < lengths[:,None]) & targets.ne(0)
    answer_mask = valid & (positions >= prompt_lengths[:,None])
    losses = F.cross_entropy(logits.transpose(1,2),targets,reduction='none')
    if not bool(valid.any()) or not bool(answer_mask.any()):
        raise ValueError('every loss batch needs nonpadding full and answer targets')
    return (losses[valid].mean(), losses[answer_mask].mean(),
            dict(full_targets=int(valid.sum()),answer_targets=int(answer_mask.sum())))


@torch.no_grad()
def diagnostics(model, rows, vocab, arm, cat):
    metrics, outputs = evaluate(model,rows,vocab,arm,cat)
    sums = dict(full=0.,answer=0.)
    counts = dict(full_targets=0,answer_targets=0)
    for start in range(0,len(rows),64):
        batch = rows[start:start+64]
        seq,lengths = tensors([r['prompt']+r['answer'] for r in batch],vocab)
        logits,_ = model(seq[:,:-1],lengths-1)
        full,answer,n = loss_terms(logits,seq,torch.tensor([len(r['prompt']) for r in batch]),lengths)
        sums['full'] += float(full)*n['full_targets']
        sums['answer'] += float(answer)*n['answer_targets']
        for key in counts:
            counts[key] += n[key]
    return dict(exact=metrics['next'],legible=metrics['legible'],terminated=metrics['terminated'],
                full_loss=sums['full']/counts['full_targets'],
                answer_loss=sums['answer']/counts['answer_targets'],**counts),outputs


def write_json(path, value):
    Path(path).write_text(json.dumps(value,indent=2)+'\n')


def run(out, arm, seed=43, initial_steps=2000, max_steps=6000,
        ntrain=800, ndev=160, ntest=160, batch=64, data_seed=1041):
    if not 0 < initial_steps <= max_steps or min(ntrain,ndev,ntest,batch) < 1:
        raise ValueError('positive sizes and 0 < initial_steps <= max_steps required')
    out = Path(out)
    out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    rows,groups,vocab,cat,data = make_inputs(arm,ntrain,ndev,ntest,data_seed)
    architecture = dict(width=48,layers=3,heads=4,max_length=256)
    torch.manual_seed(seed)
    initial_model = TinyLM(len(vocab),**architecture)
    initial = {key:value.detach().clone() for key,value in initial_model.state_dict().items()}
    schedule = sample_schedule(len(groups['train']),max_steps,batch,seed+100)
    config = dict(version='v0.4-onehop-objective-control',arm=arm,seed=seed,data_seed=data_seed,
                  sizes=dict(train=ntrain,dev=ndev,test=ntest),batch=batch,lr=.003,
                  initial_steps=initial_steps,max_steps=max_steps,gate=.95,architecture=architecture,
                  vocabulary=vocab,parameters=sum(p.numel() for p in initial_model.parameters()),
                  initial_state_sha256=state_hash(initial),schedule_sha256=tensor_hash(schedule),
                  schedule_seed=seed+100,rows_sha256=digest(rows),worlds_sha256=digest(data),
                  catalog_sha256=digest(cat),torch_version=str(torch.__version__),
                  source_sha256={Path(module.__file__).name:file_hash(module.__file__)
                                 for module in (graphs,model_module,native)},
                  control_source_sha256=file_hash(__file__),
                  declared_design=(seed==43 and data_seed==1041 and initial_steps==2000
                                   and max_steps==6000 and (ntrain,ndev,ntest,batch)==(800,160,160,64)),
                  scope='Exploratory reused-world calibration. Within-arm paired objectives; no novelty claim.')
    write_json(out/'config.json',config)
    write_json(out/'worlds.json',data)
    write_json(out/'catalog.json',cat)
    (out/'rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    torch.save(dict(state_dict=initial,config=config),out/'initial.pt')
    torch.save(schedule,out/'sample_schedule.pt')
    seq,lengths = tensors([r['prompt']+r['answer'] for r in groups['train']],vocab)
    prompts = torch.tensor([len(r['prompt']) for r in groups['train']])
    outcomes = {}
    # Each objective receives independent copies of the exact same weights and schedule.
    for objective in ('full','answer_only'):
        dest = out/objective
        dest.mkdir()
        model = TinyLM(len(vocab),**architecture)
        model.load_state_dict(initial)
        assert state_hash(model.state_dict()) == config['initial_state_sha256']
        optimizer = torch.optim.AdamW(model.parameters(),lr=.003)
        write_json(dest/'optimizer.json',optimizer.defaults)
        exposure = dict(records=0,input_tokens=0,full_targets=0,answer_targets=0,supervised_targets=0)
        checkpoints,logs = [],[]
        started = time.monotonic()
        for step,ix in enumerate(schedule,1):
            model.train()
            logits,_ = model(seq[ix,:-1],lengths[ix]-1)
            full,answer,counts = loss_terms(logits,seq[ix],prompts[ix],lengths[ix])
            loss = full if objective=='full' else answer
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            exposure['records'] += len(ix)
            exposure['input_tokens'] += int((lengths[ix]-1).sum())
            for key in ('full_targets','answer_targets'):
                exposure[key] += counts[key]
            exposure['supervised_targets'] += counts['full_targets' if objective=='full' else 'answer_targets']
            if step==1 or step%200==0 or step in (initial_steps,max_steps):
                log = dict(step=step,full_loss=float(full.detach()),answer_loss=float(answer.detach()),
                           elapsed_seconds=time.monotonic()-started,exposures=dict(exposure))
                logs.append(log)
                print(json.dumps(dict(arm=arm,objective=objective,**log)),flush=True)
            if step not in (initial_steps,max_steps):
                continue
            model.eval()
            dev,dev_outputs = diagnostics(model,groups['dev'],vocab,arm,cat)
            passed = dev['exact']['correct']/dev['exact']['n'] >= .95
            checkpoint = dest/f'checkpoint-{step}.pt'
            torch.save(dict(state_dict=model.state_dict(),optimizer_state_dict=optimizer.state_dict(),
                            config=config,objective=objective,step=step,catalog=cat),checkpoint)
            record = dict(step=step,development=dev,gate_pass=passed,exposures=dict(exposure),
                          elapsed_seconds=time.monotonic()-started,checkpoint_sha256=file_hash(checkpoint),
                          state_sha256=state_hash(model.state_dict()),
                          schedule_prefix_sha256=tensor_hash(schedule[:step]))
            checkpoints.append(record)
            write_json(dest/f'dev-generations-{step}.json',dev_outputs)
            # Durable decision record precedes all test inspection, including retrospective checkpoints.
            write_json(dest/'decisions.json',dict(checkpoints=checkpoints,logs=logs,
                       initial_state_sha256=config['initial_state_sha256']))
            print(json.dumps(dict(arm=arm,objective=objective,development=record)),flush=True)
            if passed or step==max_steps:
                break
        write_json(dest/'stopping.json',dict(step=step,gate_pass=passed,
                   reason='development gate' if passed else 'declared ceiling',
                   test_accessed=False))
        outcomes[objective] = dict(objective=objective,stopped_step=step,competence_gate_pass=passed,
                                   checkpoints=checkpoints,logs=logs,
                                   initial_state_sha256=config['initial_state_sha256'],
                                   schedule_sha256=config['schedule_sha256'],rows_sha256=config['rows_sha256'])
    # Both paired objectives have stopped durably before any retrospective evaluation.
    # This barrier prevents even the first objective's test results from preceding
    # the second objective's development-based stopping decision.
    for objective,result in outcomes.items():
        dest = out/objective
        for record in result['checkpoints']:
            checkpoint = dest/f"checkpoint-{record['step']}.pt"
            saved = torch.load(checkpoint,weights_only=True)
            model.load_state_dict(saved['state_dict'])
            model.eval()
            evaluations,outputs = {},{}
            for partition in ('train','dev','test'):
                evaluations[partition],outputs[partition] = diagnostics(model,groups[partition],vocab,arm,cat)
            record['evaluation'] = evaluations
            write_json(dest/f"generations-{record['step']}.json",outputs)
        write_json(dest/'metrics.json',result)
    common = sorted(set(r['step'] for r in outcomes['full']['checkpoints']) &
                    set(r['step'] for r in outcomes['answer_only']['checkpoints']))
    summary = dict(config=config,paired_checkpoint_steps=common,
                   stopped_steps={k:v['stopped_step'] for k,v in outcomes.items()},
                   gate_pass={k:v['competence_gate_pass'] for k,v in outcomes.items()},
                   comparison='Use common checkpoint steps only for paired exposure comparisons; '
                              'unequal stopped endpoints are not compute matched.')
    write_json(out/'summary.json',summary)
    files = {str(p.relative_to(out)):dict(sha256=file_hash(p),bytes=p.stat().st_size)
             for p in out.rglob('*') if p.is_file()}
    write_json(out/'artifact-manifest.json',files)
    return summary


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    parser.add_argument('--arms',nargs='+',choices=['text','atomic'],default=['text','atomic'])
    parser.add_argument('--seed',type=int,default=43)
    parser.add_argument('--data-seed',type=int,default=1041)
    parser.add_argument('--initial-steps',type=int,default=2000)
    parser.add_argument('--max-steps',type=int,default=6000)
    parser.add_argument('--ntrain',type=int,default=800)
    parser.add_argument('--ndev',type=int,default=160)
    parser.add_argument('--ntest',type=int,default=160)
    parser.add_argument('--batch',type=int,default=64)
    args = vars(parser.parse_args())
    arms,root = args.pop('arms'),Path(args.pop('out'))
    if len(set(arms)) != len(arms):
        parser.error('duplicate arms are not allowed')
    for arm in arms:
        run(root/arm,arm,**args)
