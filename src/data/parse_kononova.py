#!/usr/bin/env python
"""
Parser for Kononova et al. 2019 dataset.

Converts the JSON format to a canonical pandas DataFrame with standardized columns.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Union, List, Dict, Any


def parse_kononova(json_path: Union[str, Path]) -> pd.DataFrame:
    """Parse Kononova dataset to canonical DataFrame.
    
    Args:
        json_path: Path to the Kononova JSON file
        
    Returns:
        DataFrame with canonical columns:
            - sample_id: Unique identifier for each record
            - source: Dataset source (always "kononova2019")
            - target_formula: Chemical formula of target material
            - precursor_formulas: List of precursor formulas
            - doi: DOI reference
            - reaction_string: Balanced reaction equation
            - target_mp_id: Materials Project ID (if available)
    """
    json_path = Path(json_path)
    
    # Load JSON
    print(f"Loading {json_path.name}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Processing {len(data)} records...")
    
    # Parse each record
    records = []
    for idx, entry in enumerate(data):
        try:
            record = _parse_kononova_record(entry, idx)
            if record:
                records.append(record)
        except Exception as e:
            # Skip malformed records
            continue
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    print(f"Parsed {len(df)} valid records")
    
    return df


def _parse_kononova_record(entry: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """Parse a single Kononova record to canonical format.
    
    Args:
        entry: Single JSON record from Kononova dataset
        idx: Index of the record (for sample_id)
        
    Returns:
        Dictionary with canonical fields, or None if parsing fails
    """
    # Extract target information
    target = entry.get('target', {})
    if not target:
        return None
    
    target_formula = target.get('material_formula', '')
    if not target_formula:
        return None
    
    target_mp_id = target.get('mp_id')
    
    # Extract precursors
    precursors = entry.get('precursors', [])
    precursor_formulas = [
        p.get('material_formula', '') 
        for p in precursors 
        if p.get('material_formula')
    ]
    
    if not precursor_formulas:
        return None
    
    # Extract reaction string
    reaction_string = entry.get('reaction_string')
    
    # Extract DOI
    doi = entry.get('doi', '')
    
    # Create unique sample_id
    sample_id = f"kononova2019_{idx:06d}"
    
    return {
        'sample_id': sample_id,
        'source': 'kononova2019',
        'target_formula': target_formula,
        'precursor_formulas': precursor_formulas,
        'doi': doi,
        'reaction_string': reaction_string,
        'target_mp_id': target_mp_id
    }


def main():
    """Demo: parse and display sample data."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from src.config import RAW_SOLID_STATE_2019
    
    # Parse the dataset
    df = parse_kononova(RAW_SOLID_STATE_2019)
    
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
    
    # Check precursor counts
    precursor_counts = df['precursor_formulas'].apply(len)
    print(f"\nPrecursor count distribution:")
    print(precursor_counts.value_counts().sort_index())


if __name__ == "__main__":
    main()
