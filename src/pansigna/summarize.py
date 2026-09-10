"""Descriptive seed-level summaries; no claims of statistical significance."""
import argparse
import json
from pathlib import Path
from statistics import mean

def summarize(root):
    results = [json.loads(p.read_text()) for p in sorted(Path(root).glob("*/metrics.json"))]
    if not results:
        raise ValueError("no metrics found")
    signatures = {(r["source_sha256"], r["steps"], r["training_objective"], r["parameters"]) for r in results}
    if len(signatures) != 1:
        raise ValueError("mixed protocols: summarize each configuration separately")
    lines = ["# Pilot results", "", "Exploratory finite-world results; not a confirmatory hypothesis test.", "",
             "| Arm | Seed | Task accuracy | Recipient probe | Learned swap | Actor/action correct | Random swap | Shuffled swap | Full-state swap |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in results:
        t = r["test"]
        values = [t["learned"]["baseline_accuracy"], r["recipient_probe_accuracy"],
                  t["learned"]["recipient_counterfactual"]["rate"], t["learned"]["other_fields_correct"]["rate"],
                  t["random"]["recipient_counterfactual"]["rate"], t["shuffled_labels"]["recipient_counterfactual"]["rate"],
                  t.get("full_final_state", {}).get("recipient_counterfactual", {}).get("rate")]
        lines.append(f"| {r['arm']} | {r['seed']} | " + " | ".join("not measured" if v is None else f"{v:.3f}" for v in values) + " |")
    indexed = {(r["arm"], r["seed"]): r for r in results}
    lines += ["", "## Paired seed differences", "", "Descriptive only; no confidence interval or significance claim.", ""]
    for comparator in ("nl", "sense", "permuted"):
        deltas = []
        for (arm, seed), ps in indexed.items():
            if arm == "ps" and (comparator, seed) in indexed:
                other = indexed[comparator, seed]
                deltas.append(ps["test"]["learned"]["recipient_counterfactual"]["rate"] - other["test"]["learned"]["recipient_counterfactual"]["rate"])
        if deltas:
            lines.append(f"- ps minus {comparator}: {deltas}; mean {mean(deltas):.3f}")
    lines += ["", "Raw JSON records include conditional metrics and denominators, hashes, selected layers and resource counts.",
              "Task accuracy and linear decodability do not establish causal selectivity or safe weight editing.", ""]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    text = summarize(args.root)
    with Path(args.out).open("x") as f:
        f.write(text)

if __name__ == "__main__":
    main()
