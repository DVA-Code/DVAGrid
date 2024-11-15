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
import datetime
import paho.mqtt.client as mqtt
import json
import ku_grid_model
import threading
import os
from dotenv import load_dotenv
import html_contents
import buses_and_lines

network = ku_grid_model.create_network()

load_dotenv()
# MQTT broker details
broker_address = "mqtt.iammeter.com"  # MQTT broker address 
broker_port = 1883  # Default MQTT port
username = os.getenv("METER_MQTT_USER")
password = os.getenv("METER_MQTT_PASS")

TOTAL_BLOCKS = 5
PHYSICS = 0
BIOTECH = 1
MANAGEMENT = 2
CIVIL = 3
ELECTRICAL = 4
TRANSFORMER = 5


# Topics to subscribe to, for each meter
Topic = {PHYSICS: "device/CD0FF6AB/realtime",
          BIOTECH: "device/57DB095D/realtime",
          MANAGEMENT: "device/8FA834AC/realtime",
          CIVIL: "device/DAD94549/realtime",
          ELECTRICAL: "device/C249361B/realtime",
          TRANSFORMER: "device/F51C3384/realtime"}


# set the power factor of 0.95
PF = 0.95
tan_phi = math.sqrt(1-PF**2)/PF

# initialize the variables to store the total power for each block
physics_meter_total_power = 1000
biotech_meter_total_power = 1000
management_meter_total_power = 1000
civil_meter_total_power = 1000
electrical_meter_total_power = 1000
transformer_meter_total_power = 1000

# path to save map
MAP_PATH = r"G:\My Drive\D-VA\Main Project\Python implementation\ku_grid.html"

# create a map object
map = folium.Map(location=(27.619013147338894, 85.5387356168638), 
                    zoom_start=18, max_zoom=30)

# add a layer to plot the distribution grid
grid_layer = folium.FeatureGroup(name='Grid Layer').add_to(map)
# folium.LayerControl().add_to(map)

# add a layer for animation
animation_layer = folium.FeatureGroup(name='Animation', show = False).add_to(map)

# add a layer to display faults
fault_layer = folium.FeatureGroup(name='Fault Detection', show=False).add_to(map)
folium.LayerControl().add_to(map)

# get coordinates of all the buses in the network
bus_coords = []
for index, row in network.buses.iterrows():
#     first latitude then longitude as folium expects location in this order
    bus_coords.append([row['y'], row['x']])

# Define a legend for the buses
bus_legend_html = html_contents.get_legend_html(element_name="bus")

# Define a legend for the lines
line_legend_html = html_contents.get_legend_html(element_name="line")

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
    pa = float(payload_dict['Datas'][0][2])
    pb = float(payload_dict['Datas'][1][2])
    pc = float(payload_dict['Datas'][2][2])
    total_power = int(pa+pb+pc)

    # store the total power to the variables of corresponding blocks
    global physics_meter_total_power
    global biotech_meter_total_power
    global civil_meter_total_power
    global management_meter_total_power
    global electrical_meter_total_power
    global transformer_meter_total_power

    global map
    global grid_layer

    if message.topic == Topic[PHYSICS]:
        physics_meter_total_power = total_power
        print(f"got message from physics, power = {total_power}")
        network.loads.loc['Load16', 'p_set'] = physics_meter_total_power/1e6
        network.loads.loc['Load16', 'q_set'] = (physics_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[BIOTECH]:
        biotech_meter_total_power = total_power
        print(f"got message from biotech, power = {total_power}")
        network.loads.loc['Load19', 'p_set'] = biotech_meter_total_power/1e6
        network.loads.loc['Load19', 'q_set'] = (biotech_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[MANAGEMENT]:
        management_meter_total_power = total_power
        print(f"got message from management, power = {total_power}")
        network.loads.loc['Load5', 'p_set'] = management_meter_total_power/1e6
        network.loads.loc['Load5', 'q_set'] = (management_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[CIVIL]:
        civil_meter_total_power = total_power
        print(f"got message from civil, power = {total_power}")
        network.loads.loc['Load6', 'p_set'] = civil_meter_total_power/1e6
        network.loads.loc['Load6', 'q_set'] = (civil_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[ELECTRICAL]:
        electrical_meter_total_power = total_power
        print(f"got message from electrical, power = {total_power}")
        network.loads.loc['Load49', 'p_set'] = electrical_meter_total_power/1e6
        network.loads.loc['Load49', 'q_set'] = (electrical_meter_total_power/1e6)*tan_phi
    elif message.topic == Topic[TRANSFORMER]:
        transformer_meter_total_power = total_power
        print(f"got message from transformer, power = {total_power}")
        metered_total_power = physics_meter_total_power+biotech_meter_total_power+management_meter_total_power+civil_meter_total_power+electrical_meter_total_power
        unmetered_total_power = transformer_meter_total_power - metered_total_power

        # update the active and reactive powers of unmetered loads
        # in proportion to their circuit breaker rating
        network.loads.loc['Load17', 'p_set'] = (unmetered_total_power*0.010548)/1e6
        network.loads.loc['Load17', 'q_set'] = ((unmetered_total_power*0.010548)/1e6)*tan_phi
        network.loads.loc['Load8', 'p_set'] = (unmetered_total_power*0.042194)/1e6
        network.loads.loc['Load8', 'q_set'] = ((unmetered_total_power*0.042194)/1e6)*tan_phi
        network.loads.loc['Load30', 'p_set'] = (unmetered_total_power*0.042194)/1e6
        network.loads.loc['Load30', 'q_set'] = ((unmetered_total_power*0.042194)/1e6)*tan_phi
        network.loads.loc['Load38', 'p_set'] = (unmetered_total_power*0.0843882)/1e6
        network.loads.loc['Load38', 'q_set'] = ((unmetered_total_power*0.0843882)/1e6)*tan_phi
        network.loads.loc['Load13', 'p_set'] = (unmetered_total_power*0.0527426)/1e6
        network.loads.loc['Load13', 'q_set'] = ((unmetered_total_power*0.0527426)/1e6)*tan_phi
        network.loads.loc['Load23', 'p_set'] = (unmetered_total_power*0.042194)/1e6
        network.loads.loc['Load23', 'q_set'] = ((unmetered_total_power*0.042194)/1e6)*tan_phi
        network.loads.loc['Load41', 'p_set'] = (unmetered_total_power*0.0527426)/1e6
        network.loads.loc['Load41', 'q_set'] = ((unmetered_total_power*0.0527426)/1e6)*tan_phi
        network.loads.loc['Load50', 'p_set'] = (unmetered_total_power*0.042194)/1e6
        network.loads.loc['Load50', 'q_set'] = ((unmetered_total_power*0.042194)/1e6)*tan_phi
        network.loads.loc['Load22', 'p_set'] = (unmetered_total_power*0.084388)/1e6
        network.loads.loc['Load22', 'q_set'] = ((unmetered_total_power*0.084388)/1e6)*tan_phi
        network.loads.loc['Load34', 'p_set'] = (unmetered_total_power*0.0527426)/1e6
        network.loads.loc['Load34', 'q_set'] = ((unmetered_total_power*0.0527426)/1e6)*tan_phi
        network.loads.loc['Load36', 'p_set'] = (unmetered_total_power*0.084388)/1e6
        network.loads.loc['Load36', 'q_set'] = ((unmetered_total_power*0.084388)/1e6)*tan_phi
        network.loads.loc['Load40', 'p_set'] = (unmetered_total_power*0.021097)/1e6
        network.loads.loc['Load40', 'q_set'] = ((unmetered_total_power*0.021097)/1e6)*tan_phi
        network.loads.loc['Load10', 'p_set'] = (unmetered_total_power*0.021097)/1e6
        network.loads.loc['Load10', 'q_set'] = ((unmetered_total_power*0.021097)/1e6)*tan_phi
        network.loads.loc['Load25', 'p_set'] = (unmetered_total_power*0.010548)/1e6
        network.loads.loc['Load25', 'q_set'] = ((unmetered_total_power*0.010548)/1e6)*tan_phi
        network.loads.loc['Load3', 'p_set'] = (unmetered_total_power*0.021097)/1e6
        network.loads.loc['Load3', 'q_set'] = ((unmetered_total_power*0.021097)/1e6)*tan_phi
        network.loads.loc['Load45', 'p_set'] = (unmetered_total_power*0.0527426)/1e6
        network.loads.loc['Load45', 'q_set'] = ((unmetered_total_power*0.0527426)/1e6)*tan_phi
        network.loads.loc['Load32', 'p_set'] = (unmetered_total_power*0.021097)/1e6
        network.loads.loc['Load32', 'q_set'] = ((unmetered_total_power*0.021097)/1e6)*tan_phi
        network.loads.loc['Load52', 'p_set'] = (unmetered_total_power*0.021097)/1e6
        network.loads.loc['Load52', 'q_set'] = ((unmetered_total_power*0.021097)/1e6)*tan_phi
        network.loads.loc['Load43', 'p_set'] = (unmetered_total_power*0.021097)/1e6
        network.loads.loc['Load43', 'q_set'] = ((unmetered_total_power*0.021097)/1e6)*tan_phi
        network.loads.loc['Load28', 'p_set'] = (unmetered_total_power*0.042194)/1e6
        network.loads.loc['Load28', 'q_set'] = ((unmetered_total_power*0.042194)/1e6)*tan_phi
        network.loads.loc['Load27', 'p_set'] = (unmetered_total_power*0.063291)/1e6
        network.loads.loc['Load27', 'q_set'] = ((unmetered_total_power*0.063291)/1e6)*tan_phi
        network.loads.loc['Load51', 'p_set'] = (unmetered_total_power*0.063291)/1e6
        network.loads.loc['Load51', 'q_set'] = ((unmetered_total_power*0.063291)/1e6)*tan_phi
 
# counter to count number of minutes
minute_counter=0
# global variables to keep records of system peak power, total power, and losses
peak_power = 65000
system_total_power = 0
system_loss_full_day = 0


def load_flow():
    global physics_meter_total_power
    global biotech_meter_total_power
    global civil_meter_total_power
    global management_meter_total_power
    global electrical_meter_total_power
    global transformer_meter_total_power

    global peak_power
    global system_total_power
    global system_loss_full_day
    global minute_counter
    # timestamp = datetime.datetime.now()

    while True:
        # perform newton Raphson Load Flow
        network.pf()

        ####################################################################
        ######################### Network Plotting #########################
        ####################################################################

        # add circles to the locations of buses in the map
        bus_v_mags = {}
        for i in range(len(bus_coords)):
            # get the bus name
            bus_name = network.buses.index.to_list()[i]
            bus_name = buses_and_lines.get_bus_names(bus_name)
            # get per unit voltage magnitude the bus
            v_mag_pu = network.buses_t.v_mag_pu.iloc[0, i]
            # get the difference from the per unit value
            V_mag_diff = abs(v_mag_pu-1.0)
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
            bus_v_mags[f'{bus_name}'] = [v_mag_pu, V_mag_diff]
    

        line_loading = {}
        total_system_loss = 0
        for index, row in network.lines.iterrows():
            # get the name of the line
            line_name = index
            # print(f"index= {index}\n type={type(index)}")
            # get active and reactive powers of the line
            line_p = network.lines_t.p0.loc['now', index ]
            line_q = network.lines_t.q0.loc['now', index ]    
            # get the starting and ending buses of each line
            bus0 = row['bus0']
            bus1 = row['bus1']
            # set line colors based on the line loading
            #assumed nominal capacity of the line (sqrt(3)*400*300/1000000 MVA)
            s_nom_assumed = 0.207846   
            # calculate the line percentage loading
            s_actual = math.sqrt(line_p**2 + line_q**2)     #actual apparent power
            # print(f"{line_name}: actual apparent power = {s_actual}")
            percentage_loading = (s_actual/s_nom_assumed)*100
            line_I = (s_actual*10e6)/(math.sqrt(3)*400.0)   #line current
            line_I = line_I/3   #per phase current
            line_R = buses_and_lines.get_line_resistance(line_name)     #line resistance
            line_loss = (line_I**2)*line_R      # power loss per line
            line_loss_3_phase = 3*line_loss     # total 3 phase power loss
            # print(f"{line_name}: current = {line_I} A, resistance = {line_R}ohm,  line loss = {line_loss_3_phase:.2f} W")
            total_system_loss = total_system_loss+line_loss_3_phase
            line_color = ''
            dash_size = ''
            show_arrow = True
            show_animation = True
            show_fault = False

            # uncomment to simulate a virtual power outage on line2_3
            # if line_name=="Line2_3":
            #     line_p = 0
            #     line_q = 0

            # uncomment to simulate a virtual fault on line4_5
            # if line_name=="Line4_7":
            #     percentage_loading = 160.0
                
            if (line_p == 0) and (line_q==0):
                # black color if no power flowing through the line
                line_color = 'black' 
                dash_size = '5, 10'
                percentage_loading = 0
                show_arrow = False
                show_animation = False
            elif (0 < percentage_loading <= 50):
                # green color if line loading is less than 50%
                line_color = 'green' 
            elif (50 < percentage_loading <= 100):
                # violet if line loading is between 50 to 100%
                line_color = 'orange' 
            elif (100 < percentage_loading <= 150):
                # red if line loading is between 100 to 150&
                line_color = 'red'
            else:
                # indicate fault if percentage loading exceeds 150%
                line_color = 'red'
                show_fault = True

            # set line weight relative to percentage loading
            line_weight = 2.0 + percentage_loading*4/100
            # tooltip text for the line
            tooltip_text = f'<span style="font-weight: bold; padding-left: 0px">{line_name}</span><br>P = {line_p*1000: .3f} kW<br>Q = {line_q*1000:.3f} kVAr<br>loading = {percentage_loading: .3f}%'
            # finally, add the line
            # latitude first then longitude
            folium.PolyLine(locations=[(network.buses.loc[bus0].y, network.buses.loc[bus0].x), 
                                    (network.buses.loc[bus1].y, network.buses.loc[bus1].x)],
                            color = line_color, weight  = line_weight,
                            dash_array = dash_size,
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

            if show_arrow:
                folium.Polygon(locations=[(y4, x4), (y3, x3), (y5, x5)],
                     color= line_color, weight=2.0,
                     fill=True, fill_color = line_color, fill_opacity=0.8).add_to(grid_layer)
              
            
            if show_animation:
                # Use AntPath for animation
                # coordinates - first latitude(y) then longitude(x)
                AntPath([(y1, x1), (y2, x2)], 
                        delay = 1200, dash_array=(3,10), 
                        color=line_color, pulse_color='#FFFFFF',
                        weight=3, opacity=1.0).add_to(animation_layer)
                
            if show_fault:
                # url of fault icon
                flash_url = 'G:\\My Drive\\D-VA\\Main Project\\Python implementation\\images\\flash2.png'

                # Coordinates for the flash icon
                flash_y = (network.buses.loc[bus0].y + network.buses.loc[bus1].y)/2
                flash_x = (network.buses.loc[bus0].x + network.buses.loc[bus1].x)/2
                flash_coords = [flash_y, flash_x]
                m_flash = (network.buses.loc[bus1].y - network.buses.loc[bus0].y)/(network.buses.loc[bus1].x-network.buses.loc[bus0].x)
                theta_flash = math.atan(m_flash)    #angle in radian
                theta_flash = theta_flash * 180/math.pi     #radian to degrees

                # Create a custom icon using the image URL
                icon = folium.CustomIcon(
                    flash_url,
                    icon_size=(70, 70),  # Size of the icon
                    icon_anchor=(35, 35),  # Position of the icon anchor relative to the icon center
                    popup_anchor=(0, -20),  # Position of the popup relative to the icon
                )

                # Add a marker with the custom icon to the map
                folium.Marker(
                    location=flash_coords,
                    icon=icon,
                    popup=f'A fault exists in {line_name}'
                ).add_to(fault_layer)
            line_loading[f"{line_name}"] = percentage_loading

        bus_v_mags = dict(sorted(bus_v_mags.items(), key=lambda item: item[1][1], reverse = True))
        for key in bus_v_mags:
            bus_v_mags[key] = bus_v_mags[key][0]
        line_loading = dict(sorted(line_loading.items(), key=lambda item: item[1], reverse = True))
        bus_html = html_contents.get_table_html(300, "Critical Buses", "Bus", "|V| pu", **bus_v_mags)
        line_html = html_contents.get_table_html(500, "Critical Lines", "Line", "% Loading", **line_loading)
        map.get_root().html.add_child(folium.Element(bus_html))
        map.get_root().html.add_child(folium.Element(line_html))

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
        system_total_power = system_total_power+transformer_meter_total_power/1000
        system_loss_full_day = system_loss_full_day+total_system_loss
        if transformer_meter_total_power > peak_power:
            print(f"peak power changed from {peak_power/1000} kW to {transformer_meter_total_power/1000} kW")
            peak_power = transformer_meter_total_power
            peak_loss = total_system_loss
            peak_timestamp = datetime.datetime.now()
        minute_counter = minute_counter+1
        print(f"total system loss = {total_system_loss/1000:.2f} kW")
        if minute_counter==(1):
            daily_average_power = system_total_power/(24*60)
            daily_peak_power = peak_power
            print(f"daily average power = {daily_average_power:.3f} kW")
            print(f"daily_peak_power = {daily_peak_power/1000} kW")
            print(f"daily peak timestamp = {peak_timestamp.strftime("%Y-%m-%d %H:%M:%S")}")
            print(f"system full day loss = {system_loss_full_day/(60.0*1000)} kWh")
            print(f"system peak loss = {peak_loss/1000:.2f} kW")
            minute_counter=0
            # reset the system total power
            system_total_power = 0
            # reset the peak power to 65 kW
            peak_power = 65000
            system_loss_full_day = 0
            

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
client.subscribe(Topic[ELECTRICAL])
client.subscribe(Topic[TRANSFORMER])

# Loop to maintain MQTT connection and process incoming messages
client.loop_forever()
