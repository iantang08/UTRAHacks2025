import math
from pyjoycon import JoyCon, get_L_id
import time

# Constants
POLLING_INTERVAL = 150  # ms
TOLERANCE = 20          # Small tolerance for minor variation
GYRO_SCALE = 100        # Scale factor for gyroscope data

# You can adjust these two to calibrate how harshly you penalize big differences:
VARIANCE_POWER = 1.5    # Exponent for large distances (1.5 is between linear and square)
SCALE = 0.5             # Overall multiplier for penalty (lower => more lenient, higher => harsher)

# Initialize JoyCon
joycon_id = get_L_id()
joycon = JoyCon(*joycon_id)

# Ideal routine (placeholder, will be replaced by user recording)
ideal = []

def calculate_distance(point1, point2):
    """Euclidean distance in 3D."""
    return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)))

def calculate_score(user_points, ideal_points):
    """
    Compare the user's points vs. the recorded ideal points,
    returning a score from 0 to 100 (best).

    - If distance <= TOLERANCE, no penalty.
    - If distance > TOLERANCE, penalty = ((distance - TOLERANCE) ** VARIANCE_POWER).
      This punishes big spikes more than linear, but less than full squaring if VARIANCE_POWER < 2.
    - The total average penalty is then scaled by SCALE, subtracted from 100.
    """
    if not user_points or not ideal_points:
        return 0

    # We'll compare up to the min length if they differ
    min_length = min(len(user_points), len(ideal_points))

    total_penalty = 0.0
    for i in range(min_length):
        dist = calculate_distance(user_points[i], ideal_points[i])
        if dist > TOLERANCE:
            # Exponential penalty for larger differences
            penalty = (dist - TOLERANCE) ** VARIANCE_POWER
        else:
            # Within tolerance => no penalty
            penalty = 0
        total_penalty += penalty

    # Average penalty over the matched length
    avg_penalty = total_penalty / min_length

    # Penalize for missing or extra points
    length_diff = abs(len(user_points) - len(ideal_points))
    length_penalty = length_diff * 2  # 2 points off per missing/extra sample

    # Convert penalty to a score out of 100
    # The bigger the penalty, the lower the score
    score = 100 - (avg_penalty * SCALE) - length_penalty
    return max(int(score), 0)

# Main loop
points = []
active = False
recording_mode = False  # True if in recording mode
play_mode = False       # True if in play mode

while True:
    status = joycon.get_status()
    gyro = status['gyro']
    buttons = status['buttons']['left']

    # Button mappings
    up_button = buttons['up']
    left_button = buttons['left']
    down_button = buttons['down']

    # Enter recording mode (left button)
    if left_button == 1 and not recording_mode and not play_mode:
        print("Entering recording mode...")
        recording_mode = True
        play_mode = False
        time.sleep(0.5)  # Debounce

    # Enter play mode (down button)
    if down_button == 1 and not play_mode and not recording_mode:
        if ideal:  # Only enter play mode if a routine is recorded
            print("Entering play mode...")
            play_mode = True
            recording_mode = False
            time.sleep(0.5)  # Debounce
        else:
            print("No routine recorded. Please record a routine first.")

    # Start recording or playing (up button)
    if up_button == 1:
        if recording_mode and not active:
            print("Starting recording...")
            points = []
            active = True
            time.sleep(0.5)  # Debounce
        elif play_mode and not active:
            print("Starting playback...")
            points = []
            active = True
            time.sleep(0.5)  # Debounce

    # Stop recording or playing (up button released)
    if up_button == 0 and active:
        if recording_mode:
            print("Stopping recording...")
            ideal = points.copy()
            points = []
            active = False
            recording_mode = False
            print("Routine saved!")
            print("Ideal routine:", ideal)
            time.sleep(0.5)  # Debounce
        elif play_mode:
            print("Stopping playback...")
            score = calculate_score(points, ideal)
            print("User points:", points)
            print("Score:", score)
            points = []
            active = False
            play_mode = False
            time.sleep(0.5)  # Debounce

    # Collect data if active
    if active:
        x, y, z = map(lambda g: int(g // GYRO_SCALE), [gyro['x'], gyro['y'], gyro['z']])
        points.append((x, y, z))
        print(f"Recorded point: ({x}, {y}, {z})")

    time.sleep(POLLING_INTERVAL / 1000)
