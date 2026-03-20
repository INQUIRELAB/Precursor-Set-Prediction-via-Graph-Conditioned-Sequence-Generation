"""
Data schema for solid-state synthesis reactions.

Defines canonical data structures for representing reactions,
targets, and precursors.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import re


@dataclass
class Reaction:
    """Canonical representation of a solid-state synthesis reaction."""
    
    target_formula: str
    precursor_formulas: List[str]
    doi: str
    reaction_string: Optional[str] = None
    target_mp_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        # Normalize formulas (remove whitespace)
        self.target_formula = self.target_formula.strip()
        self.precursor_formulas = [p.strip() for p in self.precursor_formulas]
        
        # Sort precursors for consistency
        self.precursor_formulas = sorted(set(self.precursor_formulas))
    
    def is_valid(self) -> bool:
        """Check if the reaction has valid data."""
        if not self.target_formula:
            return False
        if not self.precursor_formulas or len(self.precursor_formulas) == 0:
            return False
        if not all(self._is_valid_formula(f) for f in [self.target_formula] + self.precursor_formulas):
            return False
        return True
    
    @staticmethod
    def _is_valid_formula(formula: str) -> bool:
        """Check if a chemical formula is valid (simple heuristic)."""
        if not formula or len(formula) == 0:
            return False
        # Check for basic chemical formula pattern (elements + numbers)
        # Allow uppercase letter followed by optional lowercase, optional numbers
        pattern = r'^([A-Z][a-z]?\d*\.?\d*)+$'
        return bool(re.match(pattern, formula))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'target_formula': self.target_formula,
            'precursor_formulas': self.precursor_formulas,
            'doi': self.doi,
            'reaction_string': self.reaction_string,
            'target_mp_id': self.target_mp_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reaction':
        """Create from dictionary."""
        return cls(
            target_formula=data['target_formula'],
            precursor_formulas=data['precursor_formulas'],
            doi=data['doi'],
            reaction_string=data.get('reaction_string'),
            target_mp_id=data.get('target_mp_id')
        )


def parse_dataset1_reaction(entry: Dict[str, Any]) -> Optional[Reaction]:
    """Parse reaction from SS_rxns_80806.json format."""
    try:
        # Extract target
        if not entry.get('target') or len(entry['target']) == 0:
            return None
        target = entry['target'][0]
        target_formula = target.get('material_formula', '')
        target_mp_id = target.get('mp_id')
        
        # Extract precursors
        precursors = entry.get('precursors', [])
        precursor_formulas = [p.get('material_formula', '') for p in precursors]
        precursor_formulas = [f for f in precursor_formulas if f]  # Remove empty
        
        # Extract reaction string
        target_reaction = entry.get('target_reaction', [])
        reaction_string = target_reaction[0][-1] if target_reaction and len(target_reaction[0]) > 0 else None
        
        # DOI
        doi = entry.get('DOI', '')
        
        reaction = Reaction(
            target_formula=target_formula,
            precursor_formulas=precursor_formulas,
            doi=doi,
            reaction_string=reaction_string,
            target_mp_id=target_mp_id
        )
        
        return reaction if reaction.is_valid() else None
        
    except Exception as e:
        return None


def parse_dataset2_reaction(entry: Dict[str, Any]) -> Optional[Reaction]:
    """Parse reaction from solid-state_dataset_2019-06-27_upd.json format."""
    try:
        # Extract target
        target = entry.get('target', {})
        target_formula = target.get('material_formula', '')
        target_mp_id = target.get('mp_id')
        
        # Extract precursors
        precursors = entry.get('precursors', [])
        precursor_formulas = [p.get('material_formula', '') for p in precursors]
        precursor_formulas = [f for f in precursor_formulas if f]  # Remove empty
        
        # Extract reaction string
        reaction_string = entry.get('reaction_string')
        
        # DOI
        doi = entry.get('doi', '')
        
        reaction = Reaction(
            target_formula=target_formula,
            precursor_formulas=precursor_formulas,
            doi=doi,
            reaction_string=reaction_string,
            target_mp_id=target_mp_id
        )
        
        return reaction if reaction.is_valid() else None
        
    except Exception as e:
        return None
