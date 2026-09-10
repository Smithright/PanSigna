"""Read back graph checkpoints; diagnose training competence without further fitting."""
import argparse
import hashlib
import json
from pathlib import Path
import torch
from pansigna.graphs import evaluate
from pansigna.model import TinyLM


def check(path):
    path=Path(path)
    out=path/'checkpoint-readback.json'
    if out.exists():
        raise ValueError('checkpoint readback already exists')
    checkpoint=torch.load(path/'model.pt',map_location='cpu',weights_only=True)
    config=checkpoint['config']
    torch.set_num_threads(2)
    model=TinyLM(len(config['vocab']),width=config['width'],layers=config['layers'],heads=config['heads']).eval()
    model.load_state_dict(checkpoint['state_dict'])
    rows=[json.loads(line) for line in (path/'rows.jsonl').read_text().splitlines()]
    test=[r for r in rows if r['partition']=='test' and r['variant'] in (0,1)]
    metrics,samples=evaluate(model,test,config['vocab'],config['arm'],checkpoint['catalog'])
    assert metrics==json.loads((path/'metrics.json').read_text())['test']
    assert samples==json.loads((path/'generations.json').read_text())['test']
    train,_=evaluate(model,[r for r in rows if r['partition']=='train'],config['vocab'],config['arm'],checkpoint['catalog'])
    result=dict(test_metrics_and_generations_match=True,test_n=len(test),train=train,
                interpretation='Post-hoc training competence diagnosis only; no parameter changes or model selection.',
                model_sha256=hashlib.sha256((path/'model.pt').read_bytes()).hexdigest(),
                rows_sha256=hashlib.sha256((path/'rows.jsonl').read_bytes()).hexdigest())
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(path=str(path),**result)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('paths',nargs='+')
    args=parser.parse_args()
    for path in args.paths:
        check(path)
