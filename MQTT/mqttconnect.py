import network
import time
from MQTT.simple import MQTTClient
#import ssl
from machine import unique_id

# MQTT Parameters
MQTT_SERVER = "" # 10.247.137.92
MQTT_PORT = 1883
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "XRP-Nemitz"
MQTT_KEEPALIVE = 9999
MQTT_SSL = None   # set to False if using local Mosquitto MQTT broker
MQTT_SSL_PARAMS = {'server_hostname': MQTT_SERVER}

def initialize_wifi(ssid, password):

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    #print(ssid,password)
    # Connect to the network
    wlan.connect(ssid, password)

    # Wait for Wi-Fi connection
    connection_timeout = 10
    while connection_timeout > 0:
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        time.sleep(1)

    # Check if connection is successful
    if wlan.status() != 3:
        return False
    else:
        print('Connection successful!')
        network_info = wlan.ifconfig()
        print('IP address:', network_info[0])
        return True
def read_config(filename):
    config = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    except Exception as e:
        print("Error reading config:", e)
    return config

def connect_mqtt():

    config = read_config("MQTT/config.txt")

    id = (''.join(['{:02x}'.format(b) for b in unique_id()]))
    
    #print(id)
    if not initialize_wifi(config.get("ssid"),config.get("password")):
        return None;
    try:
        client = MQTTClient(client_id=MQTT_CLIENT_ID + id,
                            server=config.get("mqtt_broker"),
                            user=MQTT_USER,
                            password=MQTT_PASSWORD,
                            port=MQTT_PORT,
                            keepalive=MQTT_KEEPALIVE,
                            ssl=MQTT_SSL
                            )
        client.connect()
        return client
    except Exception as e:
        print('Error connecting to MQTT:', e)
        raise  # Re-raise the exception to see the full traceback