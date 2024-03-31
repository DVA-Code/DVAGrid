import time 
import paho.mqtt.client as mqtt
import json
import threading

# MQTT broker details
broker_address = "mqtt.iammeter.com"  # MQTT broker address - iammeter broker in this case
broker_port = 1883  # Default MQTT port
username = "karuna"
password = "232794"

TOTAL_BLOCKS = 4

PHYSICS = 0
BIOTECH = 1
MANAGEMENT = 2
CIVIL = 3

# Topics to subscribe to, for each meter
Topic = {PHYSICS: "device/CD0FF6AB/realtime",
          BIOTECH: "device/57DB095D/realtime",
          MANAGEMENT: "device/8FA834AC/realtime",
          CIVIL: "device/DAD94549/realtime"}

physics_dict = {}

# Callback function to handle incoming messages
def on_message(client, userdata, message):
    global physics_dict
    # decode the message into a python string and then convert to a dictionary  
    Payload_str = message.payload.decode("utf-8")
    physics_dict = json.loads(Payload_str)
    # print(payload_dict)
    


def time_tracker():
    while True:
        global physics_dict
        print(physics_dict)
        time.sleep(20)
    

t1 = threading.Thread(target=time_tracker)
t1.start()

# Create MQTT client instance
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

# Set username and password for authentication
client.username_pw_set(username, password)

# Assign callback function to handle incoming messages
client.on_message = on_message

# Connect to MQTT broker
client.connect(broker_address, broker_port)

# Subscribe to the topics
client.subscribe(Topic[PHYSICS])

# Loop to maintain MQTT connection and process incoming messages
client.loop_forever()


