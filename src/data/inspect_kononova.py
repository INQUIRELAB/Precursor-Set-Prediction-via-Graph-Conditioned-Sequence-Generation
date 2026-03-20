#!/usr/bin/env python
"""
Inspect Kononova et al. 2019 dataset structure.

Loads the JSON file and prints basic information about the dataset
structure without any processing.
"""

import json
import sys
from pathlib import Path
from pprint import pprint

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import KONONOVA_TEXT_MINED, RAW_SOLID_STATE_2019


def truncate_dict(d, max_str_len=100, max_list_len=3):
    """Truncate long strings and lists in a dictionary for display."""
    if isinstance(d, dict):
        return {k: truncate_dict(v, max_str_len, max_list_len) for k, v in d.items()}
    elif isinstance(d, list):
        if len(d) > max_list_len:
            return [truncate_dict(item, max_str_len, max_list_len) for item in d[:max_list_len]] + [f"... ({len(d) - max_list_len} more items)"]
        else:
            return [truncate_dict(item, max_str_len, max_list_len) for item in d]
    elif isinstance(d, str):
        if len(d) > max_str_len:
            return d[:max_str_len] + f"... (truncated, total {len(d)} chars)"
        else:
            return d
    else:
        return d


def inspect_kononova_dataset(file_path: Path):
    """Inspect the Kononova dataset JSON file."""
    
    print("=" * 70)
    print(f"INSPECTING: {file_path.name}")
    print("=" * 70)
    
    if not file_path.exists():
        print(f"\n❌ File not found: {file_path}")
        print(f"\nTrying alternative path: {RAW_SOLID_STATE_2019}")
        if RAW_SOLID_STATE_2019.exists():
            file_path = RAW_SOLID_STATE_2019
            print(f"✓ Found file at: {file_path}")
        else:
            print("❌ No Kononova dataset found")
            return
    
    # Load JSON
    print(f"\nLoading JSON file...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Basic statistics
    print("\n" + "=" * 70)
    print("DATASET STATISTICS")
    print("=" * 70)
    
    if isinstance(data, list):
        print(f"Data type: List")
        print(f"Number of records: {len(data)}")
    elif isinstance(data, dict):
        print(f"Data type: Dictionary")
        print(f"Number of top-level keys: {len(data)}")
    else:
        print(f"Data type: {type(data)}")
    
    # Top-level keys (if list, show first record keys)
    print("\n" + "=" * 70)
    print("TOP-LEVEL STRUCTURE")
    print("=" * 70)
    
    if isinstance(data, list) and len(data) > 0:
        first_record = data[0]
        if isinstance(first_record, dict):
            print(f"\nKeys in first record ({len(first_record)} keys):")
            for i, key in enumerate(first_record.keys(), 1):
                print(f"  {i:2d}. {key}")
    elif isinstance(data, dict):
        print(f"\nTop-level keys ({len(data)} keys):")
        for i, key in enumerate(data.keys(), 1):
            print(f"  {i:2d}. {key}")
    
    # Example records
    print("\n" + "=" * 70)
    print("EXAMPLE RECORDS (truncated)")
    print("=" * 70)
    
    if isinstance(data, list):
        n_examples = min(3, len(data))
        for i in range(n_examples):
            print(f"\n--- Record {i + 1} ---")
            truncated = truncate_dict(data[i], max_str_len=80, max_list_len=2)
            pprint(truncated, width=120, compact=False)
    elif isinstance(data, dict):
        # Show first 3 key-value pairs
        for i, (key, value) in enumerate(list(data.items())[:3], 1):
            print(f"\n--- Key: {key} ---")
            truncated = truncate_dict(value, max_str_len=80, max_list_len=2)
            pprint(truncated, width=120, compact=False)
    
    print("\n" + "=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)


def main():
    """Main entry point."""
    
    # Try primary path first, fall back to alternative
    file_path = KONONOVA_TEXT_MINED
    
    if not file_path.exists():
        # Try the legacy solid-state dataset (likely the Kononova 2019 data)
        file_path = RAW_SOLID_STATE_2019
    
    inspect_kononova_dataset(file_path)


if __name__ == "__main__":
    main()
