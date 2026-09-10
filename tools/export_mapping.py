"""Export readable decoder coefficients; these are NOT proven causal channels."""
import argparse
import csv
import json
from pathlib import Path
import torch
from pansigna.world import ENTITIES

parser = argparse.ArgumentParser()
parser.add_argument("run", type=Path)
parser.add_argument("--out", required=True, type=Path)
args = parser.parse_args()
with torch.serialization.safe_globals([torch.torch_version.TorchVersion]):
    checkpoint = torch.load(args.run/"checkpoint.pt", map_location="cpu", weights_only=True)
args.out.mkdir(parents=True, exist_ok=False)
weights = checkpoint["probe_weights"]
with (args.out/"recipient-decoder.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["hidden_coordinate_or_intercept", *ENTITIES])
    for i, row in enumerate(weights.tolist()):
        writer.writerow([i if i < len(weights)-1 else "intercept", *row])
with (args.out/"patch-basis.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["hidden_coordinate", *range(checkpoint["basis"].shape[1])])
    for i, row in enumerate(checkpoint["basis"].tolist()):
        writer.writerow([i, *row])
(args.out/"interpretation.json").write_text(json.dumps({
    "warning": "Decoder coefficients indicate recoverability, not causal control or addressable model weights.",
    "centering_mean": checkpoint["probe_mean"].tolist(),
    "layer": checkpoint["manifest"]["selected_layer"],
    "registry": checkpoint["manifest"].get("registry", {e["key"]:e["bits"] for e in checkpoint["manifest"].get("catalog", [])}),
    "source_sha256": checkpoint["manifest"].get("source_sha256", checkpoint["manifest"].get("source_hashes")),
}, indent=2)+"\n")
