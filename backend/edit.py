import math
from pyjoycon import JoyCon, get_L_id
import time

joycon_id = get_L_id()
joycon = JoyCon(*joycon_id)
joycon.get_status()

ideal = [[30, 0, 380],
         [30, 110, 780],
         [90, 170, 1160],
         [120, 200, 1540],
         [120, 180, 1940],
         [130, 220, 2320]]
points = []
position = [0.0, 0.0, 0.0]
polling_interval = 200  # ms
active = False
read = False
start_time = 0

while True:
    status = joycon.get_status()
    accel = status['accel']
    gyro = status['gyro']
    a = status['buttons']['left']['up']
    b = status['buttons']['left']['left']
    c = status['buttons']['left']['down']

    if b == 1 and not read:
        read = True
        print("reading!")
        continue
    if c == 1 and read:
        read = False
        print("not reading!")
        continue

    # nothing
    if a == 0 and not active:
        continue

    # starting tracking loop
    if a == 1 and not active:
        points = []
        position = [0, 0, 0]
        active = True
        continue

    # ending tracking loop
    if a == 0 and active and not read:
        active = False
        score = 100
        print(points)
        for user_point, ideal_point in zip(points, ideal):
            distance = 0
            for i in range(3):
                distance += abs(user_point[i] - ideal_point[i])
            distance = max(distance - 150, 0)
            score -= distance / len(ideal)

        if len(points) < len(ideal):
            score += (len(points) - len(ideal)) * (100 / len(ideal))

        score = int(max(score, 0))
        print("score:", score)

        points = []
        position = [0, 0, 0]
    elif a == 0 and active:
        active = False
        ideal = points
        points = []
        position = [0, 0, 0]
        print(ideal)
        print("saved!")

    x, y, z = map(lambda a: int(a // 100) * 10, [accel['x'], accel['y'], accel['z']])
    z //= 10
    points.append((x, y, z))

    time.sleep(polling_interval / 1000)
