import torch
from torch import nn

def patch_subspace(base, donor, basis):
    """Replace only the orthonormal basis coordinates with donor coordinates."""
    return base + ((donor - base) @ basis) @ basis.T

def fit_subspace(x, labels, classes, ridge=0.01):
    """Linear ridge decoder row space, rank capped at classes-1."""
    x = x.double()
    x = x - x.mean(0)
    y = torch.nn.functional.one_hot(labels, classes).double()
    y = y - y.mean(0)
    w = torch.linalg.solve(x.T @ x + ridge * torch.eye(x.shape[1], dtype=x.dtype), x.T @ y)
    u, singular, _ = torch.linalg.svd(w, full_matrices=False)
    rank = min(classes - 1, int((singular > 1e-8).sum()))
    return u[:, :rank].float()

class TinyLM(nn.Module):
    """Causal transformer, trained on next-token answers (conditional LM pilot)."""
    def __init__(self, vocab, width=48, layers=2, heads=4, max_length=256):
        super().__init__()
        self.embedding = nn.Embedding(vocab, width, padding_idx=0)
        self.position = nn.Embedding(max_length, width)
        self.blocks = nn.ModuleList([nn.TransformerEncoderLayer(width, heads, width*2,
            dropout=0, batch_first=True, norm_first=True) for _ in range(layers)])
        self.norm = nn.LayerNorm(width)
        self.output = nn.Linear(width, vocab)

    def forward(self, tokens, lengths=None, capture_layer=None, intervention=None):
        if lengths is None:
            lengths = torch.full((len(tokens),), tokens.shape[1], dtype=torch.long)
        pos = torch.arange(tokens.shape[1])
        h = self.embedding(tokens) + self.position(pos)
        mask = torch.ones(tokens.shape[1], tokens.shape[1], dtype=torch.bool).triu(1)
        captured = None
        for layer, block in enumerate(self.blocks):
            h = block(h, src_mask=mask, src_key_padding_mask=tokens.eq(0))
            if layer == capture_layer:
                captured = h.clone()
            if intervention is not None and layer == intervention[0]:
                _, donor, basis = intervention[:3]
                h = h.clone()
                idx = torch.arange(len(h))
                positions = intervention[3] if len(intervention) == 4 else lengths-1
                h[idx, positions] = patch_subspace(h[idx, positions], donor, basis)
        return self.output(self.norm(h)), captured
