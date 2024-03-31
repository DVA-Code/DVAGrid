import pypsa
import pandas as pd
import matplotlib.pyplot as plt
import numpy  as np
import cartopy.crs as ccrs
import math
import matplotlib.ticker as mticker
import folium
import time 
import paho.mqtt.client as mqtt
import json
import ku_grid
import threading

network = ku_grid.create_network()

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

# set a counter to count the number of messages received
counter = 0

# set the power factor of 0.95
PF = 0.95
tan_phi = math.sqrt(1-PF**2)/PF

# initialize the variables to store the total power for each block
physics_meter_total_power = 1000
biotech_meter_total_power = 1000
management_meter_total_power = 1000
civil_meter_total_power = 1000

# create a map object
map = folium.Map(location=(27.619013147338894, 85.5387356168638), 
                    zoom_start=17, max_zoom=30)

# add a layer to plot the distribution grid
grid_layer = folium.FeatureGroup(name='Grid Layer').add_to(map)
folium.LayerControl().add_to(map)

# get coordinates of all the buses in the network
bus_coords = []
for index, row in network.buses.iterrows():
#     first latitude then longitude as folium expects location in this order
    bus_coords.append([row['y'], row['x']])

# Define a legend for the buses
bus_legend_html = """
        <div style="position: fixed; 
        top: 300px; right: 50px; width: 150px; height: 180px; 
        border:0px solid grey; z-index:9999; font-size:14px;
        background-color: white;
        ">&nbsp; <span style="font-weight: bold; font-size: 20px">Bus Legends </span></b><br>
        &nbsp; <font color="red" style="font-size: 30px;">●</font><span style="font-weight:bold;"> |V| < 0.95</span>   <br>
        &nbsp; <font color="green" style="font-size: 30px;">●</font><span style="font-weight:bold;"> 0.95 ≤ |V| ≤ 1.05</span><br>
        &nbsp; <font color="yellow" style="font-size: 30px;">●</font><span style="font-weight:bold;"> 1.05 < |V|</span><br>
        </div>
        """

# Define a legend for the lines
line_legend_html = """
        <div style="position: fixed; 
        bottom: 20px; right: 20px; width: 200px; height: 180px; 
        border:0px solid grey; z-index:9999; font-size:14px;
        background-color: white;
        ">&nbsp; <span style="font-weight: bold; font-size: 20px">Line Legends </span></b><br>
        &nbsp; <font color="green" style="font-size: 30px;">—</font><span style="font-weight:bold;"> Loading ≤ 50%</span><br>
        &nbsp; <font color="orange" style="font-size: 30px;">—</font><span style="font-weight:bold;"> 50% ≤ Loading < 100%</span><br>
        &nbsp; <font color="red" style="font-size: 30px;">—</font><span style="font-weight:bold;"> Loading > 100%</span><br>
        </div>
        """
# Add bus legend to the map
map.get_root().html.add_child(folium.Element(bus_legend_html))

# Add line legend to the map
map.get_root().html.add_child(folium.Element(line_legend_html))

map_counter = 0





# Callback function to handle incoming messages
def on_message(client, userdata, message):
    # decode the message into a python string and then convert to a dictionary  
    Payload_str = message.payload.decode("utf-8")
    payload_dict = json.loads(Payload_str)

    # get the active powers of all three phases
    pa = int(payload_dict['Datas'][0][2])
    pb = int(payload_dict['Datas'][1][2])
    pc = int(payload_dict['Datas'][2][2])
    total_power = pa+pb+pc

    global map_counter

    # store the total power to the gloabl variables of corresponding blocks
    global physics_meter_total_power
    global biotech_meter_total_power
    global civil_meter_total_power
    global management_meter_total_power

    global map
    global grid_layer

    if message.topic == Topic[PHYSICS]:
        print(f"got message from physics")
        physics_meter_total_power = total_power
        network.loads.loc['Load16', 'p_set'] = physics_meter_total_power/1e6
        network.loads.loc['Load16', 'q_set'] = (physics_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[BIOTECH]:
        print(f"got message from biotech")
        biotech_meter_total_power = total_power
        network.loads.loc['Load19', 'p_set'] = biotech_meter_total_power/1e6
        network.loads.loc['Load19', 'q_set'] = (biotech_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[MANAGEMENT]:
        print(f"got message from management")
        management_meter_total_power = total_power
        network.loads.loc['Load5', 'p_set'] = management_meter_total_power/1e6
        network.loads.loc['Load5', 'q_set'] = (management_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[CIVIL]:
        print(f"got message from civil")
        civil_meter_total_power = total_power
        network.loads.loc['Load6', 'p_set'] = civil_meter_total_power/1e6
        network.loads.loc['Load6', 'q_set'] = (civil_meter_total_power/1e6)*tan_phi
    

def time_tracker():
    global physics_meter_total_power
    global biotech_meter_total_power
    global civil_meter_total_power
    global management_meter_total_power
    while True:
        print(f"physics = {physics_meter_total_power}")
        print(f"biotech = {biotech_meter_total_power}")
        print(f"civil = {civil_meter_total_power}")
        print(f"management = {management_meter_total_power}")
        time.sleep(60)


thread = threading.Thread(target=time_tracker)
thread.start()

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
client.subscribe(Topic[BIOTECH])
client.subscribe(Topic[MANAGEMENT])
client.subscribe(Topic[CIVIL])

# Loop to maintain MQTT connection and process incoming messages
client.loop_forever()

