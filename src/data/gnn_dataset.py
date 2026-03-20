"""
PyTorch Geometric Dataset for Custom GNN Precursor Prediction.
Implements Pymatgen-based graph construction to bypass torch-cluster dependencies.
"""

import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from pathlib import Path
from pymatgen.core import Structure
from torch_geometric.data import Data, Batch

class GNNPrecursorDataset(Dataset):
    def __init__(self, metadata_file=None, metadata_df=None, vocab_size=500, cutoff=6.0, max_neighbors=32):
        """
        Args:
            metadata_file (str/Path): Path to gemnet_training_data.parquet
            metadata_df (pd.DataFrame): Optional dataframe implementation (avoids reloading)
            vocab_size (int): Expected vocabulary size
            cutoff (float): Radius cutoff for graph
            max_neighbors (int): Max neighbors per atom
        """
        self.metadata_file = Path(metadata_file) if metadata_file else None
        self.vocab_size = vocab_size
        self.cutoff = cutoff
        self.max_neighbors = max_neighbors
        
        # Load metadata
        if metadata_df is not None:
             self.df = metadata_df.reset_index(drop=True)
             print(f"Loaded {len(self.df)} samples from DataFrame.")
        elif self.metadata_file:
            print(f"Loading dataset from {self.metadata_file}...")
            self.df = pd.read_parquet(self.metadata_file)
            print(f"Loaded {len(self.df)} samples from file.")
        else:
            raise ValueError("Must provide either metadata_file or metadata_df")

        # Filter (already done, but safe to keep)
        # Assuming df has 'cif_path'
        if 'cif_path' in self.df.columns:
            self.df = self.df[self.df['cif_path'].notna()]
        
        
        from src.config import BASE_DIR
        self.base_dir = BASE_DIR

    def __len__(self):
        return len(self.df)

    def _get_graph(self, structure):
        """Convert structure to graph using Pymatgen."""
        # 1. Node features (Atomic Numbers)
        z = torch.tensor(structure.atomic_numbers, dtype=torch.long)
        pos = torch.tensor(structure.cart_coords, dtype=torch.float)
        
        # 2. Edges (Connectivity)
        # Pymatgen get_all_neighbors
        # Returns list of neighbors for each atom
        all_neighbors = structure.get_all_neighbors(self.cutoff, include_index=True)
        
        # Build edge_index and edge_attr
        src_indices = []
        dst_indices = []
        distances = []
        
        for i, neighbors in enumerate(all_neighbors):
            # Sort by distance and take max_neighbors
            neighbors = sorted(neighbors, key=lambda x: x[1])[:self.max_neighbors]
            
            for nbr in neighbors:
                # nbr is (site, distance, index) or similar depending on pymatgen version
                # In newer pymatgen: Neighbor object or tuple
                # if include_index=True: (PeriodicSite, distance, index)
                
                # Check formatting carefully
                # Pymatgen's get_all_neighbors returns list of neighbors.
                # neighbors is list of PeriodicNeighbor
                
                # Accessing properties safely
                try:
                    d = nbr.nn_distance # PeriodicNeighbor attribute
                    j = nbr.index # Index of neighbor
                except AttributeError:
                    # Fallback for older versions or tuple returns
                    # typically (site, dist, index)
                    d = nbr[1]
                    j = nbr[2]
                
                src_indices.append(i) # Source atom
                dst_indices.append(j) # Target atom
                distances.append(d)
                
        edge_index = torch.tensor([src_indices, dst_indices], dtype=torch.long)
        edge_distances = torch.tensor(distances, dtype=torch.float)
        
        # Edge Weights: Gaussian RBF (simple)
        # exp(-d^2 / sigma^2)
        # sigma ~= 1.0 roughly good for Angstrom scale
        edge_weight = torch.exp(-edge_distances**2)
        
        return Data(z=z, pos=pos, edge_index=edge_index, edge_weight=edge_weight)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        cif_path = self.base_dir / row['cif_path']
        
        try:
            structure = Structure.from_file(cif_path)
            data = self._get_graph(structure)
        except Exception as e:
            # Fallback (Dummy H atom)
            z = torch.tensor([1], dtype=torch.long)
            pos = torch.tensor([[0.0, 0.0, 0.0]], dtype=torch.float)
            edge_index = torch.tensor([[0],[0]], dtype=torch.long)
            edge_weight = torch.tensor([1.0], dtype=torch.float)
            data = Data(z=z, pos=pos, edge_index=edge_index, edge_weight=edge_weight)
            
        # Target
        target = torch.zeros(self.vocab_size, dtype=torch.float32)
        indices = row['precursor_indices']
        if isinstance(indices, (list, np.ndarray)):
            for i in indices:
                if 0 <= i < self.vocab_size:
                    target[i] = 1.0
        
        # Add sample_id for tracking
        data.sample_id = row['sample_id']
                    
        return data, target

def collate_gnn(batch):
    data_list = [item[0] for item in batch]
    targets = [item[1] for item in batch]
    
    # Use PyG Batch
    batch_data = Batch.from_data_list(data_list)
    targets_batch = torch.stack(targets)
    
    return batch_data, targets_batch
