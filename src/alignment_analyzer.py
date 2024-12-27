import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

class DefensiveAlignmentAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def calculate_alignment_features(self, pre_snap_df):
        """
        Calculate features that characterize defensive alignments
        
        Args:
            pre_snap_df: DataFrame containing pre-snap defensive positions
        """
        features = {}
        
        # Box count (players within 8 yards of LOS)
        features['box_count'] = len(pre_snap_df[pre_snap_df['y'].abs() <= 8])
        
        # Distance from LOS stats
        los_distances = pre_snap_df['y'].abs()
        features.update({
            'avg_los_distance': los_distances.mean(),
            'std_los_distance': los_distances.std(),
            'max_los_distance': los_distances.max()
        })
        
        # Horizontal spread stats
        x_positions = pre_snap_df['x']
        features.update({
            'defensive_width': x_positions.max() - x_positions.min(),
            'x_std': x_positions.std()
        })
        
        return features
    
    def identify_formation_type(self, pre_snap_df):
        """
        Identify the type of defensive formation
        
        Args:
            pre_snap_df: DataFrame containing pre-snap defensive positions
        """
        # Count players in different zones
        box_players = len(pre_snap_df[pre_snap_df['y'].abs() <= 8])
        deep_players = len(pre_snap_df[pre_snap_df['y'].abs() > 8])
        
        # Basic formation classification
        if box_players >= 7:
            return 'Stacked Box'
        elif box_players == 6:
            return 'Standard'
        else:
            return 'Light Box'
    
    def calculate_defensive_spacing(self, pre_snap_df):
        """
        Calculate spacing metrics for defensive alignment
        
        Args:
            pre_snap_df: DataFrame containing pre-snap defensive positions
        """
        # Calculate pairwise distances between defenders
        positions = pre_snap_df[['x', 'y']].values
        distances = []
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = np.linalg.norm(positions[i] - positions[j])
                distances.append(dist)
        
        return {
            'avg_spacing': np.mean(distances),
            'min_spacing': np.min(distances),
            'max_spacing': np.max(distances),
            'spacing_std': np.std(distances)
        }
    
    def cluster_formations(self, formations_df, n_clusters=5):
        """
        Cluster similar defensive formations
        
        Args:
            formations_df: DataFrame containing formation features
            n_clusters: Number of clusters to identify
        """
        # Select features for clustering
        features = ['box_count', 'avg_los_distance', 'defensive_width', 'avg_spacing']
        X = formations_df[features].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        return clusters 