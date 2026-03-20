# Precursor-Set-Prediction-via-Graph-Conditioned-Sequence-Generation (Conceptual Pipeline)

This repository is a **non-enabling Proof-of-Concept** for the paper:

**“Combinatorial Precursor Set Prediction for Inorganic Materials Synthesis via Graph-Conditioned Sequence Generation”**

## Why this is “concept-only”

Some aspects of the method may be subject to **US patent rights**. To respect that, this public package provides:
- the **conceptual pipeline** (what components exist and how information flows),
- high-level **training/evaluation protocol descriptions**,
- and **proof sketches** for key design choices,

but it **omits the operational implementation** that could enable construction of the potentially patent-relevant system.

## Runnable conceptual demo

This repository includes a tiny runnable conceptual script:

- `concept_demo.py`

Run:

`python concept_demo.py`

What it demonstrates:
- conceptual target parsing + modality conditioning,
- retrieval-only baseline vs conceptual fused generator,
- provenance tracing for predicted precursors,
- feasibility check (element-coverage),
- toy metrics (EM, Hit@k, Jaccard),
- toy combinatorial-ceiling summary (seen vs unseen precursor sets).

What it does **not** provide:
- production model architecture/weights,
- actual training/inference implementation,
- operational pipeline details.

### Demo output structure

For each target, the script prints:
- retrieval-only baseline output,
- conceptual fused prediction,
- toy ground truth,
- per-precursor provenance (`composition-rule`, `retrieval-prior`, `structure+composition`),
- toy metrics.

At the end, it prints aggregate toy metrics and a toy combinatorial-ceiling summary.

## Data processing guide (no bundled data)

To keep this repository lightweight and avoid distributing large raw/processed files, the `data/` folder is **not bundled**.
Instead, we provide the processing code used for the main pipeline preprocessing flow.

### Data sources used in the main pipeline

The data used in the main pipeline is derived from the following public sources:

- **Kononova et al. (2019), text-mined synthesis recipes**
  - Repository: https://github.com/CederGroupHub/text-mined-synthesis_public

- **Lee et al. (2025), text-mined solid-state recipes with impurity phases**
  - Repository: https://github.com/slee-lab/solid-state-recipes-with-impurity

- **Materials Project structures** (for structure-aware context where available in the full pipeline)
  - Documentation: https://docs.materialsproject.org/apps/explorer-apps/synthesis-explorer/background

### Included preprocessing code

This repository includes the key preprocessing scripts and data utilities:

- `scripts/01_build_kononova_processed.py`
- `scripts/02_build_lee2025_processed.py`
- `scripts/03_merge_datasets.py`
- `src/config.py`
- `src/data/` (parsers, normalization, validation helpers)

### Expected raw-data layout

Place downloaded source files in:

- `data/raw/SS_rxns_80806.json.gz`
- `data/raw/solid-state_dataset_2019-06-27_upd.json`
- `data/raw/kononova2019/...`
- `data/raw/lee2025/...`

### Run preprocessing

From repository root:

1. `python scripts/01_build_kononova_processed.py`
2. `python scripts/02_build_lee2025_processed.py`
3. `python scripts/03_merge_datasets.py`

Outputs are written under `data/processed/` (created locally).

### Intended use for reviewers

- Reviewers can inspect the data provenance and the exact preprocessing workflow code.
- The runnable demo (`concept_demo.py`) is conceptual and does not consume the full production data pipeline.
- Full operational training/inference code remains intentionally omitted for patent-related non-enabling disclosure.

## Conceptual workflow (end-to-end)

1. **Target representation**
   - Parse the target material composition.
   - Optionally (when available), attach structural context from a crystallographic source.

2. **Conditioning signals**
   - **Composition conditioning**: use compositional descriptors to summarize element ratios and chemistry statistics.
   - **Structure conditioning (optional)**: use a learned structural embedding to capture coordination/geometry constraints.

3. **Context retrieval (optional; used as priors)**
   - Retrieve historical synthesis “neighbor” contexts using a similarity signal computed from available attributes.
   - Fuse retrieved contexts with the generative pathway so the model can exploit known chemistry patterns.

4. **Combinatorial generative step**
   - Generate a *set* of precursor tokens (variable-size) using an encoder-decoder model under a constrained sequence formulation.
   - Decode until termination (e.g., EOS), then convert token sequences into a precursor set.

5. **Post-processing + feasibility checks (conceptual)**
   - Normalize predicted precursor strings.
   - Optionally apply light feasibility filters (e.g., ensure predicted precursors match element coverage implied by the target).

## Evaluation (high level)

The public repo describes evaluation concepts, not the full operational benchmark code:
- **Set-level Exact Match (EM)**.
- **Hit@k** (whether the ground-truth set is present in the top-k predicted set candidates).
- **Token-level overlap metrics** (precision/recall style comparisons).

## What reviewers/readers can reproduce

Readers can understand:
- how composition/structure signals interact with retrieval priors,
- how the method avoids being limited to a closed candidate pool,
- and why the approach targets **combinatorial generalization**.

For operational reproduction, contact the authors for the appropriate restricted artifacts if applicable.

## License / patent notice

See `PATENT_NOTICE.md`.

