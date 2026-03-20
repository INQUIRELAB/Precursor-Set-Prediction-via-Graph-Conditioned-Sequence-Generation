# Pseudocode: Training + Evaluation Protocol (Conceptual)

```text
Inputs:
  dataset of (target, ground_truth_precursor_set) examples

Split concept:
  temporal split to reduce leakage:
    train: earlier records
    validation: intermediate year window
    test: later records

Vocabulary concept:
  define a fixed precursor token vocabulary size K (paper uses K=150)

Training concept:
  optimize a set prediction objective using the token vocabulary,
  encouraging correct token sets under combinatorial ambiguity.

Evaluation concept:
  compute:
    - set EM
    - Hit@k
    - token-level overlap metrics
```

