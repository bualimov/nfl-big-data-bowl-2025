import numpy as np
import pandas as pd
from scipy.stats import entropy

class VersatilityMetrics:
    def __init__(self):
        self.formation_weights = {
            'Stacked Box': 1.0,
            'Standard': 1.0,
            'Light Box': 1.0
        }
        
    def calculate_formation_entropy(self, formation_counts):
        """
        Calculate entropy-based measure of formation variety
        
        Args:
            formation_counts: Series or dict containing formation counts
        """
        probs = np.array(list(formation_counts.values)) / sum(formation_counts.values)
        return entropy(probs)
    
    def calculate_spacing_versatility(self, spacing_metrics):
        """
        Calculate versatility score based on defensive spacing
        
        Args:
            spacing_metrics: DataFrame containing spacing metrics for multiple plays
        """
        # Calculate coefficient of variation for spacing metrics
        cv_avg = spacing_metrics['avg_spacing'].std() / spacing_metrics['avg_spacing'].mean()
        cv_std = spacing_metrics['spacing_std'].std() / spacing_metrics['spacing_std'].mean()
        
        # Combine into single metric
        return (cv_avg + cv_std) / 2
    
    def calculate_alignment_transitions(self, formations_df):
        """
        Calculate how often the defense changes formations
        
        Args:
            formations_df: DataFrame containing formation types by play
        """
        transitions = 0
        prev_formation = None
        
        for formation in formations_df['formation_type']:
            if prev_formation is not None and formation != prev_formation:
                transitions += 1
            prev_formation = formation
            
        return transitions / len(formations_df)
    
    def calculate_versatility_index(self, team_stats):
        """
        Calculate overall defensive versatility index
        
        Args:
            team_stats: Dict containing various defensive metrics
        """
        # Normalize each component
        formation_variety = self.calculate_formation_entropy(team_stats['formation_counts'])
        spacing_variety = self.calculate_spacing_versatility(team_stats['spacing_metrics'])
        transition_rate = self.calculate_alignment_transitions(team_stats['formations'])
        
        # Combine into single index (0-100 scale)
        weights = [0.4, 0.3, 0.3]  # Adjustable weights
        components = [formation_variety, spacing_variety, transition_rate]
        
        # Normalize to 0-100 scale
        raw_index = np.dot(weights, components)
        return (raw_index / np.max([1, raw_index])) * 100
    
    def get_versatility_breakdown(self, team_stats):
        """
        Get detailed breakdown of versatility metrics
        
        Args:
            team_stats: Dict containing various defensive metrics
        """
        return {
            'formation_entropy': self.calculate_formation_entropy(team_stats['formation_counts']),
            'spacing_versatility': self.calculate_spacing_versatility(team_stats['spacing_metrics']),
            'transition_rate': self.calculate_alignment_transitions(team_stats['formations']),
            'overall_index': self.calculate_versatility_index(team_stats)
        } 