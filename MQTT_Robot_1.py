import time
from XRPLib.differential_drive import DifferentialDrive
from MQTT.mqttconnect import *

# Add SSID and PW in config.txt
# Add MQTT broker IP in config.txt and mqttconnect.py

robot1 = DifferentialDrive.get_default_differential_drive()

c = connect_mqtt()
c.ping()

if False: #publishing
    c.publish("topic/message", "Start driving", retain=True)
    drivetrain.set_speed(10,10)
    time.sleep(2)
    c.publish("topic/message", "Stop motors", retain=True)
    drivetrain.set_speed(0,0)
    c.publish("topic/data", str(20), retain=True)
else: #subscribing # julian is going to send things over certain topics which are exclusive to each robot
    #robots constantly listneing, only moves when spoken to
    def handle_message(dx, dy):
        try:
            dxMovement = int(dx)
            dyMovement = int(dy)
            robot1.stop()
            while abs(dxMovement) > 20:
                if dxMovement > 0:
                    robot1.set_effort(0.2,0.2) # walking until it's done
                if dxMovement < 0:
                    robot1.set_effort(-0.2, -0.2)
            robot1.stop()
            time.sleep(3)
            while abs(dyMovement) > 20:
                if dyMovement > 0:
                    robot1.turn(90, max_effort=0.5)
                    robot1.set_effort(0.2,0.2)
                if dyMovement < 0:
                    robot1.turn(-90, max_effort= 0.5)
            robot1.stop()
        except:
            print("Exception parsing")
    
    c.set_callback(handle_message)
    c.subscribe("SlidePuzzle/send/1") #can be re-named to any topic name and any data name e.g., nemitz/kinematics
    while True:
        try:
            c.wait_msg()
        except:
            print("exception")