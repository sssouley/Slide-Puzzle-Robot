import time
from XRPLib.differential_drive import DifferentialDrive
from MQTT.mqttconnect import *

robot2 = DifferentialDrive.get_default_differential_drive()
current_orientation = 'e'  # Start facing east

c = connect_mqtt()
c.ping()

Kp = 0.015
DRIVE_EFFORT_SCALE = 0.6
TIMEOUT = 1.0  # seconds
last_msg_time = time.time()
robot_is_moving = False

def get_turn_angle_and_new_dir_math(dx, dy, current_dir):
    dir_to_angle = {'e': 0, 'n': 90, 'w': 180, 's': 270}
    angle_to_dir = {v: k for k, v in dir_to_angle.items()}

    if dx > 0:
        target_angle = 0
    elif dx < 0:
        target_angle = 180
    elif dy > 0:
        target_angle = 270  # South
    elif dy < 0:
        target_angle = 90  # North
    else:
        raise ValueError("Invalid input: both dx and dy are 0")

    current_angle = dir_to_angle[current_dir.lower()]
    delta = (target_angle - current_angle + 360) % 360
    if delta > 180:
        delta -= 360

    new_dir = angle_to_dir[target_angle]
    return delta, new_dir

def handle_message(topic, message):
    global current_orientation, last_msg_time, robot_is_moving

    try:
        last_msg_time = time.time()  # Reset timeout timer
        payload_str = message.decode().strip("[]")
        print(f"Received on topic {topic}: {payload_str}")
        dx, dy = [int(part.strip()) for part in payload_str.split(",")]

        if abs(dx) > abs(dy):
            dy = 0
        else:
            dx = 0

        turn_angle, new_orientation = get_turn_angle_and_new_dir_math(dx, dy, current_orientation)

        if turn_angle != 0:
            print(f"Turning {turn_angle}° from {current_orientation} to {new_orientation}")
            robot2.turn(turn_angle, max_effort=0.5)
            current_orientation = new_orientation
            robot2.stop()
            time.sleep(0.3)

        dist = abs(dx) if dx != 0 else abs(dy)
        if dist > 5:
            effort = min(Kp * dist, 0.5) * DRIVE_EFFORT_SCALE
            effort = max(effort, 0.25)
            print(f"Driving with effort {effort}")
            robot2.set_effort(effort, effort)
            robot_is_moving = True
            time.sleep(0.6)
            robot2.stop()
        else:
            robot2.stop()
            robot_is_moving = False

    except Exception as e:
        error_msg = f"Error handling message: {e}"
        print(error_msg)
        c.publish("SlidePuzzle/error/2", error_msg)
        robot2.stop()
        robot_is_moving = False


c.set_callback(handle_message)
c.subscribe("SlidePuzzle/send/2")

while True:
    try:
        c.check_msg()  # Non-blocking check for new message
        if time.time() - last_msg_time > TIMEOUT and robot_is_moving:
            print("No recent message — stopping robot.")
            robot2.stop()
            robot_is_moving = False
        time.sleep(0.1)  # Reduce CPU usage
    except Exception as e:
        error_msg = f"Exception occurred: {e}"
        print(error_msg)
        c.publish("SlidePuzzle/error/2", error_msg)
        robot2.stop()
        robot_is_moving = False

