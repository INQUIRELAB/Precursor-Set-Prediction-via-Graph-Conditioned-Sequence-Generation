# Evaluation Protocol (High Level)

## Benchmark split concept

Use a temporal split to reduce leakage between training and evaluation:
- training uses earlier records,
- validation uses an intermediate year window,
- test uses later records.

## Vocabulary restriction concept

For evaluation, predictions are restricted to a fixed precursor vocabulary of size `K` (conceptually `K=150` in the paper).

## Metrics (conceptual definitions)

1. **Set-level Exact Match (EM)**
   - Predicted precursor set equals the ground-truth set.

2. **Hit@k**
   - The ground-truth set appears in the top-k predicted candidate sets.

3. **Token-level overlap**
   - Precision/recall-like comparisons between predicted and ground-truth tokens.

## Out-of-distribution evaluation idea

Evaluate whether performance remains non-trivial on:
- targets whose ground-truth precursor sets are not present in training records,
- and optionally on structurally constrained targets when structure conditioning is enabled.

