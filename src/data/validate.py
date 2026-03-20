"""
Validation functions for reaction datasets.

Ensures data quality by checking for missing values, correct types,
and unique identifiers.
"""

import pandas as pd
from typing import List


def drop_missing_target(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with missing or empty target_formula.
    
    Args:
        df: DataFrame with target_formula column
        
    Returns:
        DataFrame with valid target_formula values
    """
    n_before = len(df)
    
    # Drop NaN values
    df = df.dropna(subset=['target_formula'])
    
    # Drop empty strings
    df = df[df['target_formula'].str.strip().str.len() > 0]
    
    n_after = len(df)
    n_dropped = n_before - n_after
    
    if n_dropped > 0:
        print(f"  Dropped {n_dropped} rows with missing target_formula")
    
    return df.reset_index(drop=True)


def drop_empty_precursors(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with empty precursor_formulas list.
    
    Args:
        df: DataFrame with precursor_formulas column
        
    Returns:
        DataFrame with non-empty precursor lists
    """
    n_before = len(df)
    
    # Drop NaN values
    df = df.dropna(subset=['precursor_formulas'])
    
    # Drop empty lists
    df = df[df['precursor_formulas'].apply(lambda x: isinstance(x, list) and len(x) > 0)]
    
    n_after = len(df)
    n_dropped = n_before - n_after
    
    if n_dropped > 0:
        print(f"  Dropped {n_dropped} rows with empty precursor_formulas")
    
    return df.reset_index(drop=True)


def ensure_precursors_list_str(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure precursor_formulas contains list of strings.
    
    Converts any non-conforming values and drops rows that can't be converted.
    
    Args:
        df: DataFrame with precursor_formulas column
        
    Returns:
        DataFrame with precursor_formulas as list[str]
    """
    n_before = len(df)
    
    def convert_to_list_str(value):
        """Convert value to list of strings."""
        # Already a list
        if isinstance(value, list):
            # Convert all elements to strings and filter empty
            result = [str(x).strip() for x in value if x is not None]
            result = [x for x in result if len(x) > 0]
            return result if len(result) > 0 else None
        
        # Single string - wrap it in a list
        elif isinstance(value, str):
            value = value.strip()
            return [value] if len(value) > 0 else None
        
        # Other types - can't convert
        else:
            return None
    
    # Apply conversion
    df['precursor_formulas'] = df['precursor_formulas'].apply(convert_to_list_str)
    
    # Drop rows where conversion failed
    df = df.dropna(subset=['precursor_formulas'])
    
    n_after = len(df)
    n_dropped = n_before - n_after
    
    if n_dropped > 0:
        print(f"  Dropped {n_dropped} rows with invalid precursor_formulas type")
    
    return df.reset_index(drop=True)


def ensure_unique_sample_id(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure sample_id column contains unique values.
    
    If duplicates are found, keeps the first occurrence and drops the rest.
    
    Args:
        df: DataFrame with sample_id column
        
    Returns:
        DataFrame with unique sample_id values
    """
    n_before = len(df)
    
    # Check for duplicates
    duplicates = df['sample_id'].duplicated()
    n_duplicates = duplicates.sum()
    
    if n_duplicates > 0:
        print(f"  Warning: Found {n_duplicates} duplicate sample_ids")
        print(f"  Keeping first occurrence, dropping rest")
        df = df[~duplicates]
    
    n_after = len(df)
    
    return df.reset_index(drop=True)


def validate_dataset(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Run all validation checks on a dataset.
    
    Args:
        df: DataFrame to validate
        verbose: Whether to print progress messages
        
    Returns:
        Validated DataFrame
    """
    if verbose:
        print("\nValidating dataset...")
        print(f"  Initial records: {len(df)}")
    
    # Drop missing targets
    df = drop_missing_target(df)
    
    # Drop empty precursors
    df = drop_empty_precursors(df)
    
    # Ensure precursors is list[str]
    df = ensure_precursors_list_str(df)
    
    # Ensure unique sample_id
    df = ensure_unique_sample_id(df)
    
    if verbose:
        print(f"  Final records: {len(df)}")
        print(f"  Validation complete!")
    
    return df


def print_validation_summary(df: pd.DataFrame):
    """Print summary statistics after validation.
    
    Args:
        df: Validated DataFrame
    """
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    print(f"\nTotal records: {len(df)}")
    print(f"Unique targets: {df['target_formula'].nunique()}")
    print(f"Unique sample_ids: {df['sample_id'].nunique()}")
    
    if 'source' in df.columns:
        print(f"\nRecords by source:")
        print(df['source'].value_counts())
    
    # Precursor statistics
    precursor_counts = df['precursor_formulas'].apply(len)
    print(f"\nPrecursors per reaction:")
    print(f"  Mean: {precursor_counts.mean():.2f}")
    print(f"  Median: {precursor_counts.median():.0f}")
    print(f"  Min: {precursor_counts.min()}")
    print(f"  Max: {precursor_counts.max()}")
    
    print("\n" + "=" * 70)


def ensure_impurities_list_str(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure impurities column contains list of strings.
    
    If impurities column doesn't exist, creates it with empty lists.
    Converts any non-conforming values and drops rows that can't be converted.
    
    Args:
        df: DataFrame with optional impurities column
        
    Returns:
        DataFrame with impurities as list[str]
    """
    n_before = len(df)
    
    # Create column if it doesn't exist
    if 'impurities' not in df.columns:
        df['impurities'] = [[] for _ in range(len(df))]
        print(f"  Created impurities column with empty lists")
        return df
    
    def convert_to_list_str(value):
        """Convert value to list of strings."""
        # Already a list
        if isinstance(value, list):
            # Convert all elements to strings and filter empty
            result = []
            for x in value:
                if x is not None:
                    try:
                        s = str(x).strip()
                        if len(s) > 0:
                            result.append(s)
                    except:
                        pass
            return result
        
        # None - convert to empty list
        elif value is None:
            return []
        
        # Single string - wrap it in a list
        elif isinstance(value, str):
            value = value.strip()
            return [value] if len(value) > 0 else []
        
        # Other types (including float NaN) - convert to empty list
        else:
            return []
    
    # Apply conversion
    df['impurities'] = df['impurities'].apply(convert_to_list_str)
    
    n_after = len(df)
    
    return df
