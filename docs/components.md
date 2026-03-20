# Conceptual Model Components

## Conditioning modalities

### Composition conditioning
Captures elemental ratios and chemistry statistics derived from the target formula.

### Structure conditioning (optional)
Encodes geometry-related constraints so the model can better reflect coordination and phase/geometry effects when a crystallographic context is available.

## Retrieval priors (optional)

Historical synthesis contexts can improve plausibility by providing:
- precursor family priors (what kinds of precursors are common),
- decomposition pathway patterns,
- and corpus-level regularities.

Conceptually, retrieval is used as additional context, not as a closed candidate pool constraint.

## Generative set construction (core idea)

The generator produces precursor token sequences that are then interpreted as a set.
The combinatorial aspect is emphasized:
- the method is not restricted to enumerating precursor combinations from a fixed catalog,
- it targets *open-ended* combination construction under chemistry-relevant constraints.

