import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class DefensiveVisualizer:
    def __init__(self):
        self.field_length = 120
        self.field_width = 53.3
        self.colors = sns.color_palette("husl", 10)
        
    def setup_field(self, ax):
        """Set up football field for plotting"""
        # Field dimensions
        ax.set_xlim(0, self.field_width)
        ax.set_ylim(-10, 10)  # Focus on region around LOS
        
        # Add yard lines
        for y in range(-10, 11, 5):
            ax.axhline(y=y, color='gray', linestyle='-', alpha=0.2)
            
        # Add hash marks
        for x in range(0, int(self.field_width) + 1, 5):
            ax.axvline(x=x, color='gray', linestyle='-', alpha=0.2)
            
        ax.set_xlabel('Field Width (yards)')
        ax.set_ylabel('Distance from LOS (yards)')
        
    def plot_defensive_alignment(self, pre_snap_df, title=None):
        """
        Plot defensive alignment for a single play
        
        Args:
            pre_snap_df: DataFrame containing pre-snap positions
            title: Optional title for the plot
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        self.setup_field(ax)
        
        # Plot defenders
        ax.scatter(pre_snap_df['x'], pre_snap_df['y'], 
                  c='red', s=100, label='Defenders')
        
        if title:
            ax.set_title(title)
        ax.legend()
        
        return fig
    
    def plot_formation_distribution(self, formation_counts):
        """
        Plot distribution of defensive formations
        
        Args:
            formation_counts: Series containing formation counts
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        formation_counts.plot(kind='bar', ax=ax)
        ax.set_title('Distribution of Defensive Formations')
        ax.set_xlabel('Formation Type')
        ax.set_ylabel('Count')
        plt.xticks(rotation=45)
        
        return fig
    
    def plot_versatility_radar(self, versatility_metrics):
        """
        Create radar plot of versatility metrics
        
        Args:
            versatility_metrics: Dict containing versatility components
        """
        # Prepare data
        categories = ['Formation Variety', 'Spacing Versatility', 'Formation Transitions']
        values = [
            versatility_metrics['formation_entropy'],
            versatility_metrics['spacing_versatility'],
            versatility_metrics['transition_rate']
        ]
        
        # Create radar plot
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        values = np.concatenate((values, [values[0]]))  # complete the loop
        angles = np.concatenate((angles, [angles[0]]))  # complete the loop
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title('Defensive Versatility Breakdown')
        
        return fig
    
    def plot_spacing_distribution(self, spacing_metrics):
        """
        Plot distribution of defensive spacing metrics
        
        Args:
            spacing_metrics: DataFrame containing spacing metrics
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(data=spacing_metrics, x='avg_spacing', bins=30, ax=ax)
        ax.set_title('Distribution of Average Defensive Spacing')
        ax.set_xlabel('Average Spacing (yards)')
        ax.set_ylabel('Count')
        
        return fig 