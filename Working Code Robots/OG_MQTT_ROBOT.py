import time
from XRPLib.differential_drive import DifferentialDrive
from MQTT.mqttconnect import *

# Add SSID and PW in config.txt
# Add MQTT broker IP in config.txt and mqttconnect.py

robot1 = DifferentialDrive.get_default_differential_drive()
robot2 = DifferentialDrive.get_default_differential_drive()
robot3 = DifferentialDrive.get_default_differential_drive()

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
    def handle_message(topic, robotSelection, dx, dy):
        try:
            #print(topic)
            print(robotSelection) # Depending on Which Robot Moves - currently hardcoded but if I have time I can make a loop based off the number
            # Eye in the sky camera needs to calculate moves, then writes MQTT message i.e. telling the robot to move forward 
            # Robot # 1
            if robotSelection == b'1':
                movingX = False
                movingY = True
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
                
                

            # Robot 2
            if robotSelection == b'Robot 2':
                dxMovement = int(dx)
                dyMovement = int(dy)
                if dxMovement > 0:
                    robot2.set_speed(dxMovement/5, dxMovement/5) #walk distance dx
                    if dyMovement > 0:
                        robot2.turn(90)
                        robot2.set_speed(dyMovement/5, dyMovement/5) #walk distance dy
                    elif dyMovement < 0:
                        robot2.turn(-90)
                        robot2.set_speed(dyMovement/5, dyMovement/5) # walk distance dy
                if dxMovement < 0:
                    dyMovement = -dyMovement
                    robot2.turn(180, max_effort= 0.5)
                    robot2.set_speed(dxMovement/5, dxMovement/5) # walk -dx
                    if dyMovement > 0:
                        robot2.turn(90)
                        robot2.set_speed(dyMovement/5, dyMovement/5) #walk distance dy
                    elif dyMovement < 0:
                        robot2.turn(-90)
                        robot2.set_speed(dyMovement/5, dyMovement/5) #walk distnace dy
            # Robot 3
            if robotSelection == b'Robot 3':
                dxMovement = int(dx)
                dyMovement = int(dy)
                if dxMovement > 0:
                    robot3.set_speed(dxMovement/5, dxMovement/5) #walk distance dx
                    if dyMovement > 0:
                        robot3.turn(90)
                        robot3.set_speed(dyMovement/5, dyMovement/5) #walk distance dy
                    elif dyMovement < 0:
                        robot3.turn(-90)
                        robot3.set_speed(dyMovement/5, dyMovement/5) # walk distance dy
                if dxMovement < 0:
                    dyMovement = -dyMovement
                    robot3.turn(180, max_effort= 0.5)
                    robot3.set_speed(dxMovement/5, dxMovement/5) # walk -dx
                    if dyMovement > 0:
                        robot3.turn(90)
                        robot3.set_speed(dyMovement/5, dyMovement/5) #walk distance dy
                    elif dyMovement < 0:
                        robot3.turn(-90)
                        robot3.set_speed(dyMovement/5, dyMovement/5) #walk distnace dy
                
                # Stops all Robots after their task
                robot1.stop()
                robot2.stop()
                robot3.stop()
        except:
            print("Exception parsing")
    
    c.set_callback(handle_message)
    c.subscribe("topic/data") #can be re-named to any topic name and any data name e.g., nemitz/kinematics
    while True:
        try:
            c.wait_msg()
        except:
            print("exception")