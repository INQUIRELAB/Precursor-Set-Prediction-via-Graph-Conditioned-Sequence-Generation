#!/usr/bin/env python3
"""
Runnable conceptual pipeline demo (non-enabling).

This file provides a toy, interpretable approximation of the paper workflow:
input parse -> conceptual composition/structure encoding -> retrieval priors ->
conceptual fusion -> set generation -> feasibility checks -> toy evaluation.

It intentionally does NOT include the proprietary/generative production model.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple


ELEMENT_RE = re.compile(r"([A-Z][a-z]?)([0-9]*\.?[0-9]*)")


def parse_formula(formula: str) -> Dict[str, float]:
    """Very small formula parser for conceptual demo purposes."""
    out: Dict[str, float] = {}
    for elem, count in ELEMENT_RE.findall(formula):
        val = float(count) if count else 1.0
        out[elem] = out.get(elem, 0.0) + val
    if not out:
        raise ValueError(f"Could not parse formula: {formula}")
    return out


def default_oxide_for_element(elem: str) -> str:
    """Map element -> conceptual default precursor family."""
    special = {
        "Li": "Li2CO3",
        "Na": "Na2CO3",
        "K": "K2CO3",
        "Ba": "BaCO3",
        "Sr": "SrCO3",
        "Ca": "CaCO3",
        "W": "WO3",
        "Mo": "MoO3",
    }
    if elem in special:
        return special[elem]
    if elem == "O":
        return ""
    # Generic conceptual rule: use sesquioxide-style template.
    return f"{elem}2O3"


@dataclass
class ConceptConfig:
    use_retrieval: bool = True
    retrieval_top_k: int = 2
    use_structure_signal: bool = True


class ConceptPipeline:
    """Toy conceptual pipeline; not the production method."""

    def __init__(self, config: ConceptConfig, retrieval_db: Dict[str, List[str]]):
        self.config = config
        self.retrieval_db = retrieval_db

    def encode_composition(self, formula: str) -> Dict[str, float]:
        return parse_formula(formula)

    def encode_structure(self, structure_available: bool) -> Dict[str, float]:
        # Conceptual placeholder for "structure-conditioned" branch.
        return {"polymorph_signal": 1.0 if structure_available else 0.0}

    def retrieve_priors(self, formula: str) -> List[str]:
        if not self.config.use_retrieval:
            return []
        # Simple keyword-style retrieval: exact or prefix match on formula string.
        if formula in self.retrieval_db:
            return self.retrieval_db[formula][: self.config.retrieval_top_k]
        for key, vals in self.retrieval_db.items():
            if formula.startswith(key) or key.startswith(formula):
                return vals[: self.config.retrieval_top_k]
        return []

    def retrieval_only_predict(self, formula: str) -> Set[str]:
        return set(self.retrieve_priors(formula))

    def generate_precursor_set(self, formula: str, structure_available: bool) -> Tuple[Set[str], Dict[str, str]]:
        elem_counts = self.encode_composition(formula)
        struct_sig = self.encode_structure(structure_available)
        priors = self.retrieve_priors(formula)

        predicted: Set[str] = set()
        provenance: Dict[str, str] = {}
        for elem in elem_counts:
            token = default_oxide_for_element(elem)
            if token:
                predicted.add(token)
                provenance[token] = "composition-rule"

        # Conceptual "fusion": add prior suggestions as soft context.
        for p in priors:
            predicted.add(p)
            provenance[p] = "retrieval-prior"

        # Conceptual structure-conditioned tweak:
        # if structure is available and tungsten/molybdenum exists, retain oxide route.
        if self.config.use_structure_signal and struct_sig["polymorph_signal"] > 0:
            for heavy in ("WO3", "MoO3"):
                if heavy in predicted:
                    provenance[heavy] = "structure+composition"

        return predicted, provenance


def element_set_from_precursors(precursors: Set[str]) -> Set[str]:
    elems: Set[str] = set()
    for p in precursors:
        elems.update(parse_formula(p).keys())
    elems.discard("O")
    return elems


def element_coverage_ok(target_formula: str, precursors: Set[str]) -> bool:
    target_elems = set(parse_formula(target_formula).keys())
    target_elems.discard("O")
    return target_elems.issubset(element_set_from_precursors(precursors))


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def evaluate_sample(gt: Set[str], pred: Set[str], pred_topk: List[Set[str]]) -> Dict[str, float]:
    em = 1.0 if gt == pred else 0.0
    hit_at_k = 1.0 if any(gt == p for p in pred_topk) else 0.0
    return {
        "em": em,
        "hit_at_k": hit_at_k,
        "jaccard": jaccard(gt, pred),
    }


def load_demo_inputs(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["targets"]


def summarize_ceiling(targets: List[Dict[str, object]], train_sets: Set[frozenset]) -> Dict[str, float]:
    total = len(targets)
    seen = 0
    for t in targets:
        gt = frozenset(t["ground_truth_precursors"])
        if gt in train_sets:
            seen += 1
    unseen = total - seen
    oracle_retrieval_limit = seen / total if total else 0.0
    return {
        "total": float(total),
        "seen": float(seen),
        "unseen": float(unseen),
        "oracle_retrieval_limit": oracle_retrieval_limit,
    }


def main() -> None:
    repo = Path(__file__).resolve().parent
    demo_path = repo / "demo_inputs.json"
    targets = load_demo_inputs(demo_path)

    # Tiny conceptual retrieval memory, intentionally simplistic.
    retrieval_db = {
        "Li2Mg2(WO4)3": ["WO3", "MgO", "Li2CO3"],
        "Ni0.5Zn0.5Fe2O4": ["NiO", "ZnO", "Fe2O3"],
    }

    pipeline = ConceptPipeline(ConceptConfig(use_retrieval=True), retrieval_db)
    train_precursor_sets = {
        frozenset(["WO3", "MgO", "Li2CO3"]),
        frozenset(["NiO", "ZnO", "Fe2O3"]),
        frozenset(["La2O3", "K2CO3", "MnCO3"]),
    }

    print("=== Conceptual Pipeline Demo (Non-Enabling) ===")
    print("Stages: parse -> encode(comp/struct) -> retrieve -> fuse -> generate -> feasibility -> evaluate")

    metric_rows: List[Dict[str, float]] = []
    for item in targets:
        formula = str(item["target_formula"])
        structure_available = bool(item.get("structure_available", False))
        gt_set = set(item.get("ground_truth_precursors", []))

        retrieval_only = pipeline.retrieval_only_predict(formula)
        pred_set, provenance = pipeline.generate_precursor_set(formula, structure_available)
        pred = sorted(pred_set)

        # Toy top-k list: [retrieval-only, conceptual-fused]
        topk = [retrieval_only, pred_set]
        scores = evaluate_sample(gt_set, pred_set, topk)
        scores["coverage_ok"] = 1.0 if element_coverage_ok(formula, pred_set) else 0.0
        metric_rows.append(scores)

        print(f"\nTarget: {formula}")
        print(f"Structure available: {structure_available}")
        print(f"Retrieval-only baseline: {sorted(retrieval_only)}")
        print(f"Conceptual fused prediction: {pred}")
        print(f"Ground truth (demo): {sorted(gt_set)}")
        print(f"Provenance: {provenance}")
        print(
            "Metrics -> "
            f"EM={scores['em']:.0f}, Hit@2={scores['hit_at_k']:.0f}, "
            f"Jaccard={scores['jaccard']:.2f}, Feasibility(coverage)={scores['coverage_ok']:.0f}"
        )

    n = max(1, len(metric_rows))
    avg_em = sum(r["em"] for r in metric_rows) / n
    avg_hk = sum(r["hit_at_k"] for r in metric_rows) / n
    avg_j = sum(r["jaccard"] for r in metric_rows) / n
    avg_cov = sum(r["coverage_ok"] for r in metric_rows) / n

    ceiling = summarize_ceiling(targets, train_precursor_sets)
    print("\n=== Aggregate Toy Summary ===")
    print(f"Avg EM: {avg_em:.2f}")
    print(f"Avg Hit@2: {avg_hk:.2f}")
    print(f"Avg Jaccard: {avg_j:.2f}")
    print(f"Avg Element-Coverage Feasibility: {avg_cov:.2f}")
    print(
        "Combinatorial-ceiling toy view -> "
        f"seen={int(ceiling['seen'])}/{int(ceiling['total'])}, "
        f"unseen={int(ceiling['unseen'])}/{int(ceiling['total'])}, "
        f"retrieval-oracle-limit={ceiling['oracle_retrieval_limit']:.2f}"
    )


if __name__ == "__main__":
    main()

