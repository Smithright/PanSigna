import torch
from pansigna.model import TinyLM, patch_subspace, fit_subspace

def test_patch_identity_and_orthogonal_locality():
    base = torch.tensor([[1., 2., 3.]])
    donor = torch.tensor([[4., 5., 6.]])
    basis = torch.tensor([[1.], [0.], [0.]])
    assert torch.equal(patch_subspace(base, base, basis), base)
    assert torch.equal(patch_subspace(base, donor, basis), torch.tensor([[4., 2., 3.]]))

def test_subspace_recovers_known_signal():
    x = torch.tensor([[1.,0.,1.], [-1.,0.,1.], [1.,0.,-1.], [-1.,0.,-1.]])
    q = fit_subspace(x, torch.tensor([0,1,0,1]), classes=2)
    assert q.shape == (3,1)
    assert torch.allclose(q @ q.T, torch.diag(torch.tensor([1.,0.,0.])), atol=1e-5)

def test_causal_mask_and_identity_patch():
    torch.manual_seed(3)
    model = TinyLM(20, width=16, layers=2, heads=2).eval()
    x = torch.tensor([[1,2,3,4]])
    y = torch.tensor([[1,2,9,8]])
    with torch.no_grad():
        logits, h = model(x, capture_layer=0)
        other, _ = model(y)
        assert torch.allclose(logits[:,:2], other[:,:2], atol=1e-6)
        patched, _ = model(x, intervention=(0, h[:,-1], torch.eye(16)))
        assert torch.allclose(logits, patched, atol=1e-6)

def test_full_final_state_patch_reproduces_donor_output():
    torch.manual_seed(9)
    model = TinyLM(20, width=16, layers=2, heads=2).eval()
    base = torch.tensor([[1,2,3,4]])
    donor = torch.tensor([[5,6,7,4]])
    with torch.no_grad():
        donor_logits, h = model(donor, capture_layer=1)
        patched, _ = model(base, intervention=(1, h[:,-1], torch.eye(16)))
        assert torch.allclose(patched[:,-1], donor_logits[:,-1], atol=1e-6)

def test_categorical_id_permutation_is_equivariant():
    import copy
    torch.manual_seed(5)
    model = TinyLM(20, width=16, heads=2).eval()
    renamed = copy.deepcopy(model)
    permutation = torch.cat((torch.tensor([0]), torch.randperm(19)+1))
    with torch.no_grad():
        renamed.embedding.weight[permutation] = model.embedding.weight
        renamed.output.weight[permutation] = model.output.weight
        renamed.output.bias[permutation] = model.output.bias
        tokens = torch.tensor([[1,2,3,4]])
        original, _ = model(tokens)
        changed, _ = renamed(permutation[tokens])
        assert torch.allclose(original, changed[:,:,permutation], atol=1e-6)

def test_explicit_patch_position_stays_at_prompt_boundary():
    torch.manual_seed(12)
    model = TinyLM(20, width=16, heads=2).eval()
    base = torch.tensor([[1,2,3,4,5]])
    donor = torch.tensor([[6,7,8,9,10]])
    with torch.no_grad():
        before,_ = model(base)
        donor_logits,h = model(donor,capture_layer=1)
        patched,_ = model(base,intervention=(1,h[:,2],torch.eye(16),torch.tensor([2])))
        assert torch.allclose(patched[:,2],donor_logits[:,2],atol=1e-6)
        assert torch.allclose(patched[:,-1],before[:,-1],atol=1e-6)
