"""
PyTorch Dataset for GemNet Precursor Prediction.
Loads structures from CIFs and precursor targets from parquet.
"""

import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from pathlib import Path
from pymatgen.core import Structure
import warnings

# Try identifying available GemNet/OCP dependencies
try:
    from torch_geometric.data import Data, Batch
    HAS_PYG = True
except ImportError:
    HAS_PYG = False
    
try:
    from fairchem.core.common.utils import radius_graph_pbc
    from fairchem.core.preprocessing import AtomsToGraphs
    from fairchem.core.datasets import data_list_collater
    HAS_OCP = True
except ImportError:
    HAS_OCP = False

from src.features.gemnet_embed import GemNetEmbedder

class GemNetPrecursorDataset(Dataset):
    def __init__(self, metadata_file, vocab_size=500, cutoff=6.0, max_neighbors=50):
        """
        Args:
            metadata_file (str/Path): Path to gemnet_training_data.parquet
            vocab_size (int): Expected vocabulary size
            cutoff (float): Radius cutoff for graph construction
            max_neighbors (int): Max neighbors for graph construction
        """
        self.metadata_file = Path(metadata_file)
        self.vocab_size = vocab_size
        
        # Load metadata
        print(f"Loading dataset from {self.metadata_file}...")
        self.df = pd.read_parquet(self.metadata_file)
        
        # Filter out missing CIFs just in case (though we did it in build step)
        self.df = self.df[self.df['cif_path'].notna()]
        print(f"Loaded {len(self.df)} samples.")
        
        # Reuse GemNetEmbedder for graph conversion logic
        # Pass dummy args since we only want _structure_to_graph
        self.embedder = GemNetEmbedder(device='cpu', cutoff=cutoff, max_neighbors=max_neighbors)
        
        # Base dir for relative CIF paths
        from src.config import BASE_DIR
        self.base_dir = BASE_DIR

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        
        # 1. Load Structure
        cif_path = self.base_dir / row['cif_path']
        try:
            structure = Structure.from_file(cif_path)
        except Exception:
            # Return None or handle error. returning None requires custom collate handling
            # Ideally we filtered these out.
            # Create dummy structure?
            # Let's creating a tiny stub if fail
            structure = Structure(
                lattice=[[3,0,0],[0,3,0],[0,0,3]],
                species=['H'],
                coords=[[0,0,0]]
            )
            
        # 2. Convert to Graph (AtomicData)
        try:
            # We access the internal method. 
            # Ideally this logic should be public but this is expedient.
            data = self.embedder._structure_to_graph(structure)
        except Exception as e:
            # Fallback
            print(f"Graph conversion failed for {cif_path}: {e}")
            data = self.embedder._structure_to_graph(
                Structure([[3,0,0],[0,3,0],[0,0,3]], ['H'], [[0,0,0]])
            )
            
        # 3. Create Target Vector (Multi-hot)
        target = torch.zeros(self.vocab_size, dtype=torch.float32)
        indices = row['precursor_indices']
        
        if isinstance(indices, list):
            for i in indices:
                if 0 <= i < self.vocab_size:
                    target[i] = 1.0
        elif isinstance(indices, np.ndarray):
            for i in indices:
                if 0 <= i < self.vocab_size:
                    target[i] = 1.0
                    
        return data, target

def collate_graphs(batch):
    """
    Collate function for OCP/GemNet graphs.
    """
    # batch is list of (data, target) tuples
    data_list = [item[0] for item in batch]
    targets = [item[1] for item in batch]
    
    # Batch the targets
    targets_batch = torch.stack(targets)
    
    # Batch the graphs using PyG/OCP method
    if HAS_PYG:
        batch_data = Batch.from_data_list(data_list)
    else:
        # Fallback if PyG not found (unlikely if strictly using OCP deps)
        # Assuming OCP provides collator
        from fairchem.core.datasets import data_list_collater
        batch_data = data_list_collater(data_list)
        
    return batch_data, targets_batch
