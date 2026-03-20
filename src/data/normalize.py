"""
Chemical name normalization utilities.

Standardizes chemical formulas and material names for consistency.
"""

import re
from typing import List, Union
import numpy as np


# Unicode subscript to regular digit mapping
SUBSCRIPT_MAP = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'
}


def normalize_chem_name(s: str) -> str:
    """Normalize a chemical formula or material name.
    
    Applies the following transformations:
    1. Strip leading/trailing whitespace
    2. Collapse internal whitespace to single spaces
    3. Convert unicode subscripts to regular digits
    4. Strip again after transformations
    
    Args:
        s: Chemical formula or material name
        
    Returns:
        Normalized string
    """
    if not isinstance(s, str):
        return str(s).strip()
    
    # Strip whitespace
    s = s.strip()
    
    # Collapse multiple whitespace to single space
    s = re.sub(r'\s+', ' ', s)
    
    # Convert unicode subscripts to regular digits
    for subscript, digit in SUBSCRIPT_MAP.items():
        s = s.replace(subscript, digit)
    
    # Final strip
    s = s.strip()
    
    return s


def normalize_chem_list(formulas: Union[List[str], np.ndarray]) -> List[str]:
    """Normalize a list of chemical formulas.
    
    Applies normalization to each formula, removes duplicates,
    and sorts the result.
    
    Args:
        formulas: List or array of chemical formulas
        
    Returns:
        Normalized, deduplicated, sorted list
    """
    # Handle None or empty
    if formulas is None:
        return []
    
    # Convert numpy array or other iterable to list
    try:
        formulas = list(formulas)
    except:
        return []
    
    if not formulas:
        return []
    
    # Normalize each formula
    normalized = [normalize_chem_name(f) for f in formulas]
    
    # Filter out empty strings
    normalized = [f for f in normalized if f and len(f) > 0]
    
    # Remove duplicates and sort
    normalized = sorted(set(normalized))
    
    return normalized


def normalize_reaction_data(df):
    """Normalize all chemical names in a reaction DataFrame.
    
    Applies normalization to:
    - precursor_formulas (list)
    - impurities (list)
    - target_formula (string)
    
    Args:
        df: DataFrame with reaction data
        
    Returns:
        DataFrame with normalized chemical names
    """
    import pandas as pd
    
    print("Normalizing chemical names...")
    
    # Normalize target formulas
    if 'target_formula' in df.columns:
        print("  Normalizing target_formula...")
        df['target_formula'] = df['target_formula'].apply(normalize_chem_name)
    
    # Normalize precursor lists
    if 'precursor_formulas' in df.columns:
        print("  Normalizing precursor_formulas...")
        df['precursor_formulas'] = df['precursor_formulas'].apply(normalize_chem_list)
    
    # Normalize impurity lists
    if 'impurities' in df.columns:
        print("  Normalizing impurities...")
        df['impurities'] = df['impurities'].apply(normalize_chem_list)
    
    print("  Normalization complete!")
    
    return df
