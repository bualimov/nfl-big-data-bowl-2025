import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def load_tracking_data():
    """Load tracking data from all available weeks"""
    all_tracking = []
    week = 1
    while True:
        try:
            df = pd.read_csv(f'tracking_week_{week}.csv')
            all_tracking.append(df)
            week += 1
        except FileNotFoundError:
            break
    return pd.concat(all_tracking, ignore_index=True)

def load_plays_data():
    return pd.read_csv('plays.csv')

def load_players_data():
    return pd.read_csv('players.csv')

def normalize_coordinates(x, y, play_direction):
    """Normalize coordinates based on play direction"""
    if play_direction == 'left':
        return 120 - x, 53.3 - y
    return x, y

def get_offensive_position_group(position):
    """Map offensive positions to groups"""
    if position in ['WR', 'TE']:
        return 'Receiver'
    elif position == 'QB':
        return 'QB'
    elif position in ['RB', 'FB', 'HB']:
        return 'Back'
    elif position in ['T', 'G', 'C']:
        return 'OLine'
    return position

def get_defensive_matchup_rules():
    """Define defensive matchup rules for each position"""
    return {
        'CB': ['WR', 'TE'],  # CBs match up with receivers
        'S': ['TE', 'WR', 'RB'],  # Safeties can match with TEs, WRs, or RBs
        'LB': ['RB', 'TE', 'FB'],  # LBs match with backs and TEs
        'DE': ['T'],  # DEs align with tackles
        'DT': ['G', 'C']  # DTs align with guards/center
    }

def find_closest_offensive_player(def_x, def_y, offense_data, valid_positions):
    """Find the closest offensive player from valid matchup positions"""
    min_dist = float('inf')
    closest_player = None
    
    for _, off_player in offense_data.iterrows():
        if off_player.position in valid_positions:
            dist = np.sqrt((def_x - off_player.x)**2 + (def_y - off_player.y)**2)
            if dist < min_dist:
                min_dist = dist
                closest_player = off_player
    
    return closest_player, min_dist

def determine_specific_position(player_pos, x, y, ball_y, offense_data):
    """Determine specific alignment of defensive player"""
    matchup_rules = get_defensive_matchup_rules()
    valid_positions = matchup_rules.get(player_pos, [])
    
    if player_pos in ['CB', 'DB']:
        # Find closest receiver
        closest_player, _ = find_closest_offensive_player(x, y, offense_data, ['WR', 'TE'])
        if closest_player is not None:
            # Determine left/right based on player's position relative to ball
            return f"{'Left' if y < ball_y else 'Right'} CB"
    elif player_pos == 'S':
        # Determine safety type based on position relative to ball
        return f"{'Free' if y < ball_y else 'Strong'} Safety"
    elif player_pos == 'LB':
        if abs(y - ball_y) < 2:
            return 'MLB'
        # Determine left/right based on player's position relative to ball
        return f"{'Left' if y < ball_y else 'Right'} LB"
    elif player_pos == 'DE':
        # Determine left/right based on player's position relative to ball
        return f"{'Left' if y < ball_y else 'Right'} DE"
    elif player_pos == 'DT':
        # Determine left/right based on player's position relative to ball
        return f"{'Left' if y < ball_y else 'Right'} DT"
    
    return player_pos

def get_minimum_defensive_distance(position):
    """Get minimum allowed distance from line of scrimmage based on position"""
    base_distance = 1.0
    
    if position.endswith('CB'):
        return base_distance
    elif position.endswith('Safety'):
        return 7.0
    elif position.endswith('LB') or position == 'MLB':
        return 3.0
    elif position.endswith('DE') or position.endswith('DT'):
        return base_distance
    return base_distance

def is_successful_defense(play_info):
    """Determine if a defensive play was successful based on overall defensive performance"""
    # For passing plays
    if pd.notna(play_info.passResult):
        # Consider incomplete passes, interceptions, and sacks as successful
        if play_info.passResult in ['I', 'IN', 'S']:
            return True
        # For complete passes, consider it successful if gain was limited
        if play_info.passResult == 'C':
            return play_info.yardsGained <= 3  # Stricter threshold for pass defense success
    
    # For running plays, consider it successful if gain was limited
    return play_info.yardsGained <= 2

def adjust_position_to_legal(x_rel, y_rel, position, closest_off_player=None):
    """Adjust position to ensure it's legal and properly spaced"""
    min_distance = get_minimum_defensive_distance(position)
    x_rel = max(x_rel, min_distance)
    
    if closest_off_player is not None:
        # Adjust based on matchup
        if position.endswith('DE'):
            # DEs should be outside the tackle
            y_rel = y_rel + (1.0 if 'Right' in position else -1.0)
        elif position.endswith('DT'):
            # DTs should be in gaps
            y_rel = y_rel + (0.5 if 'Right' in position else -0.5)
    
    if position.endswith('Safety'):
        x_rel = max(x_rel, 7.0)
    elif position.endswith('LB') or position == 'MLB':
        x_rel = np.clip(x_rel, 3.0, 5.0)
    elif position.endswith('DE') or position.endswith('DT'):
        x_rel = np.clip(x_rel, 1.0, 2.0)
    elif position.endswith('CB'):
        x_rel = np.clip(x_rel, 1.0, 7.0)
    
    return x_rel, y_rel

def analyze_pre_snap_tendencies(tracking_df, plays_df, players_df):
    """Analyze pre-snap defensive tendencies"""
    # Get pre-snap frames
    pre_snap_data = tracking_df[tracking_df.frameType == 'before']
    
    # Analyze player movement before snap
    motion_analysis = pre_snap_data.groupby(['gameId', 'playId', 'nflId']).agg({
        's': ['mean', 'max'],  # Speed
        'a': ['mean', 'max'],  # Acceleration
        'dis': 'sum',  # Total distance traveled
        'o': ['mean', 'std'],  # Orientation
        'dir': ['mean', 'std']  # Direction
    }).reset_index()
    
    # Rename columns for clarity
    motion_analysis.columns = ['gameId', 'playId', 'nflId', 
                             'avg_speed', 'max_speed',
                             'avg_accel', 'max_accel',
                             'total_distance',
                             'avg_orientation', 'orientation_var',
                             'avg_direction', 'direction_var']
    
    return motion_analysis

def calculate_optimal_positions(tracking_df, plays_df, players_df, formation, alignment, is_passing_play=False):
    """Calculate optimal defensive positions considering pre-snap tendencies"""
    print(f"\nCalculating optimal positions for {formation} formation, {alignment} alignment")
    
    # Filter plays by formation and alignment
    formation_plays = plays_df[
        (plays_df.offenseFormation == formation) &
        (plays_df.receiverAlignment == alignment)
    ]
    
    if is_passing_play:
        formation_plays = formation_plays[formation_plays.passResult.notna()]
    
    # Find plays where the defense as a whole was successful
    successful_plays = formation_plays[formation_plays.apply(is_successful_defense, axis=1)]
    
    if len(successful_plays) == 0:
        print(f"No successful defensive plays found for {formation} formation")
        return None
    
    print(f"Found {len(successful_plays)} successful defensive plays")
    
    # Analyze pre-snap tendencies
    pre_snap_analysis = analyze_pre_snap_tendencies(tracking_df, successful_plays, players_df)
    
    # Dictionary to store positions for each successful play
    play_positions = []
    matchup_rules = get_defensive_matchup_rules()
    
    print("\nAnalyzing defensive positions in successful plays:")
    for _, play in successful_plays.iterrows():
        play_data = tracking_df[
            (tracking_df.gameId == play.gameId) &
            (tracking_df.playId == play.playId) &
            (tracking_df.event == 'ball_snap')
        ]
        
        if play_data.empty:
            continue
            
        play_data = play_data.merge(players_df[['nflId', 'position']], on='nflId', how='left')
        
        ball_data = play_data[play_data.nflId.isna()].iloc[0]
        offense_data = play_data[play_data.club == play.possessionTeam]
        defense_data = play_data[play_data.club == play.defensiveTeam]
        
        # Print play details
        print(f"\nPlay {play.playId}:")
        print(f"Play direction: {ball_data.playDirection}")
        print(f"Ball position: x={ball_data.x:.2f}, y={ball_data.y:.2f}")
        print(f"Yards gained: {play.yardsGained}")
        if pd.notna(play.passResult):
            print(f"Pass result: {play.passResult}")
        
        # Analyze each defensive player
        for _, def_player in defense_data.iterrows():
            specific_pos = determine_specific_position(def_player.position, def_player.x, def_player.y, ball_data.y, offense_data)
            
            # Get pre-snap tendencies for this player
            player_tendencies = pre_snap_analysis[
                (pre_snap_analysis.gameId == play.gameId) &
                (pre_snap_analysis.playId == play.playId) &
                (pre_snap_analysis.nflId == def_player.nflId)
            ]
            
            # Calculate relative position
            x_rel = def_player.x - ball_data.x
            y_rel = def_player.y - ball_data.y
            
            # Find closest offensive player for matchup
            closest_off, dist = find_closest_offensive_player(def_player.x, def_player.y, offense_data, matchup_rules.get(def_player.position, []))
            
            # Store position data with movement metrics
            position_data = {
                'defensive_position': specific_pos,
                'x_rel': x_rel,
                'y_rel': y_rel,
                'formation': formation,
                'alignment': alignment,
                'matchup_position': closest_off.position if closest_off is not None else None,
                'avg_speed': player_tendencies.avg_speed.iloc[0] if not player_tendencies.empty else 0,
                'max_speed': player_tendencies.max_speed.iloc[0] if not player_tendencies.empty else 0,
                'total_distance': player_tendencies.total_distance.iloc[0] if not player_tendencies.empty else 0
            }
            
            play_positions.append(position_data)
            
            # Print position details
            print(f"{specific_pos} ({def_player.jerseyNumber}) {'matched with ' + closest_off.position + ' ' + str(closest_off.jerseyNumber) if closest_off is not None else 'positioned relative to ball'}")
            print(f"Relative position: x={x_rel:.2f}, y={y_rel:.2f}")
            if not player_tendencies.empty:
                print(f"Pre-snap movement - Avg speed: {position_data['avg_speed']:.2f}, Max speed: {position_data['max_speed']:.2f}, Total distance: {position_data['total_distance']:.2f}")
            
            # Adjust position to be legal
            x_rel, y_rel = adjust_position_to_legal(x_rel, y_rel, specific_pos, closest_off)
            print(f"Adjusted position: x={x_rel:.2f}, y={y_rel:.2f}")
    
    if not play_positions:
        print("No valid positions calculated")
        return None
    
    # Convert to DataFrame and calculate statistics
    positions_df = pd.DataFrame(play_positions)
    
    # Print statistics for each defensive position
    for pos in positions_df.defensive_position.unique():
        pos_data = positions_df[positions_df.defensive_position == pos]
        print(f"\n{pos} Statistics:")
        print(f"Number of samples: {len(pos_data)}")
        print(f"Average x_rel: {pos_data.x_rel.mean():.2f}")
        print(f"Average y_rel: {pos_data.y_rel.mean():.2f}")
        print(f"Standard deviation x_rel: {pos_data.x_rel.std():.2f}")
        print(f"Standard deviation y_rel: {pos_data.y_rel.std():.2f}")
        print(f"Average pre-snap speed: {pos_data.avg_speed.mean():.2f}")
        print(f"Average total pre-snap movement: {pos_data.total_distance.mean():.2f}")
    
    # Calculate optimal positions
    optimal_positions = positions_df.groupby('defensive_position').agg({
        'x_rel': 'mean',
        'y_rel': 'mean',
        'formation': 'first',
        'alignment': 'first',
        'matchup_position': lambda x: x.value_counts().index[0] if len(x.value_counts()) > 0 else None,
        'avg_speed': 'mean',
        'total_distance': 'mean'
    }).reset_index()
    
    print(f"\nCalculated optimal positions for {len(optimal_positions)} defensive positions")
    print("\nOptimal positions:")
    print(optimal_positions[['defensive_position', 'x_rel', 'y_rel', 'matchup_position', 'avg_speed', 'total_distance']])
    
    return optimal_positions

def find_valid_play(tracking_df, plays_df, is_passing_play=False):
    """Find a valid play in the tracking data"""
    print("Looking for a valid play...")
    
    tracking_plays = tracking_df[tracking_df.event == 'ball_snap'][['gameId', 'playId']].drop_duplicates()
    valid_plays = tracking_plays.merge(plays_df, on=['gameId', 'playId'])
    
    if is_passing_play:
        valid_plays = valid_plays[valid_plays.passResult.notna()]
        print("Filtering for passing plays...")
    
    if valid_plays.empty:
        raise ValueError("No valid plays found in tracking data!")
    
    valid_play = valid_plays.iloc[0]
    print(f"Found valid play: {valid_play.playId} from game {valid_play.gameId}")
    print(f"Play type: {'Passing' if is_passing_play else 'Any'}")
    return valid_play.gameId, valid_play.playId

def analyze_defensive_positions(is_passing_play=False):
    """Analyze defensive positions relative to offensive formations"""
    print("Loading tracking data from all weeks...")
    tracking_df = load_tracking_data()
    plays_df = load_plays_data()
    players_df = load_players_data()
    
    print(f"Loaded {len(tracking_df)} tracking records")
    print(f"Loaded {len(plays_df)} plays")
    print(f"Loaded {len(players_df)} players")
    
    os.makedirs('step234', exist_ok=True)
    
    game_id, play_id = find_valid_play(tracking_df, plays_df, is_passing_play)
    play_info = plays_df[(plays_df.gameId == game_id) & (plays_df.playId == play_id)].iloc[0]
    
    print(f"\nAnalyzing play {play_id} from game {game_id}")
    print(f"Formation: {play_info.offenseFormation}")
    print(f"Alignment: {play_info.receiverAlignment}")
    
    optimal_positions = calculate_optimal_positions(
        tracking_df, plays_df, players_df,
        play_info.offenseFormation,
        play_info.receiverAlignment,
        is_passing_play
    )
    
    if optimal_positions is not None:
        output_file = 'step234/optimal_defensive_positions_pass.csv' if is_passing_play else 'step234/optimal_defensive_positions.csv'
        optimal_positions.to_csv(output_file, index=False)
        
        # Create visualization
        plt.figure(figsize=(15, 10))
        plt.grid(True)
        
        # Plot field boundaries
        plt.axhline(y=0, color='k', linestyle='-')
        plt.axhline(y=53.3, color='k', linestyle='-')
        plt.axvline(x=0, color='k', linestyle='-')
        plt.axvline(x=120, color='k', linestyle='-')
        
        # Plot optimal defensive positions
        scatter = plt.scatter(optimal_positions.x_rel, optimal_positions.y_rel, 
                            c=optimal_positions.avg_speed, cmap='viridis', 
                            s=100 * (1 + optimal_positions.total_distance/optimal_positions.total_distance.max()))
        
        # Add labels for each position
        for _, pos in optimal_positions.iterrows():
            plt.annotate(f"{pos.defensive_position}\n(s={pos.avg_speed:.1f})", 
                        (pos.x_rel, pos.y_rel),
                        xytext=(5, 5), textcoords='offset points')
        
        plt.colorbar(scatter, label='Average Pre-snap Speed (yards/s)')
        plt.title(f'Optimal Defensive Positions - {play_info.offenseFormation} Formation\nMarker size indicates total pre-snap movement')
        plt.xlabel('Yards from Line of Scrimmage')
        plt.ylabel('Yards from Center')
        
        # Save the plot
        plt.savefig('step234/defensive_positions.png')
        plt.close()
        
        return optimal_positions
    else:
        raise ValueError("No valid optimal positions calculated!")

if __name__ == "__main__":
    print("\nAnalyzing passing play...")
    analyze_defensive_positions(is_passing_play=True) 