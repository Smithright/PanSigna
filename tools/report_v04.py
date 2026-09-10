"""Validate paired-run artifacts, reload final checkpoints, and report v0.4."""
import argparse
import json
from pathlib import Path

import torch

from pansigna.learning_controls import file_hash, state_hash, diagnostics
from pansigna.model import TinyLM


def build(root, out):
    root, out = Path(root), Path(out)
    if out.exists():
        raise FileExistsError(out)
    torch.set_num_threads(2)
    results, receipts = {}, {}
    for arm in ('text', 'atomic'):
        base = root/arm
        manifest = json.loads((base/'artifact-manifest.json').read_text())
        for name, expected in manifest.items():
            path = base/name
            assert file_hash(path) == expected['sha256'], path
            assert path.stat().st_size == expected['bytes'], path
        summary = json.loads((base/'summary.json').read_text())
        config = summary['config']
        assert config['declared_design'] is True
        rows = [json.loads(line) for line in (base/'rows.jsonl').read_text().splitlines()]
        test = [r for r in rows if r['partition'] == 'test']
        cat = json.loads((base/'catalog.json').read_text())
        metrics = {o:json.loads((base/o/'metrics.json').read_text())
                   for o in ('full','answer_only')}
        for key in ('initial_state_sha256','schedule_sha256','rows_sha256'):
            assert metrics['full'][key] == metrics['answer_only'][key] == config[key]
        for step in summary['paired_checkpoint_steps']:
            paired = [next(c for c in m['checkpoints'] if c['step']==step) for m in metrics.values()]
            for key in ('records','input_tokens','full_targets','answer_targets'):
                assert paired[0]['exposures'][key] == paired[1]['exposures'][key]
            assert paired[0]['schedule_prefix_sha256'] == paired[1]['schedule_prefix_sha256']
        for objective, result in metrics.items():
            final = result['checkpoints'][-1]
            checkpoint = base/objective/f"checkpoint-{final['step']}.pt"
            saved = torch.load(checkpoint, weights_only=True)
            model = TinyLM(len(config['vocabulary']), **config['architecture'])
            model.load_state_dict(saved['state_dict'])
            model.eval()
            assert state_hash(model.state_dict()) == final['state_sha256']
            measured, generations = diagnostics(model,test,config['vocabulary'],arm,cat)
            recorded = json.loads((base/objective/f"generations-{final['step']}.json").read_text())['test']
            assert generations == recorded
            for key in ('exact','legible','terminated'):
                assert measured[key] == final['evaluation']['test'][key]
            receipts[f'{arm}/{objective}'] = dict(step=final['step'],
                checkpoint_sha256=file_hash(checkpoint),state_sha256=final['state_sha256'],
                reproduced_test_generations=len(generations),exact=measured['exact'])
        results[arm] = dict(summary=summary,metrics=metrics,
                           manifest_sha256=file_hash(base/'artifact-manifest.json'))
    out.mkdir(parents=True)
    (out/'summary.json').write_text(json.dumps(dict(results=results,readbacks=receipts),indent=2)+'\n')
    lines = ['# PanSigna v0.4: paired one-hop objective control', '',
        'Exploratory calibration on reused synthetic graph worlds, seed 43. The protocol',
        'and implementation were committed at `5a09b70` before the declared run.',
        'This isolates the objective within each representation; it does not replicate',
        'all v0.3 conditions or establish a PanSigna-specific advantage.', '',
        '## Measured checkpoints', '',
        '| Representation | Objective | Steps | Train exact | Dev exact | Test exact | Dev gate |',
        '|---|---|---:|---:|---:|---:|---|']
    def score(value):
        return f"{value['correct']}/{value['n']} ({100*value['correct']/value['n']:.1f}%)"
    for arm, bundle in results.items():
        for objective, result in bundle['metrics'].items():
            for c in result['checkpoints']:
                ev=c['evaluation']
                lines.append('| '+' | '.join([arm,objective,str(c['step']),
                    *[score(ev[p]['exact']) for p in ('train','dev','test')],
                    'pass' if c['gate_pass'] else 'fail'])+' |')
    if not any(v for b in results.values() for v in b['summary']['gate_pass'].values()):
        lines += ['', '**Outcome:** all four models failed development competence. Both',
            'answer-only models fit all 1600 training records at the final checkpoint,',
            'while held-out accuracy remained near the eight-choice chance reference.',
            'Answer-only supervision improves fitting here but is insufficient for',
            'generalization. No intermediate causal mapping was evaluated on these',
            'unqualified models. This is a negative result for this recipe, not a',
            'general impossibility result for PanSigna or causal training.', '']
    lines += ['', '## What was controlled', '',
        'Within each representation the objectives received identical initial parameters,',
        'rows, vocabulary, optimizer defaults and precomputed sample schedules. Common',
        'checkpoints have identical record/input-token exposures. Full loss supervises',
        'all nonpadding next tokens; answer-only supervises the answer and EOS.',
        'Both stopping decisions were recorded before test evaluation for either member',
        'of each pair. The 95% development gate selected stopping at 2000 or 6000 steps.', '',
        '| Representation | Common comparison steps | Full stopped | Answer-only stopped |',
        '|---|---|---:|---:|']
    for arm,bundle in results.items():
        s=bundle['summary']
        lines.append(f"| {arm} | {s['paired_checkpoint_steps']} | {s['stopped_steps']['full']} | {s['stopped_steps']['answer_only']} |")
    lines += ['', 'Unequal stopping endpoints are not compute matched. Cross-representation',
        'comparisons also differ in sequence lengths, vocabulary, parameter counts and',
        'canonicalization. Full and answer losses are recorded for both objectives in',
        '`summary.json`; full-sequence losses across tokenizations are not comparable',
        'perplexities. Each template shares its underlying graph, and atomic templates',
        'collapse to the same input. Counts are descriptive, not independent trials.', '',
        '## Claim boundary and reproduction', '',
        'Passing one-hop retrieval qualifies only that task for this calibration run.',
        'It does not establish two-hop reasoning, real-language word-sense annotation,',
        'causally legible intermediates or safe parameter editing. Failure blocks those',
        'downstream claims for the affected model. New seeds and fresh worlds belong',
        'in a separately declared confirmation, not a rescue selected by these tests.', '',
        'All manifest file hashes/sizes matched. Reloading each of the four final',
        'checkpoints reproduced its 320 held-out greedy generations and exact counts.',
        'The paired initialization, rows, full schedule and common exposure hashes',
        'were checked. These are local reproducibility checks, not external replication.', '',
        '```sh',
        '.venv/bin/python -m pansigna.learning_controls --out runs/v04-onehop',
        '.venv/bin/python tools/report_v04.py --runs runs/v04-onehop --out docs/results-v04',
        '```', '',
        'Use fresh output directories. The archive includes model checkpoints, optimizer',
        'states, data, schedules, catalog, every checkpoint generation and diagnostics.', '']
    (out/'report.md').write_text('\n'.join(lines))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--runs',required=True)
    p.add_argument('--out',required=True)
    args=p.parse_args()
    build(args.runs,args.out)
