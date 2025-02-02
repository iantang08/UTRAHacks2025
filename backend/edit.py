import math
import random
from pyjoycon import JoyCon, get_L_id, get_R_id
import time

# -------------- Constants & Configuration --------------

POLLING_INTERVAL = 150  # ms
TOLERANCE = 20          # Small tolerance for scoring variation
GYRO_SCALE = 100        # Scale factor for gyroscope data

# Scoring sensitivity
VARIANCE_POWER = 1.5
SCALE = 0.5

# ------------------ Heart Rate Parameters ------------------
HEART_RATE_MIN = 60.0       # Absolute lower bound on HR
HEART_RATE_MAX = 180.0      # Absolute upper bound on HR

# ------------------ Growth Logic ------------------
BASE_GROWTH = 0.02                # Base growth factor per distance unit
GROWTH_DECAY_INCREMENT = 0.0002   # How fast the growth factor goes down each consecutive high-delta frame
GROWTH_INDEX_MAX = 200            # Limit how much we can decrease growth factor

# ------------------ Decay Logic ------------------
BASE_DECAY = 0.05           # Minimal decay per update
DECAY_INCREMENT = 0.0      # Each consecutive low-delta frame increases decay by this
DECAY_INDEX_MAX = 3        # Max consecutive increments of decay

# ------------------ Movement Threshold ------------------
DELTA_THRESHOLD = 5.0       # “High” movement threshold

# ------------------ Baseline Logic ------------------
BASELINE_RANGE = 10.0       # If HR goes outside ±10 BPM of baseline, we disable baseline corrections

# -------------- JoyCon Initialization --------------
joycon_id = get_R_id()
joycon = JoyCon(*joycon_id)

# -------------- Helper Functions --------------

def calculate_distance(point1, point2):
    """Euclidean distance in 3D."""
    return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)))

def calculate_score(user_points, ideal_points):
    """
    Compare the user's points vs. the recorded ideal points,
    returning a score from 0 to 100 (best).

    - If distance <= TOLERANCE, no penalty.
    - If distance > TOLERANCE, penalty = ((distance - TOLERANCE) ** VARIANCE_POWER).
    - The total average penalty is scaled by SCALE, subtracted from 100.
    """
    if not user_points or not ideal_points:
        return 0

    min_length = min(len(user_points), len(ideal_points))
    total_penalty = 0.0

    for i in range(min_length):
        dist = calculate_distance(user_points[i], ideal_points[i])
        if dist > TOLERANCE:
            penalty = (dist - TOLERANCE) ** VARIANCE_POWER
        else:
            penalty = 0
        total_penalty += penalty

    avg_penalty = total_penalty / min_length

    # Penalize for missing or extra points
    length_diff = abs(len(user_points) - len(ideal_points))
    length_penalty = length_diff * 2  # 2 points off per missing/extra sample

    score = 100 - (avg_penalty * SCALE) - length_penalty
    return max(int(score), 0)

def update_heart_rate(
    heart_rate,
    growth_index,
    decay_index,
    dist,
    baseline_hr,
    baseline_active
):
    """
    Updates heart_rate given the distance (dist) between consecutive frames.

    1) If dist > DELTA_THRESHOLD => "high movement"
       - growth_index += 1 (capped at GROWTH_INDEX_MAX)
       - decay_index = 0 (reset decay buildup)
    2) Else => "low movement"
       - decay_index += 1 (capped at DECAY_INDEX_MAX)
       - growth_index = 0

    3) growth_factor = max(0, BASE_GROWTH - growth_index * GROWTH_DECAY_INCREMENT)
    4) decay_factor = BASE_DECAY + (decay_index * DECAY_INCREMENT)
    5) heart_rate += dist * growth_factor
    6) If baseline_active == True, we apply "half" the normal decay
       (pretending we're near baseline). Otherwise, apply the full decay.
    7) Clamp heart_rate to [HEART_RATE_MIN, HEART_RATE_MAX].

    Returns: (updated_heart_rate, updated_growth_index, updated_decay_index)
    """

    # 1 & 2) Update indexes
    if dist > DELTA_THRESHOLD:
        growth_index = min(growth_index + 1, GROWTH_INDEX_MAX)
        decay_index = 0
    else:
        decay_index = min(decay_index + 1, DECAY_INDEX_MAX)
        growth_index = 0

    # 3) Growth factor (decreases with consecutive high-delta frames)
    growth_factor = max(0.0, BASE_GROWTH - growth_index * GROWTH_DECAY_INCREMENT)

    # 4) Decay factor (increases with consecutive low-delta frames)
    decay_factor = BASE_DECAY + decay_index * DECAY_INCREMENT

    # 5) Increase heart rate by movement
    heart_rate += dist * growth_factor

    # 6) Apply decay
    if baseline_active:
        # If still considered "near baseline," apply half the normal decay
        heart_rate -= (decay_factor / 2.0)
    else:
        # If we've left baseline range, use full decay
        heart_rate -= decay_factor

    # 7) Clamp
    heart_rate = max(HEART_RATE_MIN, min(heart_rate, HEART_RATE_MAX))
    return heart_rate, growth_index, decay_index

# -------------- Main Loop --------------

ideal = []
points = []
active = False
recording_mode = True
play_mode = False

baseline_hr = None
baseline_active = True  # If True, we apply "baseline corrections" (half decay)

heart_rate = 0
growth_index = 0
decay_index = 0

heart_rate_history = []

while True:
    status = joycon.get_status()
    gyro = status['gyro']
    buttons = status['buttons']['right']

    # Button mappings
    up_button = buttons['x']


    # --- Stop recording or playing (release up button) ---
    if up_button == 0 and not active:
        continue

    if up_button == 1 and not active:
        active = True
        continue

    if up_button == 0 and active:
        if recording_mode:
            ideal = points.copy()
            points = []
            active = False
            # recording_mode = False
            print(ideal)
            break

    # --- If we are actively recording or playing ---
    if active:
        # Get current gyro data
        x, y, z = map(lambda g: int(g // GYRO_SCALE), [gyro['x'], gyro['y'], gyro['z']])
        points.append((x, y, z))

    time.sleep(POLLING_INTERVAL / 1000)
