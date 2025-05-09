import time
from XRPLib.differential_drive import DifferentialDrive
from MQTT.mqttconnect import *

# Add SSID and PW in config.txt
# Add MQTT broker IP in config.txt and mqttconnect.py

drivetrain = DifferentialDrive.get_default_differential_drive()
c = connect_mqtt()
c.ping()

if False: #publishing
    c.publish("topic/message", "Start driving", retain=True)
    drivetrain.set_speed(10,10)
    time.sleep(2)
    c.publish("topic/message", "Stop motors", retain=True)
    drivetrain.set_speed(0,0)
    c.publish("topic/data", str(20), retain=True)
else: #subscribing
    def handle_message(topic, msg):
        try:
            #print(topic)
            print(msg)
            if msg == b'0':
                drivetrain.set_speed(0,0)
            if msg == b'10':
                drivetrain.set_speed(10,10)
                time.sleep(2)
            if msg == b'20':
                drivetrain.set_speed(-10,-10)
                time.sleep(2)
            drivetrain.set_speed(0,0)
        except:
            print("Exception parsing")
    
    c.set_callback(handle_message)
    c.subscribe("topic/data") #can be re-named to any topic name and any data name e.g., nemitz/kinematics
    while True:
        try:
            c.wait_msg()
        except:
            print("exception")