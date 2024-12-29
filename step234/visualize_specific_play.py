import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Field dimensions
FIELD_LENGTH = 120  # includes end zones
FIELD_WIDTH = 53.3

def load_tracking_data(week=1):
    return pd.read_csv(f'tracking_week_{week}.csv')

def load_plays_data():
    return pd.read_csv('plays.csv')

def load_players_data():
    return pd.read_csv('players.csv')

def draw_football_field(ax):
    """Draw a football field on the given axes"""
    # Draw the main field rectangle
    ax.plot([0, FIELD_LENGTH], [0, 0], 'white')
    ax.plot([0, FIELD_LENGTH], [FIELD_WIDTH, FIELD_WIDTH], 'white')
    ax.plot([0, 0], [0, FIELD_WIDTH], 'white')
    ax.plot([FIELD_LENGTH, FIELD_LENGTH], [0, FIELD_WIDTH], 'white')
    
    # Draw yard lines
    for yard in range(10, FIELD_LENGTH-9, 10):
        ax.plot([yard, yard], [0, FIELD_WIDTH], 'white', alpha=0.3)
        # Add yard numbers
        ax.text(yard, 2, str((yard-10)//10), color='white', ha='center')
        ax.text(yard, FIELD_WIDTH-2, str((yard-10)//10), color='white', ha='center')
    
    # Set field color
    ax.set_facecolor('darkgreen')
    
    # Set aspect ratio to equal
    ax.set_aspect('equal')
    
    # Set limits
    ax.set_xlim(-5, FIELD_LENGTH+5)
    ax.set_ylim(-5, FIELD_WIDTH+5)
    
    return ax

def find_valid_play(tracking_df, plays_df, is_passing_play=False):
    """Find a valid play in the tracking data"""
    print("Looking for a valid play...")
    
    # Get unique game and play IDs in tracking data
    tracking_plays = tracking_df[tracking_df.event == 'ball_snap'][['gameId', 'playId']].drop_duplicates()
    
    # Merge with plays data to get only valid plays
    valid_plays = tracking_plays.merge(plays_df, on=['gameId', 'playId'])
    
    if is_passing_play:
        # Filter for passing plays (where passResult is not null)
        valid_plays = valid_plays[valid_plays.passResult.notna()]
        print("Filtering for passing plays...")
    
    if valid_plays.empty:
        raise ValueError("No valid plays found in tracking data!")
    
    # Return the first valid play
    valid_play = valid_plays.iloc[0]
    print(f"Found valid play: {valid_play.playId} from game {valid_play.gameId}")
    print(f"Play type: {'Passing' if is_passing_play else 'Any'}")
    return valid_play.gameId, valid_play.playId

def visualize_play(play_id, game_id, is_passing_play=False, optimal_only=False):
    """Visualize specific play with offensive and defensive positions"""
    tracking_df = load_tracking_data()
    plays_df = load_plays_data()
    players_df = load_players_data()
    optimal_positions_file = 'step234/optimal_defensive_positions_pass.csv' if is_passing_play else 'step234/optimal_defensive_positions.csv'
    optimal_positions = pd.read_csv(optimal_positions_file)
    
    # Get play data at snap
    play_data = tracking_df[
        (tracking_df.playId == play_id) & 
        (tracking_df.gameId == game_id) &
        (tracking_df.event == 'ball_snap')
    ]
    
    if play_data.empty:
        raise ValueError("Play not found!")
    
    # Merge with player information
    play_data = play_data.merge(players_df[['nflId', 'position']], on='nflId', how='left')
    
    # Get play information
    play_info = plays_df[(plays_df.gameId == game_id) & (plays_df.playId == play_id)].iloc[0]
    
    # Create figure
    plt.figure(figsize=(20, 10))
    ax = plt.gca()
    
    # Draw the field
    draw_football_field(ax)
    
    # Get ball position and teams
    ball_data = play_data[play_data.nflId.isna()].iloc[0]
    offense_data = play_data[play_data.club == play_info.possessionTeam]
    defense_data = play_data[play_data.club == play_info.defensiveTeam]
    
    # Plot offensive players (red)
    ax.scatter(offense_data.x, offense_data.y, color='red', s=100, label='Offense')
    for _, player in offense_data.iterrows():
        ax.annotate(f"{player.position} ({player.jerseyNumber})", 
                   (player.x, player.y),
                   xytext=(5, 5), textcoords='offset points', 
                   color='white', fontsize=8)
    
    # Plot actual defensive players (blue) if not optimal_only
    if not optimal_only:
        ax.scatter(defense_data.x, defense_data.y, color='blue', s=100, label='Defense (Actual)')
        for _, player in defense_data.iterrows():
            ax.annotate(f"{player.position} ({player.jerseyNumber})", 
                       (player.x, player.y),
                       xytext=(5, -5), textcoords='offset points', 
                       color='white', fontsize=8)
    
    # Plot optimal defensive positions (cyan)
    for _, pos in optimal_positions.iterrows():
        if pd.notna(pos.matchup_position):
            # Find the corresponding offensive player
            off_player = offense_data[offense_data.position == pos.matchup_position].iloc[0]
            # Account for play direction
            if ball_data.playDirection == 'left':
                opt_x = off_player.x - pos.x_rel
                opt_y = off_player.y - pos.y_rel
            else:
                opt_x = off_player.x + pos.x_rel
                opt_y = off_player.y + pos.y_rel
        else:
            # Account for play direction
            if ball_data.playDirection == 'left':
                opt_x = ball_data.x - pos.x_rel
                opt_y = ball_data.y - pos.y_rel
            else:
                opt_x = ball_data.x + pos.x_rel
                opt_y = ball_data.y + pos.y_rel
        
        ax.scatter(opt_x, opt_y, color='cyan' if not optimal_only else 'blue', s=100, alpha=0.8)
        ax.annotate(f"{pos.defensive_position}", 
                   (opt_x, opt_y),
                   xytext=(5, 5), textcoords='offset points', 
                   color='cyan' if not optimal_only else 'white', fontsize=8)
    
    # Plot ball
    ax.scatter(ball_data.x, ball_data.y, color='brown', s=80, label='Ball')
    
    # Add play direction arrow
    arrow_x = ball_data.x
    arrow_dx = 5 if ball_data.playDirection == 'right' else -5
    ax.arrow(arrow_x, FIELD_WIDTH-5, arrow_dx, 0, head_width=1, head_length=1,
             fc='white', ec='white', label='Play Direction')
    
    # Add legend
    ax.legend(loc='upper right', fontsize=8)
    
    # Set title
    play_type = "Passing Play" if is_passing_play else "Regular Play"
    title = f"{play_type} - Play {play_id} - {play_info.offenseFormation} Formation\n{play_info.playDescription}"
    if not optimal_only:
        title += "\nActual (Blue) vs Optimal (Cyan) Defensive Positions"
    else:
        title += "\nOptimal Defensive Positions"
    plt.title(title, fontsize=10)
    
    # Zoom in on the relevant area
    margin = 5  # yards of margin around the players
    x_min = min(min(offense_data.x), min(defense_data.x)) - margin
    x_max = max(max(offense_data.x), max(defense_data.x)) + margin
    y_min = min(min(offense_data.y), min(defense_data.y)) - margin
    y_max = max(max(offense_data.y), max(defense_data.y)) + margin
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    
    # Save the plot
    base_name = 'play_pass_analysis' if is_passing_play else 'play_regular_analysis'
    suffix = '_optimal_only' if optimal_only else ''
    output_file = f'step234/{base_name}{suffix}.png'
    plt.savefig(output_file, bbox_inches='tight', dpi=300, facecolor='darkgreen')
    plt.close()

if __name__ == "__main__":
    # Find and visualize both a regular play and a passing play
    tracking_df = load_tracking_data()
    plays_df = load_plays_data()
    
    print("\nProcessing regular play...")
    game_id, play_id = find_valid_play(tracking_df, plays_df, is_passing_play=False)
    visualize_play(play_id, game_id, is_passing_play=False)
    
    print("\nProcessing passing play...")
    game_id, play_id = find_valid_play(tracking_df, plays_df, is_passing_play=True)
    visualize_play(play_id, game_id, is_passing_play=True)
    
    # Create optimal-only version of the passing play
    print("\nCreating optimal-only version of passing play...")
    visualize_play(play_id, game_id, is_passing_play=True, optimal_only=True) 