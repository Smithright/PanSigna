import json
import torch
from pansigna.experiment import batch, vocabulary, donors_for, run
from pansigna.world import records, split

def test_donors_stay_in_partition_and_change_nuisance_factors():
    for partition in ("train", "dev", "test"):
        rows = records("nl", partition)
        for base, donor in zip(rows, donors_for(rows)):
            assert split(donor[0]) == partition
            assert base[1:3] == donor[1:3]
            assert all(getattr(base[0], f) != getattr(donor[0], f) for f in ("actor", "action", "recipient"))

def test_padding_does_not_change_predictions():
    from pansigna.model import TinyLM
    vocab = vocabulary()
    rows = records("nl", "train")
    short = min(rows, key=lambda r: len(r[3]))
    long = max(rows, key=lambda r: len(r[3]))
    model = TinyLM(len(vocab), width=16, heads=2).eval()
    with torch.no_grad():
        a, la, _ = batch([short], vocab)
        b, lb, _ = batch([short, long], vocab)
        pa, _ = model(a, la)
        pb, _ = model(b, lb)
        assert torch.allclose(pa[0, la[0]-1], pb[0, lb[0]-1], atol=1e-5)

def test_end_to_end_training_saves_auditable_results(tmp_path):
    result = run("ps", 7, 2, tmp_path)
    assert result["training_input_tokens"] == 2*64*8
    assert result["split_counts"] == {"train":864, "dev":144, "test":144}
    assert set(result["test"]) == {"learned", "random", "shuffled_labels", "no_patch", "full_final_state"}
    assert result["test"]["no_patch"]["eligible_recipient_counterfactual"]["successes"] == 0
    assert json.loads((tmp_path/"ps-seed7"/"metrics.json").read_text())["seed"] == 7
    assert (tmp_path/"ps-seed7"/"checkpoint.pt").exists()
    from pansigna.model import TinyLM
    from pansigna.experiment import inspect
    with torch.serialization.safe_globals([torch.torch_version.TorchVersion]):
        checkpoint = torch.load(tmp_path/"ps-seed7"/"checkpoint.pt", weights_only=True)
    model = TinyLM(len(result["vocabulary"])).eval()
    model.load_state_dict(checkpoint["state_dict"])
    pred, _, y = inspect(model, records("ps", "test"), result["vocabulary"], result["selected_layer"])
    assert float((pred == y).float().mean()) == result["test"]["learned"]["baseline_accuracy"]
