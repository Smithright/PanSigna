# Sources and provenance

Primary methodological sources, linked rather than copied into the repository:

- Geiger, Lu, Icard and Potts (2021), [Causal Abstractions of Neural Networks](https://arxiv.org/abs/2106.02997).
  Motivates explicit high-level variables and interchange intervention validation.
- Ameisen et al. (2025), [Circuit Tracing](https://www.transformer-circuits.pub/2025/attribution-graphs/methods.html).
  Motivates validating a proposed feature's causal role in the original model;
  this repository does not implement their cross-layer transcoders.
- [Concept Bottleneck Large Language Models](https://arxiv.org/abs/2412.07992).
  Architectural comparator for a later phase; no bottleneck architecture is tested here.
- [PyTorch TransformerEncoderLayer](https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoderLayer.html).
  Borrowed implementation infrastructure; installed versions recorded in run manifests.

The separately maintained PanSigna project research includes a frontier report,
annotated source review and provenance ledger. Private file links and raw source
corpora are deliberately not distributed with this code.

The initiating design discussion supplies the bit-level null rule and the hypothesis
about notion-aligned vectors. This repository does not claim to have re-reviewed
or validated the complete original corpus. No original source file is edited.
