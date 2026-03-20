"""
Dataset loader for solid-state synthesis reactions.

Loads and processes both dataset formats, cleans data,
and creates train/val/test splits.
"""

import json
import gzip
from pathlib import Path
from typing import List, Tuple, Dict, Any
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from .schema import Reaction, parse_dataset1_reaction, parse_dataset2_reaction


class ReactionDataset:
    """Loader for solid-state synthesis reaction datasets."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize dataset loader.
        
        Args:
            data_dir: Base directory containing raw/ and processed/ subdirectories
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_raw_datasets(self) -> List[Reaction]:
        """Load both raw JSON datasets and parse into canonical format.
        
        Returns:
            List of Reaction objects
        """
        reactions = []
        
        # Load dataset 1 (compressed)
        dataset1_path = self.raw_dir / "SS_rxns_80806.json.gz"
        if dataset1_path.exists():
            print(f"Loading {dataset1_path}...")
            with gzip.open(dataset1_path, 'rt', encoding='utf-8') as f:
                data1 = json.load(f)
            
            for entry in data1:
                reaction = parse_dataset1_reaction(entry)
                if reaction:
                    reactions.append(reaction)
            print(f"  Loaded {len([r for r in reactions])} valid reactions from dataset 1")
        
        # Load dataset 2
        dataset2_path = self.raw_dir / "solid-state_dataset_2019-06-27_upd.json"
        if dataset2_path.exists():
            print(f"Loading {dataset2_path}...")
            with open(dataset2_path, 'r', encoding='utf-8') as f:
                data2 = json.load(f)
            
            before = len(reactions)
            for entry in data2:
                reaction = parse_dataset2_reaction(entry)
                if reaction:
                    reactions.append(reaction)
            print(f"  Loaded {len(reactions) - before} valid reactions from dataset 2")
        
        return reactions
    
    def clean_reactions(self, reactions: List[Reaction]) -> List[Reaction]:
        """Clean and filter reactions.
        
        Args:
            reactions: List of raw reactions
            
        Returns:
            List of cleaned reactions
        """
        print(f"\nCleaning {len(reactions)} reactions...")
        
        # Remove invalid reactions
        valid = [r for r in reactions if r.is_valid()]
        print(f"  After validation: {len(valid)} reactions")
        
        # Remove duplicates based on (target, precursors) tuple
        seen = set()
        unique = []
        for r in valid:
            key = (r.target_formula, tuple(sorted(r.precursor_formulas)))
            if key not in seen:
                seen.add(key)
                unique.append(r)
        print(f"  After deduplication: {len(unique)} reactions")
        
        # Filter out reactions with too many or too few precursors
        filtered = [r for r in unique if 1 <= len(r.precursor_formulas) <= 10]
        print(f"  After precursor count filter: {len(filtered)} reactions")
        
        return filtered
    
    def create_splits(self, reactions: List[Reaction], 
                     train_ratio: float = 0.7,
                     val_ratio: float = 0.15,
                     test_ratio: float = 0.15,
                     random_state: int = 42) -> Tuple[List[Reaction], List[Reaction], List[Reaction]]:
        """Create train/val/test splits.
        
        Args:
            reactions: List of reactions
            train_ratio: Fraction for training
            val_ratio: Fraction for validation
            test_ratio: Fraction for testing
            random_state: Random seed for reproducibility
            
        Returns:
            Tuple of (train, val, test) reaction lists
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1"
        
        # First split: train vs (val + test)
        train, temp = train_test_split(
            reactions, 
            test_size=(val_ratio + test_ratio),
            random_state=random_state
        )
        
        # Second split: val vs test
        val_size = val_ratio / (val_ratio + test_ratio)
        val, test = train_test_split(
            temp,
            test_size=(1 - val_size),
            random_state=random_state
        )
        
        print(f"\nSplit sizes:")
        print(f"  Train: {len(train)} ({len(train)/len(reactions)*100:.1f}%)")
        print(f"  Val:   {len(val)} ({len(val)/len(reactions)*100:.1f}%)")
        print(f"  Test:  {len(test)} ({len(test)/len(reactions)*100:.1f}%)")
        
        return train, val, test
    
    def save_processed(self, train: List[Reaction], val: List[Reaction], 
                      test: List[Reaction], split_name: str = "default"):
        """Save processed data to parquet files.
        
        Args:
            train: Training reactions
            val: Validation reactions
            test: Test reactions
            split_name: Name for this split
        """
        # Convert to DataFrames
        train_df = pd.DataFrame([r.to_dict() for r in train])
        val_df = pd.DataFrame([r.to_dict() for r in val])
        test_df = pd.DataFrame([r.to_dict() for r in test])
        
        # Add split indicator
        train_df['split'] = 'train'
        val_df['split'] = 'val'
        test_df['split'] = 'test'
        
        # Combine and save
        all_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
        output_path = self.processed_dir / "reactions.parquet"
        all_df.to_parquet(output_path, index=False)
        print(f"\nSaved processed data to {output_path}")
        
        # Save split metadata
        split_info = {
            'train_size': len(train),
            'val_size': len(val),
            'test_size': len(test),
            'total_size': len(all_df),
            'split_name': split_name
        }
        split_path = self.processed_dir / "split_info.json"
        with open(split_path, 'w') as f:
            json.dump(split_info, f, indent=2)
        print(f"Saved split info to {split_path}")
    
    def load_processed(self) -> pd.DataFrame:
        """Load processed parquet data.
        
        Returns:
            DataFrame with all reactions
        """
        parquet_path = self.processed_dir / "reactions.parquet"
        if not parquet_path.exists():
            raise FileNotFoundError(f"Processed data not found at {parquet_path}")
        
        return pd.read_parquet(parquet_path)
    
    def get_statistics(self, reactions: List[Reaction]) -> Dict[str, Any]:
        """Compute dataset statistics.
        
        Args:
            reactions: List of reactions
            
        Returns:
            Dictionary of statistics
        """
        # Collect all precursors
        all_precursors = set()
        all_targets = set()
        precursor_counts = []
        
        for r in reactions:
            all_targets.add(r.target_formula)
            all_precursors.update(r.precursor_formulas)
            precursor_counts.append(len(r.precursor_formulas))
        
        stats = {
            'num_reactions': len(reactions),
            'num_unique_targets': len(all_targets),
            'num_unique_precursors': len(all_precursors),
            'avg_precursors_per_reaction': np.mean(precursor_counts),
            'median_precursors_per_reaction': np.median(precursor_counts),
            'min_precursors': np.min(precursor_counts),
            'max_precursors': np.max(precursor_counts)
        }
        
        return stats
