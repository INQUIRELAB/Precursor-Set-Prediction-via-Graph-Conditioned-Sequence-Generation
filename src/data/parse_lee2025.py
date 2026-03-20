#!/usr/bin/env python
"""
Parser for Lee et al. 2025 dataset.

Converts the JSON format to a canonical pandas DataFrame with standardized columns.
"""

import json
import gzip
import pandas as pd
from pathlib import Path
from typing import Union, List, Dict, Any


def parse_lee2025(json_path: Union[str, Path]) -> pd.DataFrame:
    """Parse Lee 2025 dataset to canonical DataFrame.
    
    Args:
        json_path: Path to the Lee 2025 JSON file (may be gzipped)
        
    Returns:
        DataFrame with canonical columns:
            - sample_id: Unique identifier for each record
            - source: Dataset source (always "lee2025")
            - target_formula: Chemical formula of target material
            - precursor_formulas: List of precursor formulas
            - doi: DOI reference
            - reaction_string: Balanced reaction equation
            - target_mp_id: Materials Project ID (if available)
            - impurities: List of impurity phase formulas
    """
    json_path = Path(json_path)
    
    # Load JSON (handle gzipped files)
    print(f"Loading {json_path.name}...")
    if json_path.suffix == ".gz":
        with gzip.open(json_path, "rt", encoding="utf-8") as f:
            data = json.load(f)
    else:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    print(f"Processing {len(data)} records...")
    
    # Parse each record
    records = []
    for idx, entry in enumerate(data):
        try:
            record = _parse_lee2025_record(entry, idx)
            if record:
                records.append(record)
        except Exception as e:
            # Skip malformed records
            continue
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    print(f"Parsed {len(df)} valid records")
    
    return df


def _parse_lee2025_record(entry: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """Parse a single Lee 2025 record to canonical format.
    
    Args:
        entry: Single JSON record from Lee 2025 dataset
        idx: Index of the record (for sample_id)
        
    Returns:
        Dictionary with canonical fields, or None if parsing fails
    """
    # Extract target information
    target_list = entry.get("target", [])
    if not target_list or len(target_list) == 0:
        return None
    
    target = target_list[0]  # Take first target
    target_formula = target.get("material_formula", "")
    if not target_formula:
        return None
    
    target_mp_id = target.get("mp_id")
    
    # Extract precursors
    precursors = entry.get("precursors", [])
    precursor_formulas = [
        p.get("material_formula", "") 
        for p in precursors 
        if p.get("material_formula")
    ]
    
    if not precursor_formulas:
        return None
    
    # Extract reaction string from target_reaction
    reaction_string = None
    target_reaction = entry.get("target_reaction", [])
    if target_reaction and len(target_reaction) > 0:
        # target_reaction is a list, each element is [name, dict, ...]
        # The last element is usually the reaction string
        reaction_data = target_reaction[0]
        if len(reaction_data) >= 4:
            reaction_string = reaction_data[3]
    
    # Extract DOI
    doi = entry.get("DOI", "")
    
    # Extract impurities
    impurity_phases = entry.get("impurity_phase", [])
    impurities = [
        imp.get("material_formula", "")
        for imp in impurity_phases
        if imp.get("material_formula")
    ]
    
    # Create unique sample_id
    sample_id = f"lee2025_{idx:06d}"
    
    return {
        "sample_id": sample_id,
        "source": "lee2025",
        "target_formula": target_formula,
        "precursor_formulas": precursor_formulas,
        "doi": doi,
        "reaction_string": reaction_string,
        "target_mp_id": target_mp_id,
        "impurities": impurities
    }


def main():
    """Demo: parse and display sample data."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from src.config import RAW_SS_RXNS_80806
    
    # Parse the dataset
    df = parse_lee2025(RAW_SS_RXNS_80806)
    
    # Display info
    print("\n" + "=" * 70)
    print("PARSED DATAFRAME INFO")
    print("=" * 70)
    print(f"\nShape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nData types:")
    print(df.dtypes)
    
    print("\n" + "=" * 70)
    print("SAMPLE RECORDS")
    print("=" * 70)
    print("\n", df.head(3).to_string())
    
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"Unique targets: {df['target_formula'].nunique()}")
    print(f"Unique DOIs: {df['doi'].nunique()}")
    print(f"Records with MP ID: {df['target_mp_id'].notna().sum()}")
    print(f"Records with impurities: {df['impurities'].apply(lambda x: len(x) > 0).sum()}")
    
    # Check precursor counts
    precursor_counts = df["precursor_formulas"].apply(len)
    print(f"\nPrecursor count distribution:")
    print(precursor_counts.value_counts().sort_index())
    
    # Check impurity counts
    impurity_counts = df["impurities"].apply(len)
    print(f"\nImpurity count distribution:")
    print(impurity_counts.value_counts().sort_index())


if __name__ == "__main__":
    main()
