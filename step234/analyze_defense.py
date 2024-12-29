import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def load_tracking_data(week=1):
    return pd.read_csv(f'tracking_week_{week}.csv')

def load_plays_data():
    return pd.read_csv('plays.csv')

def load_players_data():
    return pd.read_csv('players.csv')

def normalize_coordinates(x, y, play_direction):
    """Normalize coordinates based on play direction"""
    if play_direction == 'left':
        return 120 - x, 53.3 - y
    return x, y

def determine_specific_position(player_pos, x, y, ball_y):
    """Determine specific alignment of defensive player"""
    if player_pos in ['CB', 'DB']:
        return f"{'Left' if y < ball_y else 'Right'} CB"
    elif player_pos == 'S':
        return f"{'Free' if y < ball_y else 'Strong'} Safety"
    elif player_pos == 'LB':
        if abs(y - ball_y) < 2:
            return 'MLB'
        return f"{'Left' if y < ball_y else 'Right'} LB"
    elif player_pos == 'DE':
        return f"{'Left' if y < ball_y else 'Right'} DE"
    elif player_pos == 'DT':
        return f"{'Inside' if abs(y - ball_y) < 2 else ('Left' if y < ball_y else 'Right')} DT"
    return player_pos

def get_relative_positions(tracking_df, plays_df, players_df, play_id, game_id):
    """Get relative positions of defensive players to offensive players"""
    print(f"\nAnalyzing play {play_id} from game {game_id}")
    
    # Get play information
    play_info = plays_df[(plays_df.gameId == game_id) & (plays_df.playId == play_id)].iloc[0]
    print(f"Found play info: {play_info.offenseFormation} formation")
    
    # Filter for the specific play
    play_data = tracking_df[
        (tracking_df.playId == play_id) & 
        (tracking_df.gameId == game_id) &
        (tracking_df.event == 'ball_snap')
    ]
    
    if play_data.empty:
        print("No play data found!")
        return None
    
    # Merge with player information
    play_data = play_data.merge(players_df[['nflId', 'position']], on='nflId', how='left')
    
    print(f"Found {len(play_data)} frames for the play")
    
    # Get ball position
    ball_data = play_data[play_data.nflId.isna()].iloc[0]
    ball_x, ball_y = ball_data.x, ball_data.y
    print(f"Ball position: ({ball_x}, {ball_y})")
    
    # Normalize coordinates based on play direction
    play_direction = ball_data.playDirection
    print(f"Play direction: {play_direction}")
    
    # Get offensive and defensive players
    offense_data = play_data[play_data.club == play_info.possessionTeam]
    defense_data = play_data[play_data.club == play_info.defensiveTeam]
    
    print(f"Found {len(offense_data)} offensive players and {len(defense_data)} defensive players")
    print(f"Possession team: {play_info.possessionTeam}")
    print(f"Defensive team: {play_info.defensiveTeam}")
    print("\nUnique teams in play data:")
    print(play_data.club.unique())
    
    relative_positions = []
    
    for _, def_player in defense_data.iterrows():
        def_x, def_y = normalize_coordinates(def_player.x, def_player.y, play_direction)
        
        # Find closest offensive player
        min_dist = float('inf')
        closest_off = None
        
        for _, off_player in offense_data.iterrows():
            off_x, off_y = normalize_coordinates(off_player.x, off_player.y, play_direction)
            dist = np.sqrt((def_x - off_x)**2 + (def_y - off_y)**2)
            
            if dist < min_dist:
                min_dist = dist
                closest_off = off_player
        
        if closest_off is not None:
            specific_pos = determine_specific_position(def_player.position, def_x, def_y, ball_y)
            relative_positions.append({
                'defensive_position': specific_pos,
                'x_rel': def_x - ball_x,
                'y_rel': def_y - ball_y,
                'distance_to_offense': min_dist,
                'formation': play_info.offenseFormation,
                'alignment': play_info.receiverAlignment
            })
    
    if not relative_positions:
        print("No relative positions calculated!")
        return None
    
    print(f"Calculated {len(relative_positions)} relative positions")
    return pd.DataFrame(relative_positions)

def find_valid_play(tracking_df, plays_df):
    """Find a valid play in the tracking data"""
    print("Looking for a valid play...")
    
    # Get unique game and play IDs in tracking data
    tracking_plays = tracking_df[tracking_df.event == 'ball_snap'][['gameId', 'playId']].drop_duplicates()
    
    # Merge with plays data to get only valid plays
    valid_plays = tracking_plays.merge(plays_df, on=['gameId', 'playId'])
    
    if valid_plays.empty:
        raise ValueError("No valid plays found in tracking data!")
    
    # Return the first valid play
    valid_play = valid_plays.iloc[0]
    print(f"Found valid play: {valid_play.playId} from game {valid_play.gameId}")
    return valid_play.gameId, valid_play.playId

def analyze_defensive_positions():
    """Analyze defensive positions relative to offensive formations"""
    tracking_df = load_tracking_data()
    plays_df = load_plays_data()
    players_df = load_players_data()
    
    print(f"Loaded {len(tracking_df)} tracking records")
    print(f"Loaded {len(plays_df)} plays")
    print(f"Loaded {len(players_df)} players")
    
    # Create output directory if it doesn't exist
    os.makedirs('step234', exist_ok=True)
    
    # Find a valid play
    game_id, play_id = find_valid_play(tracking_df, plays_df)
    
    print(f"\nAnalyzing play {play_id} from game {game_id}")
    
    relative_positions = get_relative_positions(tracking_df, plays_df, players_df, play_id, game_id)
    
    if relative_positions is not None:
        relative_positions.to_csv('step234/optimal_defensive_positions.csv', index=False)
        return relative_positions
    else:
        raise ValueError("No valid relative positions calculated!")

if __name__ == "__main__":
    analyze_defensive_positions() 