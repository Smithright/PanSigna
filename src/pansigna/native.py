"""Train and freely generate native PanSigna responses from pipeline artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import time
import torch
from .codec import encode, decode
from .model import TinyLM, fit_subspace
from .pipeline import read_encoding, digest
from .world import ENTITIES, ACTIONS, FIELDS

def load_corpus(root):
    root = Path(root)
    manifest = json.loads((root/"manifest.json").read_text())
    for name, expected in manifest["files"].items():
        if Path(name).name != name:
            raise ValueError("invalid corpus filename")
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError("corpus hash mismatch: " + name)
    rows = [json.loads(line) for line in (root/"encoded.jsonl").read_text().splitlines()]
    cat = json.loads((root/"catalog.json").read_text())
    if digest(cat) != manifest["catalog_sha256"]:
        raise ValueError("catalog hash mismatch")
    for row in rows:
        if read_encoding(row["bits"], cat) != row["frame"] or row["catalog_sha256"] != digest(cat):
            raise ValueError("encoding-assignment mismatch")
    return rows, cat, manifest

def examples(rows, arm, cat):
    ids = {e["key"]:e["bits"] for e in cat}
    result = []
    for row in rows:
        frame = read_encoding(row["bits"], cat)
        for field in FIELDS:
            if arm == "text":
                prompt = re.findall(r"\w+|[^\w\s]", row["raw_text"].lower()) + ["query", field]
                answer = [frame[field]]
            else:
                stream = row["bits"] + "00000000" + encode([ids["query"],ids[field]])
                prompt = list(stream) if arm == "bits" else ["ps:"+b for b in decode(stream)]
                answer = list(ids[frame[field]]) if arm == "bits" else ["ps:"+ids[frame[field]]]
            result.append({"id":row["id"]+":"+field,"partition":row["partition"],"frame":frame,"field":field,
                           "prompt":["<bos>"]+prompt+["<answer>"],"answer":answer+["<eos>"],"raw":row["raw_text"]})
    return result

def alphabet(rows, cat):
    words = {"<pad>","<bos>","<answer>","<eos>"}
    for arm in ("text","atomic","bits"):
        for e in examples(rows, arm, cat):
            words.update(e["prompt"]+e["answer"])
    return {w:i for i,w in enumerate(["<pad>"]+sorted(words-{"<pad>"}))}

def tensors(sequences, vocab):
    lengths = torch.tensor([len(s) for s in sequences])
    x = torch.zeros(len(sequences),int(lengths.max()),dtype=torch.long)
    for i,s in enumerate(sequences):
        x[i,:len(s)] = torch.tensor([vocab[w] for w in s])
    return x, lengths

def parse_response(tokens, arm, cat):
    inverse = {e["bits"]:e["key"] for e in cat}
    if arm == "text":
        return tokens[0] if len(tokens)==1 and tokens[0] in (*ENTITIES,*ACTIONS) else None
    try:
        bits = decode("".join(tokens)) if arm=="bits" else [t.removeprefix("ps:") for t in tokens if t.startswith("ps:")]
        if arm=="atomic" and len(bits)!=len(tokens):
            return None
        if len(bits)!=1:
            return None
        return inverse.get(bits[0])
    except ValueError:
        return None

@torch.no_grad()
def states(model, rows, vocab, layer):
    x, lengths = tensors([e["prompt"] for e in rows],vocab)
    _, h = model(x,lengths,capture_layer=layer)
    return h[torch.arange(len(x)),lengths-1]

@torch.no_grad()
def generate(model, rows, vocab, max_new=16, intervention=None):
    sequences = [list(e["prompt"]) for e in rows]
    outputs = [[] for _ in rows]
    done = [False]*len(rows)
    inverse = {i:w for w,i in vocab.items()}
    for _ in range(max_new):
        x,lengths = tensors(sequences,vocab)
        logits,_ = model(x,lengths,intervention=intervention)
        predictions = logits[torch.arange(len(rows)),lengths-1].argmax(-1).tolist()
        for i,p in enumerate(predictions):
            if done[i]:
                continue
            token = inverse[p]
            if token=="<eos>":
                done[i]=True
            else:
                outputs[i].append(token)
                sequences[i].append(token)
        if all(done):
            break
    return outputs,done

def donors(rows):
    result=[]
    for i,base in enumerate(rows):
        choices=[r for r in rows if r["field"]==base["field"] and all(r["frame"][f]!=base["frame"][f] for f in FIELDS)]
        if not choices:
            raise ValueError("no donor")
        result.append(choices[i%len(choices)])
    return result

def measure(model, rows, vocab, arm, cat, layer=None, basis=None):
    intervention=None
    donor_rows=donors(rows)
    if basis is not None:
        donor_h=states(model,donor_rows,vocab,layer)
        positions=torch.tensor([len(e["prompt"])-1 for e in rows])
        intervention=(layer,donor_h,basis,positions)
    outputs,stopped=generate(model,rows,vocab,intervention=intervention)
    decoded=[parse_response(o,arm,cat) if end else None for o,end in zip(outputs,stopped)]
    correct=[value==row["frame"][row["field"]] for value,row in zip(decoded,rows)]
    recipient=[value==donor["frame"]["recipient"] for value,row,donor in zip(decoded,rows,donor_rows) if row["field"]=="recipient"]
    locality=[ok for ok,row in zip(correct,rows) if row["field"]!="recipient"]
    metrics={"n":len(rows),"terminated":sum(stopped),"catalog_legible":sum(v is not None for v in decoded),
             "semantic_correct":sum(correct),"recipient_swap_successes":sum(recipient),"recipient_n":len(recipient),
             "other_fields_correct":sum(locality),"other_fields_n":len(locality)}
    samples=[{"id":row["id"],"raw":row["raw"],"field":row["field"],"expected":row["frame"][row["field"]],
              "generated":o,"terminated":end,"decoded":value,"correct":ok} for row,o,end,value,ok in zip(rows,outputs,stopped,decoded,correct)]
    return metrics,samples

def run(corpus,arm,seed,steps,out):
    destination=Path(out)
    destination.mkdir(parents=True,exist_ok=False)
    raw,cat,corpus_manifest=load_corpus(corpus)
    all_rows=examples(raw,arm,cat)
    groups={p:[e for e in all_rows if e["partition"]==p] for p in ("train","dev","test")}
    vocab=alphabet(raw,cat)
    torch.set_num_threads(2)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    model=TinyLM(len(vocab))
    optimizer=torch.optim.AdamW(model.parameters(),lr=.003)
    rng=torch.Generator().manual_seed(seed+100)
    full,lengths=tensors([e["prompt"]+e["answer"] for e in groups["train"]],vocab)
    started=time.time()
    losses=[]
    token_count=0
    for step in range(steps):
        idx=torch.randint(len(full),(64,),generator=rng)
        tokens=full[idx,:-1]
        token_count+=int((lengths[idx]-1).sum())
        logits,_=model(tokens,lengths[idx]-1)
        loss=torch.nn.functional.cross_entropy(logits.reshape(-1,len(vocab)),full[idx,1:].reshape(-1),ignore_index=0)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if step==0 or (step+1)%200==0:
            losses.append({"step":step+1,"loss":loss.item()})
    train_seconds=time.time()-started
    model.eval()
    labels=torch.tensor([ENTITIES.index(r["frame"]["recipient"]) for r in groups["train"]])
    candidates=[]
    for layer in range(2):
        h=states(model,groups["train"],vocab,layer)
        q=fit_subspace(h,labels,len(ENTITIES))
        metrics,_=measure(model,groups["dev"],vocab,arm,cat,layer,q)
        score=(metrics["recipient_swap_successes"]/metrics["recipient_n"]+metrics["other_fields_correct"]/metrics["other_fields_n"])/2
        candidates.append((score,layer,q,metrics))
    _,layer,q,_=max(candidates,key=lambda c:(c[0],-c[1]))
    train_h=states(model,groups["train"],vocab,layer)
    test_h=states(model,groups["test"],vocab,layer)
    mean=train_h.mean(0)
    x=torch.cat([train_h-mean,torch.ones(len(train_h),1)],1).double()
    targets=torch.nn.functional.one_hot(labels,len(ENTITIES)).double()
    w=torch.linalg.solve(x.T@x+.01*torch.eye(x.shape[1]),x.T@targets)
    tx=torch.cat([test_h-mean,torch.ones(len(test_h),1)],1).double()
    truth=torch.tensor([ENTITIES.index(r["frame"]["recipient"]) for r in groups["test"]])
    probe=float(((tx@w).argmax(-1)==truth).float().mean())
    rng=torch.Generator().manual_seed(seed+200)
    random_q=torch.linalg.qr(torch.randn(q.shape,generator=rng)).Q
    shuffled_q=fit_subspace(train_h,labels[torch.randperm(len(labels),generator=rng)],len(ENTITIES))
    metrics,samples=measure(model,groups["test"],vocab,arm,cat)
    tests={"none":metrics}
    for name,basis in (("learned",q),("random",random_q),("shuffled_labels",shuffled_q)):
        tests[name],_=measure(model,groups["test"],vocab,arm,cat,layer,basis)
    source_files=[Path(__file__),Path(__file__).with_name("pipeline.py"),Path(__file__).with_name("model.py"),Path(__file__).with_name("codec.py")]
    source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    result={"status":"exploratory_controlled_corpus_only","arm":arm,"seed":seed,"steps":steps,"batch_size":64,
            "training_objective":"full_next_token_native_response","training_input_tokens":token_count,
            "parameters":sum(p.numel() for p in model.parameters()),"training_seconds":train_seconds,"total_seconds":time.time()-started,
            "selected_layer":layer,"recipient_probe_accuracy":probe,"test":tests,"losses":losses,
            "dev_candidates":[{"layer":l,"score":s,"metrics":m} for s,l,_,m in candidates],
            "corpus_manifest":corpus_manifest,"source_hashes":source_hashes,"vocab":vocab,"catalog":cat,
            "torch":str(torch.__version__),"python":platform.python_version(),"platform":platform.platform(),
            "intervention":"patch fixed prompt readout position on every greedy generation step"}
    torch.save({"state_dict":model.state_dict(),"basis":q,"probe_weights":w,"probe_mean":mean,"manifest":result},destination/"checkpoint.pt")
    (destination/"metrics.json").write_text(json.dumps(result,indent=2)+"\n")
    (destination/"responses.json").write_text(json.dumps(samples,indent=2)+"\n")
    print(json.dumps({"arm":arm,"seed":seed,"test":metrics,"probe":probe,"seconds":result["total_seconds"]}),flush=True)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--corpus",required=True)
    p.add_argument("--arms",nargs="+",choices=("text","atomic","bits"),default=["text","atomic","bits"])
    p.add_argument("--seeds",nargs="+",type=int,default=[3,11,29])
    p.add_argument("--steps",type=int,default=1200)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    targets=[Path(a.out)/f"{arm}-seed{seed}" for arm in a.arms for seed in a.seeds]
    if a.steps<1 or len(set(targets))!=len(targets) or any(t.exists() for t in targets):
        p.error("positive steps and fresh unique run destinations required")
    for arm in a.arms:
        for seed in a.seeds:
            run(a.corpus,arm,seed,a.steps,Path(a.out)/f"{arm}-seed{seed}")

if __name__=="__main__":
    main()
