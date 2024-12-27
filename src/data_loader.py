import pandas as pd
import numpy as np
from pathlib import Path

class NFLDataLoader:
    def __init__(self, data_dir='.'):
        self.data_dir = Path(data_dir)
        
    def load_tracking_data(self, weeks=None):
        """
        Load tracking data for specified weeks
        
        Args:
            weeks (list): List of week numbers to load. If None, loads all weeks.
        """
        if weeks is None:
            weeks = range(1, 10)
            
        tracking_data = []
        for week in weeks:
            file_path = self.data_dir / f'tracking_week_{week}.csv'
            if file_path.exists():
                df = pd.read_csv(file_path)
                tracking_data.append(df)
                
        return pd.concat(tracking_data, ignore_index=True)
    
    def load_plays(self):
        """Load plays data"""
        return pd.read_csv(self.data_dir / 'plays.csv')
    
    def load_players(self):
        """Load players data"""
        return pd.read_csv(self.data_dir / 'players.csv')
    
    def load_games(self):
        """Load games data"""
        return pd.read_csv(self.data_dir / 'games.csv')
    
    def get_defensive_snapshots(self, tracking_df, plays_df, pre_snap_window=10):
        """
        Extract defensive alignment snapshots before the snap
        
        Args:
            tracking_df: Tracking data DataFrame
            plays_df: Plays data DataFrame
            pre_snap_window: Number of frames before snap to analyze
        """
        # Merge with plays data
        merged_df = tracking_df.merge(plays_df, on=['gameId', 'playId'])
        
        # Filter to defensive players only
        defense_df = merged_df[merged_df['team'] != merged_df['possessionTeam']]
        
        # Get pre-snap frames
        pre_snap = defense_df[defense_df['frameId'].between(
            defense_df['snapFrameId'] - pre_snap_window,
            defense_df['snapFrameId']
        )]
        
        return pre_snap

    def process_defensive_formations(self, pre_snap_df):
        """
        Process defensive formations to extract key metrics
        
        Args:
            pre_snap_df: DataFrame containing pre-snap defensive positions
        """
        # Group by play and frame
        grouped = pre_snap_df.groupby(['gameId', 'playId', 'frameId'])
        
        # Calculate formation characteristics
        formations = grouped.agg({
            'x': ['min', 'max', 'std'],
            'y': ['min', 'max', 'std'],
            'nflId': 'count'
        }).reset_index()
        
        return formations 