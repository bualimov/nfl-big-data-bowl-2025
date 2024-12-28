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

def visualize_play(play_id, game_id):
    """Visualize specific play with offensive and defensive positions"""
    tracking_df = load_tracking_data()
    plays_df = load_plays_data()
    players_df = load_players_data()
    optimal_positions = pd.read_csv('step234/optimal_defensive_positions.csv')
    
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
        ax.annotate(player.position, (player.x, player.y), 
                   xytext=(5, 5), textcoords='offset points', color='white')
    
    # Plot actual defensive players (blue)
    ax.scatter(defense_data.x, defense_data.y, color='blue', s=100, label='Defense (Actual)')
    for _, player in defense_data.iterrows():
        ax.annotate(player.position, (player.x, player.y), 
                   xytext=(5, -5), textcoords='offset points', color='white')
    
    # Plot optimal defensive positions (cyan)
    for _, pos in optimal_positions.iterrows():
        opt_x = ball_data.x + pos.x_rel
        opt_y = ball_data.y + pos.y_rel
        ax.scatter(opt_x, opt_y, color='cyan', s=100, alpha=0.5)
        ax.annotate(f"{pos.defensive_position} (Opt)", (opt_x, opt_y),
                   xytext=(5, 5), textcoords='offset points', color='cyan')
    
    # Plot ball
    ax.scatter(ball_data.x, ball_data.y, color='brown', s=80, label='Ball')
    
    # Add play direction arrow
    arrow_x = ball_data.x
    arrow_dx = 5 if ball_data.playDirection == 'right' else -5
    ax.arrow(arrow_x, FIELD_WIDTH-5, arrow_dx, 0, head_width=1, head_length=1,
             fc='white', ec='white', label='Play Direction')
    
    # Add legend
    ax.legend(loc='upper right')
    
    # Add title
    plt.title(f"Play {play_id} - {play_info.offenseFormation} Formation\n"
              f"{play_info.playDescription}\n"
              f"Actual (Blue) vs Optimal (Cyan) Defensive Positions")
    
    # Save the plot
    plt.savefig('step234/play_64_analysis.png', bbox_inches='tight', dpi=300, facecolor='darkgreen')
    plt.close()

if __name__ == "__main__":
    # Find a valid play
    tracking_df = load_tracking_data()
    plays_df = load_plays_data()
    game_id, play_id = find_valid_play(tracking_df, plays_df)
    
    visualize_play(play_id, game_id) 