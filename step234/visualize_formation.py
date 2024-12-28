import matplotlib.pyplot as plt
import numpy as np

# Create figure and axis
plt.figure(figsize=(15, 10))
ax = plt.gca()

# Set field dimensions (showing just a portion of the field)
field_width = 53.3  # yards
field_length = 30   # yards (showing just a portion)

# Draw field
ax.set_xlim(0, field_length)
ax.set_ylim(0, field_width)
ax.set_facecolor('green')

# Add yard lines
for i in range(0, field_length + 1, 5):
    ax.axvline(x=i, color='white', alpha=0.3)

# Position of ball (center of formation)
ball_x, ball_y = 10, field_width/2  # Moved ball back to show more downfield
plt.plot(ball_x, ball_y, 'o', color='brown', markersize=10, label='Ball')

# Add arrow to show play direction
plt.arrow(ball_x, field_width-5, 5, 0, head_width=1, head_length=1, 
          fc='white', ec='white', label='Play Direction')

# Offensive positions for EMPTY 3x2
# Left side (3 receivers)
plt.plot(ball_x, ball_y-12, 'ro', markersize=10, label='WR')
plt.plot(ball_x, ball_y-6, 'ro', markersize=10)
plt.plot(ball_x, ball_y-2, 'ro', markersize=10)
# QB
plt.plot(ball_x-5, ball_y, 'ro', markersize=10, label='QB')
# Right side (2 receivers)
plt.plot(ball_x, ball_y+6, 'ro', markersize=10)
plt.plot(ball_x, ball_y+12, 'ro', markersize=10)

# Add offensive player labels
plt.annotate('WR', (ball_x-0.5, ball_y-12))
plt.annotate('WR', (ball_x-0.5, ball_y-6))
plt.annotate('SLOT', (ball_x-0.5, ball_y-2))
plt.annotate('QB', (ball_x-5.5, ball_y))
plt.annotate('WR', (ball_x-0.5, ball_y+6))
plt.annotate('WR', (ball_x-0.5, ball_y+12))

# Defensive positions based on normalized optimal_defensive_positions.csv
def plot_defender(x_rel, y_rel, label):
    abs_x = ball_x + x_rel
    abs_y = ball_y + y_rel
    plt.plot(abs_x, abs_y, 'bo', markersize=10)
    plt.annotate(label, (abs_x-0.5, abs_y+0.5))

# Plot defenders using the normalized positions from our analysis
# Using the updated coordinates from EMPTY 3x2 formation
plot_defender(8.0, 0.3, 'CB')     # Cornerback
plot_defender(10.8, 0.1, 'SS')    # Strong Safety
plot_defender(10.5, 0.4, 'FS')    # Free Safety
plot_defender(7.2, -0.1, 'MLB')   # Middle Linebacker
plot_defender(5.4, 0.1, 'DE')     # Defensive End
plot_defender(5.2, -0.1, 'DT')    # Defensive Tackle
plot_defender(5.4, -0.1, 'DE')    # Other DE
plot_defender(5.2, 0.1, 'DT')     # Other DT
plot_defender(8.0, -0.3, 'CB')    # Other CB
plot_defender(6.9, 0.1, 'LB')     # Other LB

# Add title and labels
plt.title('EMPTY 3x2 Formation with Optimal Defensive Positioning\n(Normalized for Play Direction)', pad=20)
plt.xlabel('Field Length (yards)')
plt.ylabel('Field Width (yards)')

# Add legend
plt.legend(loc='upper right')

# Save the plot
plt.savefig('step234/empty_3x2_formation_normalized.png', dpi=300, bbox_inches='tight')
plt.close() 