import time
from XRPLib.differential_drive import DifferentialDrive
from MQTT.mqttconnect import *

robot1 = DifferentialDrive.get_default_differential_drive() # initializes robot drivetrain

# Initialize the orientation variable
current_orientation = 'e'  # Initial orientation in degrees (0 means facing forward)

c = connect_mqtt()
c.ping()

# Variable to store the latest message
latest_message = None

# Define the function to handle messages
def get_turn_angle_and_new_dir_math(dx, dy, current_dir): # this function helps the robot know its current orientation, and based off the dx,dy values, it's turn angle
    dir_to_angle = {
        'e': 0,
        'n': 90,
        'w': 180,
        's': 270
    }
    angle_to_dir = {v: k for k, v in dir_to_angle.items()}

    if dx > 0:
        target_angle = 0
    elif dx < 0:
        target_angle = 180
    elif dy > 0:
        target_angle = 270  # South (down)
    elif dy < 0:
        target_angle = 90  # North (up)
    else:
        raise ValueError("Invalid input: both dx and dy are 0")

    current_angle = dir_to_angle[current_dir.lower()]

    delta = (target_angle - current_angle + 360) % 360
    if delta > 180:
        delta -= 360  # Convert to smallest signed angle (e.g., -90 instead of 270)

    new_dir = angle_to_dir[target_angle]
    return delta, new_dir

def handle_message(topic, message): # topic is the channel the robot subscribes to, and the message is sent as a string
    global current_orientation, latest_message

    try: # works on decoding the string and turning it into an integer
        payload_str = message.decode()
        print(f"Received on topic {topic}: {payload_str}")
        payload_str = payload_str.strip("[]")
        parts = payload_str.split(",")
        dx = int(parts[0].strip())
        dy = int(parts[1].strip())
        print(f"dx = {dx}, dy = {dy}")

        # Store the latest message
        latest_message = (dx, dy) #

    except Exception as e:
        robot1.stop()
        print("Error handling message:", e)

def flush_and_execute(): # robot movement execution
    global current_orientation, latest_message
    while latest_message is not None:  # Process all messages in the queue
        dx, dy = latest_message

        # Prioritize dx movement first
        if abs(dx) > abs(dy): #if dx > dy, or vice versa, one of them is set to 0 so the robot can have a proper lateral or longitudal movement
            dy = 0
        else:
            dx = 0

        # Determine required turn and new direction
        turn_angle, new_orientation = get_turn_angle_and_new_dir_math(dx, dy, current_orientation)
        
        # If a turn is needed, do it
        if turn_angle != 0:
            print(f"Turning {turn_angle}° from {current_orientation} to {new_orientation}")
            robot1.turn(turn_angle, max_effort=0.5)
            current_orientation = new_orientation  # Update orientation after turning
            robot1.stop()
            time.sleep(0.5)

        # Move forward in the selected direction
        if abs(dx) > 40 or abs(dy) > 40:
            robot1.set_speed(7, 7)
            # time.sleep(1)
            # robot1.stop()
        else: #resets the robot back to facing east after it is done its movements
            robot1.stop()
            if current_orientation=='e':
                robot1.stop()
            elif current_orientation=='n':
                robot1.turn(-90, max_effort=0.5)
            elif current_orientation=='w':
                robot1.turn(180, max_effort=0.5)
            elif current_orientation=='s':
                robot1.turn(90, max_effort=0.5)
            robot1.stop() 
            current_orientation='e'


        # Reset the latest message after processing it
        latest_message = None

# Set up MQTT callback
c.set_callback(handle_message)
c.subscribe("SlidePuzzle/send/1")  # Adjust topic as needed

while True:
    try:
        # Flush all pending messages in the queue
        flush_and_execute()

        # Wait for the next message to arrive
        c.wait_msg()

    except Exception as e:
        print("Exception occurred:", e)
