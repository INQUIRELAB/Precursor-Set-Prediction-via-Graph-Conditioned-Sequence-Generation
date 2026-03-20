# Interpretability (Conceptual)

The paper emphasizes interpretability as part of the scientific discovery framing.

## Which features drive precursor choice?

Conceptually test whether the model relies on:
- oxidation-state/charge-balance signals,
- compositional “chemistry statistics,”
- or structural geometry/phase constraints (when structure conditioning is enabled).

## Concrete interpretability ideas (non-enabling)

- **Attention-based saliency**: identify which conditioning tokens/neighbor contexts influence specific precursor outputs.
- **Counterfactual perturbations**: alter one element ratio or one structural embedding while keeping others fixed, then observe which precursor tokens change.
- **Ablations**: remove (i) retrieval priors, (ii) structure conditioning, or (iii) specific feature groups; compare how precursor-set diversity/plausibility changes.

