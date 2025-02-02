import math
from pyjoycon import JoyCon, get_R_id
import time

joycon_id = get_R_id()
joycon = JoyCon(*joycon_id)
joycon.get_status()

ideal = []
points = []
position = [0.0, 0.0, 0.0]
polling_interval = 200  # ms
active = False

while True:
    status = joycon.get_status()
    accel = status['accel']
    a = status['buttons']['right']['x']

    # do nothing
    if a == 0 and not active:
        continue

    # starting tracking loop
    if a == 1 and not active:
        active = True
        continue

    elif a == 0 and active:
        active = False
        ideal = points
        points = []
        position = [0.0, 0.0, 0.0]
        print(ideal)

    x, y, z = map(lambda a: int(a // 100) * 10, [accel['x'], accel['y'], accel['z']])
    z //= 10
    points.append((x, y, z))

    time.sleep(polling_interval / 1000)
