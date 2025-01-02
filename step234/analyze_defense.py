import pandas as pd
import numpy as np

def load_tracking_data(week):
    return pd.read_csv(f'tracking_week_{week}.csv')

def load_plays():
    return pd.read_csv('plays.csv')

def load_players():
    return pd.read_csv('players.csv')

def get_last_pre_snap_frame(play_data):
    pre_snap = play_data[play_data['frameType'] == 'BEFORE_SNAP']
    if len(pre_snap) == 0:
        return None
    return pre_snap['frameId'].max()

def is_successful_defense(play):
    # Consider a defense successful if:
    # 1. Incomplete pass
    # 2. Pass for less than 3 yards
    # 3. Interception
    # 4. Sack
    if pd.isna(play['passResult']):
        return False
    
    if play['passResult'] in ['I', 'IN']:  # Incomplete or Intercepted
        return True
    
    if play['passResult'] == 'C':  # Complete
        return play['yardsGained'] < 3
    
    if play['passResult'] == 'S':  # Sack
        return True
    
    return False

def calculate_optimal_positions(tracking_data, plays, players):
    successful_plays = []
    
    # Find successful defensive plays
    for _, play in plays.iterrows():
        if is_successful_defense(play):
            play_data = tracking_data[
                (tracking_data['gameId'] == play['gameId']) & 
                (tracking_data['playId'] == play['playId'])
            ]
            
            # Merge with players data
            play_data = play_data.merge(
                players[['nflId', 'position']], 
                on='nflId',
                how='left'
            )
            
            last_frame = get_last_pre_snap_frame(play_data)
            if last_frame:
                frame_data = play_data[play_data['frameId'] == last_frame]
                successful_plays.append(frame_data)
    
    if not successful_plays:
        return None
    
    # Combine all successful plays
    all_successful = pd.concat(successful_plays)
    
    # Calculate optimal positions for each defensive position
    optimal_positions = []
    defensive_positions = ['CB', 'SS', 'FS', 'MLB', 'OLB', 'DE', 'DT']
    
    for position in defensive_positions:
        position_data = all_successful[all_successful['position'] == position]
        if len(position_data) > 0:
            # Calculate average position relative to ball
            avg_x = position_data['x'].mean()
            avg_y = position_data['y'].mean()
            
            # Add some variance to prevent all positions being exactly the same
            x_std = position_data['x'].std()
            y_std = position_data['y'].std()
            
            optimal_positions.append({
                'position': position,
                'x': avg_x,
                'y': avg_y,
                'x_std': x_std,
                'y_std': y_std
            })
    
    return pd.DataFrame(optimal_positions)

def main():
    # Load data
    tracking_data = load_tracking_data(1)
    plays = load_plays()
    players = load_players()
    
    print(f"Loaded {len(tracking_data)} tracking records")
    print(f"Loaded {len(plays)} plays")
    print(f"Loaded {len(players)} players")
    
    # Calculate optimal positions
    optimal_positions = calculate_optimal_positions(tracking_data, plays, players)
    
    if optimal_positions is not None:
        print("\nOptimal defensive positions:")
        print(optimal_positions)
        
        # Save optimal positions
        optimal_positions.to_csv('step234/optimal_defensive_positions.csv', index=False)
    else:
        print("No successful defensive plays found")

if __name__ == "__main__":
    main() 