"""Offline synthetic pilot. No external models, credentials or service calls."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import time
import torch
from .model import TinyLM, fit_subspace
from .world import ARMS, ENTITIES, ACTIONS, records, registry

def vocabulary():
    # Known finite experimental alphabet; no frequencies/labels learned from test.
    tokens = {"<pad>", *ENTITIES, *ACTIONS}
    for arm in ARMS:
        for partition in ("train", "dev", "test"):
            for _, _, _, seq in records(arm, partition):
                tokens.update(seq)
    return {t: i for i, t in enumerate(["<pad>"] + sorted(tokens - {"<pad>"}))}

def batch(rows, vocab):
    lengths = torch.tensor([len(r[3]) for r in rows])
    x = torch.zeros(len(rows), int(lengths.max()), dtype=torch.long)
    for i, row in enumerate(rows):
        x[i, :lengths[i]] = torch.tensor([vocab[t] for t in row[3]])
    y = torch.tensor([vocab[getattr(s, field)] for s, _, field, _ in rows])
    return x, lengths, y

@torch.no_grad()
def inspect(model, rows, vocab, layer):
    x, lengths, y = batch(rows, vocab)
    logits, hidden = model(x, lengths, capture_layer=layer)
    idx = torch.arange(len(rows))
    return logits[idx, lengths-1].argmax(-1), hidden[idx, lengths-1], y

def donors_for(rows):
    donors = []
    for i, (s, variant, field, _) in enumerate(rows):
        candidates = [r for r in rows if r[2] == field and r[1] == variant
                      and r[0].recipient != s.recipient and r[0].actor != s.actor
                      and r[0].action != s.action]
        if not candidates:
            raise ValueError("no valid donor")
        donors.append(candidates[i % len(candidates)])
    return donors

def rate(values):
    n = len(values)
    return {"successes": sum(values), "n": n, "rate": sum(values)/n if n else None}

@torch.no_grad()
def evaluate(model, rows, vocab, layer, basis):
    donors = donors_for(rows)
    base_pred, _, y = inspect(model, rows, vocab, layer)
    donor_pred, donor_h, donor_y = inspect(model, donors, vocab, layer)
    x, lengths, _ = batch(rows, vocab)
    logits, _ = model(x, lengths, intervention=(layer, donor_h, basis))
    patched = logits[torch.arange(len(rows)), lengths-1].argmax(-1)
    effect, locality, eligible_effect, eligible_locality = [], [], [], []
    for i, (s, _, field, _) in enumerate(rows):
        expected = vocab[donors[i][0].recipient] if field == "recipient" else y[i].item()
        success = patched[i].item() == expected
        target = effect if field == "recipient" else locality
        target.append(success)
        if base_pred[i] == y[i] and donor_pred[i] == donor_y[i]:
            (eligible_effect if field == "recipient" else eligible_locality).append(success)
    return {"baseline_accuracy": float((base_pred == y).float().mean()),
            "recipient_counterfactual": rate(effect), "other_fields_correct": rate(locality),
            "eligible_recipient_counterfactual": rate(eligible_effect),
            "eligible_other_fields_correct": rate(eligible_locality)}

def source_digest():
    files = sorted(Path(__file__).parent.glob("*.py"))
    return hashlib.sha256(b"".join(p.name.encode()+p.read_bytes() for p in files)).hexdigest()

def run(arm, seed, steps, out, objective="corpus"):
    started = time.time()
    torch.manual_seed(seed)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    vocab = vocabulary()
    data = {part: records(arm, part) for part in ("train", "dev", "test")}
    model = TinyLM(len(vocab))
    opt = torch.optim.AdamW(model.parameters(), lr=0.003)
    generator = torch.Generator().manual_seed(seed + 100)
    x, lengths, y = batch(data["train"], vocab)
    full = torch.zeros(len(x), x.shape[1]+1, dtype=torch.long)
    full[:, :x.shape[1]] = x
    full[torch.arange(len(x)), lengths] = y
    losses = []
    input_tokens = 0
    for step in range(steps):
        idx = torch.randint(len(x), (64,), generator=generator)
        input_tokens += int(lengths[idx].sum())
        if objective == "corpus":
            logits, _ = model(full[idx, :-1], lengths[idx])
            loss = torch.nn.functional.cross_entropy(logits.reshape(-1, len(vocab)), full[idx, 1:].reshape(-1), ignore_index=0)
        else:
            logits, _ = model(x[idx], lengths[idx])
            loss = torch.nn.functional.cross_entropy(logits[torch.arange(len(idx)), lengths[idx]-1], y[idx])
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step == 0 or (step+1) % 100 == 0:
            losses.append({"step": step+1, "loss": loss.item()})
    model.eval()
    labels = torch.tensor([ENTITIES.index(r[0].recipient) for r in data["train"]])
    candidates = []
    for layer in range(len(model.blocks)):
        _, h, _ = inspect(model, data["train"], vocab, layer)
        basis = fit_subspace(h, labels, len(ENTITIES))
        metrics = evaluate(model, data["dev"], vocab, layer, basis)
        score = (metrics["recipient_counterfactual"]["rate"] + metrics["other_fields_correct"]["rate"])/2
        candidates.append((score, layer, basis, metrics))
    _, layer, basis, dev = max(candidates, key=lambda c: (c[0], -c[1]))
    _, train_h, _ = inspect(model, data["train"], vocab, layer)
    control_rng = torch.Generator().manual_seed(seed + 200)
    random_basis = torch.linalg.qr(torch.randn(basis.shape, generator=control_rng)).Q
    shuffled = fit_subspace(train_h, labels[torch.randperm(len(labels), generator=control_rng)], len(ENTITIES))
    identity = torch.zeros(basis.shape[0], 0)
    test = {name: evaluate(model, data["test"], vocab, layer, q)
            for name, q in [("learned", basis), ("random", random_basis), ("shuffled_labels", shuffled), ("no_patch", identity)]}
    # Positive control at final layer: copying all state must copy donor decisions.
    test["full_final_state"] = evaluate(model, data["test"], vocab, len(model.blocks)-1, torch.eye(basis.shape[0]))
    # Diagnostic decoder is trained only on train, with a fixed ridge coefficient.
    _, test_h, _ = inspect(model, data["test"], vocab, layer)
    mean = train_h.mean(0)
    features = torch.cat((train_h - mean, torch.ones(len(train_h), 1)), 1).double()
    target = torch.nn.functional.one_hot(labels, len(ENTITIES)).double()
    weights = torch.linalg.solve(features.T@features + .01*torch.eye(features.shape[1]), features.T@target)
    test_features = torch.cat((test_h-mean, torch.ones(len(test_h), 1)), 1).double()
    test_labels = torch.tensor([ENTITIES.index(r[0].recipient) for r in data["test"]])
    probe_accuracy = float(((test_features@weights).argmax(-1) == test_labels).float().mean())
    manifest = {"status": "exploratory_synthetic_pilot_not_hypothesis_confirmation",
        "arm": arm, "seed": seed, "steps": steps, "batch_size": 64,
        "training_objective": objective, "device": "cpu",
        "parameters": sum(p.numel() for p in model.parameters()), "width": 48, "layers": 2,
        "exposures": steps*64, "padded_training_length": x.shape[1],
        "training_input_tokens": input_tokens,
        "token_count_note": "actual sampled nonpadding input tokens",
        "selected_layer": layer, "subspace_rank": basis.shape[1], "dev": dev,
        "dev_candidates": [{"layer":l, "score":score, "metrics":metrics} for score,l,_,metrics in candidates],
        "test": test, "recipient_probe_accuracy": probe_accuracy, "losses": losses,
        "split_counts": {p:len(rows) for p,rows in data.items()},
        "dataset_sha256": hashlib.sha256(repr(data).encode()).hexdigest(),
        "source_sha256": source_digest(), "torch": torch.__version__, "python": platform.python_version(),
        "platform": platform.platform(), "seconds": time.time()-started,
        "registry": registry(arm == "permuted"), "vocabulary": vocab}
    destination = Path(out)/f"{arm}-seed{seed}"
    destination.mkdir(parents=True, exist_ok=False)
    torch.save({"state_dict": model.state_dict(), "basis": basis, "probe_weights": weights,
                "probe_mean": mean, "manifest": manifest}, destination/"checkpoint.pt")
    (destination/"metrics.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"arm":arm,"seed":seed,"baseline":test["learned"]["baseline_accuracy"],
                      "recipient":test["learned"]["recipient_counterfactual"]["rate"],
                      "locality":test["learned"]["other_fields_correct"]["rate"],"seconds":manifest["seconds"]}), flush=True)
    return manifest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arms", nargs="+", choices=ARMS, default=list(ARMS[:4]))
    parser.add_argument("--seeds", nargs="+", type=int, default=[0,1,2])
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--objective", choices=("corpus", "answers"), default="corpus")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.steps < 1:
        parser.error("steps must be positive")
    targets = [Path(args.out)/f"{arm}-seed{seed}" for arm in args.arms for seed in args.seeds]
    if len(set(targets)) != len(targets) or any(p.exists() for p in targets):
        parser.error("duplicate or existing run destination; choose a new output directory")
    for arm in args.arms:
        for seed in args.seeds:
            run(arm, seed, args.steps, args.out, args.objective)

if __name__ == "__main__":
    main()
