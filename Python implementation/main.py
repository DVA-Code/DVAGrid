import pypsa
import pandas as pd
import matplotlib.pyplot as plt
import numpy  as np
import cartopy.crs as ccrs
import math
import matplotlib.ticker as mticker
import folium
from folium.plugins import AntPath
import time 
import paho.mqtt.client as mqtt
import json
import ku_grid_model
import threading
import os
from dotenv import load_dotenv

network = ku_grid_model.create_network()

load_dotenv()
# MQTT broker details
broker_address = "mqtt.iammeter.com"  # MQTT broker address 
broker_port = 1883  # Default MQTT port
username = os.getenv("METER_MQTT_USER")
password = os.getenv("METER_MQTT_PASS")

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

# path to save map
MAP_PATH = r"G:\My Drive\D-VA\Main Project\Python implementation\ku_grid.html"

# create a map object
map = folium.Map(location=(27.619013147338894, 85.5387356168638), 
                    zoom_start=17, max_zoom=30)

# add a layer to plot the distribution grid
grid_layer = folium.FeatureGroup(name='Grid Layer').add_to(map)
# folium.LayerControl().add_to(map)

# add a layer for animation
animation_layer = folium.FeatureGroup(name='Animation', show = False).add_to(map)
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

    # store the total power to the variables of corresponding blocks
    global physics_meter_total_power
    global biotech_meter_total_power
    global civil_meter_total_power
    global management_meter_total_power

    global map
    global grid_layer

    if message.topic == Topic[PHYSICS]:
        physics_meter_total_power = total_power
        network.loads.loc['Load16', 'p_set'] = physics_meter_total_power/1e6
        network.loads.loc['Load16', 'q_set'] = (physics_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[BIOTECH]:
        biotech_meter_total_power = total_power
        network.loads.loc['Load19', 'p_set'] = biotech_meter_total_power/1e6
        network.loads.loc['Load19', 'q_set'] = (biotech_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[MANAGEMENT]:
        management_meter_total_power = total_power
        network.loads.loc['Load5', 'p_set'] = management_meter_total_power/1e6
        network.loads.loc['Load5', 'q_set'] = (management_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[CIVIL]:
        civil_meter_total_power = total_power
        network.loads.loc['Load6', 'p_set'] = civil_meter_total_power/1e6
        network.loads.loc['Load6', 'q_set'] = (civil_meter_total_power/1e6)*tan_phi
 

def load_flow():
    global physics_meter_total_power
    global biotech_meter_total_power
    global civil_meter_total_power
    global management_meter_total_power
    while True:
        # perform newton Raphson Load Flow
        network.pf()

        ####################################################################
        ######################### Network Plotting #########################
        ####################################################################
    
        # add circles to the locations of buses in the map
        for i in range(len(bus_coords)):
            # get the bus name
            bus_name = network.buses.index.to_list()[i]
            # get per unit voltage magnitude the bus
            v_mag_pu = network.buses_t.v_mag_pu.iloc[0, i]
            # get voltage angle of the bus (in radian by default) and convert it to degree
            v_ang_rad = network.buses_t.v_ang.iloc[0, i]
            v_ang_deg = (180/math.pi)*v_ang_rad 
            # set bus color based on voltage magnitude
            bus_color=''
            if v_mag_pu<0.95:
                bus_color='red'
            elif 0.95<=v_mag_pu<=1.05:
                bus_color='green'
            else:
                bus_color='yellow'
            # show bus voltage magnitude and voltage angle on the popup 
            popup_text = f'<span style="font-weight:bold; padding-left:20px;">{bus_name}</span><br>|V| = {v_mag_pu: .3f} p.u.<br>δ = {v_ang_deg: .3f} deg'
            folium.Circle(location=bus_coords[i], radius=3.5, 
                        stroke=False,
                        fill=True, fill_color= bus_color, fill_opacity=1.0,
                        popup=folium.Popup(popup_text, max_width=100)).add_to(grid_layer)
    
        # add lines
        for index, row in network.lines.iterrows():
            # get the name of the line
            line_name = index
            # get active and reactive powers of the line
            line_p = network.lines_t.p0.loc['now', index ]
            line_q = network.lines_t.q0.loc['now', index ]    
            # get the starting and ending buses of each line
            bus0 = row['bus0']
            bus1 = row['bus1']
            # set line colors based on the line loading
            # assume nominal line apparent capacity of 0.4 MVA
            s_nom_assumed = 0.069   #assumed nominal capacity of the line (230*300/1000000 MVA)
            # calculate the line percentage loading
            percentage_loading = (abs(network.lines_t.p0.loc['now', index ])/s_nom_assumed)*100
            line_color = ''
            if percentage_loading <= 50:
                # green color if line loading is less than 50%
                line_color = 'green' 
            elif (50 < percentage_loading <= 100):
                # violet if line loading is between 50 to 100%
                line_color = 'orange' 
            else:
                # red if line loading is greater than 100%
                line_color = 'red'

            # set line weight relative to percentage loading
            line_weight = 2.0 + percentage_loading*4/100
            # tooltip text for the line
            tooltip_text = f'<span style="font-weight: bold; padding-left: 0px">{line_name}</span><br>P = {line_p: .3f} MW<br>Q = {line_q:.3f} MVAr<br>loading = {percentage_loading: .3f}%'
            # finally, add the line
            # latitude first then longitude
            folium.PolyLine(locations=[(network.buses.loc[bus0].y, network.buses.loc[bus0].x), 
                                    (network.buses.loc[bus1].y, network.buses.loc[bus1].x)],
                            color = line_color, weight  = line_weight,
                        tooltip= tooltip_text).add_to(grid_layer)
            
            if line_p > 0:
                # if power is flowing from bus0 to bus1 direct arrows from bus0 to bus1
                x1, y1 = network.buses.loc[bus0].x, network.buses.loc[bus0].y  #first point of the line
                x2, y2 = network.buses.loc[bus1].x, network.buses.loc[bus1].y  #second point
            else:
                # if power is flowing from bus1 to bus0 direct arrows from bus1 to bus0
                x1, y1 = network.buses.loc[bus1].x, network.buses.loc[bus1].y  #first point of the line
                x2, y2 = network.buses.loc[bus0].x, network.buses.loc[bus0].y  #second point
            x3, y3 = (x1+x2)/2, (y1+y2)/2     # mid point
            m = (y2-y1)/(x2-x1)     #slope
            l = math.sqrt(pow(x2-x1, 2) + pow(y2-y1, 2))    #line length
            al = l/8    #arrow length
            # print(f'{line_name}: slope = {m}  & length = {l}')
            theta = math.atan(m)
            theta = abs(theta)
            phi = math.pi/8     # angle between the main line and the arrow lines 
            p = al*math.sin(theta)
            b = al*math.cos(theta)
            p1= al*math.tan(phi)
            b1= p1*math.cos(theta)
            k1= b1*math.tan(theta)
            p2 = p1
            b2 = b1
            k2 = k1
            if (x1<x2) and (y1<y2):
                # coordinates for arrowheads to the lines having positive slope, arrowhead pointing upwards
                xprime=x3-b
                yprime=y3-p
                x4=xprime-k1
                y4=yprime+b1
                x5=xprime+k2
                y5=yprime-b2

            elif (x1<x2) and (y1>y2):
                 # coordinates for arrowheads to the lines having negative slope, arrowhead pointing downwards
                xprime=x3-b
                yprime=y3+p
                x4=xprime+k1
                y4=yprime+b1
                x5=xprime-k2
                y5=yprime-b2

            elif (x1>x2) and (y1<y2):
                # coordinates for arrowheads to the lines having negative slope, arrowhead pointing upwards
                xprime=x3+b
                yprime=y3-p
                x4=xprime-k1
                y4=yprime-b1
                x5=xprime+k2
                y5=yprime+b2

            elif (x1>x2) and (y1>y2):
                # coordinates for arrowheads to the lines having positive slope, arrowhead pointing downwards
                xprime=x3+b
                yprime=y3+p
                x4=xprime+k1
                y4=yprime-b1
                x5=xprime-k2
                y5=yprime+b2

            # use triangles as arrowheads
            folium.Polygon(locations=[(y4, x4), (y3, x3), (y5, x5)],
                     color= line_color, weight=2.0,
              fill=True, fill_color = line_color, fill_opacity=0.8).add_to(grid_layer)

            # Use AntPath for animation
            # coordinates - first latitude(y) then longitude(x)
            AntPath([(y1, x1), (y2, x2)], 
                    delay = 400, dash_array=(3,10), 
                    color=line_color, pulse_color='#FFFFFF',
                    weight=3, opacity=1.0).add_to(animation_layer)
    
        # add a line between HVB and LVB1 as PyPSA doesn't create a line between the buses if there is a transformer in between
        folium.PolyLine(locations=[(network.buses.loc['HVB'].y, network.buses.loc['HVB'].x), 
                                    (network.buses.loc['LVB1'].y, network.buses.loc['LVB1'].x)],
                                color = 'black').add_to(grid_layer)

        # save the geomap of the network in an html file
        map.save(MAP_PATH)
        
    #     Autorefresh section -- modify the html file so that it autorefreshes every minute
        with open(MAP_PATH, 'r', encoding='utf-8') as f:
            f_contents = f.read()
        
        refreshed_content = f_contents.replace('</head>', '<meta http-equiv="refresh" content="60"></head>')
    
        with open(MAP_PATH, 'w', encoding='utf-8') as f:
            f.write(refreshed_content)
        
        time.sleep(60)


#create a thread to handle the data operations
#so that data fetching and manipulation run independently
thread = threading.Thread(target=load_flow)
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
