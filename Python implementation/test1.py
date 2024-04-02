import pypsa
import pandas as pd
import matplotlib.pyplot as plt
import numpy  as np
import math
import folium
import ku_grid


network = ku_grid.create_network()

# path to save map
MAP_PATH = r"G:\My Drive\D-VA\Main Project\Python implementation\ku_grid.html"

# create a map object
map = folium.Map(location=(27.619013147338894, 85.5387356168638), 
                    zoom_start=17, max_zoom=30)

# add a layer to plot the distribution grid
grid_layer = folium.FeatureGroup(name='Grid Layer').add_to(map)
# folium.LayerControl().add_to(map)

# get coordinates of all the buses in the network
bus_coords = []
for index, row in network.buses.iterrows():
#     first latitude then longitude as folium expects location in this order
    bus_coords.append([row['y'], row['x']])

# perform newton Raphson Load Flow
network.pf()

# add circles to the locations of buses in the map
for i in range(len(bus_coords)):
    # get the bus name
    bus_name = network.buses.index.to_list()[i]
    # get per unit voltage magnitude the bus
    # show bus voltage magnitude and voltage angle on the popup 
    # popup_text = f'<span style="font-weight:bold; padding-left:20px;">{bus_name}</span><br>|V| = {v_mag_pu: .3f} p.u.<br>δ = {v_ang_deg: .3f} deg'
    folium.Circle(location=bus_coords[i], radius=3.0, 
                stroke=False,
                fill=True, fill_color= 'red', fill_opacity=1.0,
                ).add_to(grid_layer)


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

    # tooltip text for the line
    # tooltip_text = f'<span style="font-weight: bold; padding-left: 0px">{line_name}</span><br>P = {line_p: .3f} MW<br>Q = {line_q:.3f} MVAr<br>loading = {percentage_loading: .3f}%'
    # finally, add the line
    # latitude first then longitude
    folium.PolyLine(locations=[(network.buses.loc[bus0].y, network.buses.loc[bus0].x), 
                            (network.buses.loc[bus1].y, network.buses.loc[bus1].x)],
                    color = 'red', weight= 8.0 ).add_to(grid_layer)
    
    x1, y1 = network.buses.loc[bus0].x, network.buses.loc[bus0].y 
    x2, y2 = network.buses.loc[bus1].x, network.buses.loc[bus1].y
    x3, y3 = (x1+x2)/2, (y1+y2)/2
    m = (y2-y1)/(x2-x1)
    l = math.sqrt(pow(x2-x1, 2) + pow(y2-y1, 2))
    al = l/8
    print(f'{line_name}: slope = {m}  & length = {l}')
    theta = math.atan(m)
    theta = abs(theta)
    phi = math.pi/8
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

    folium.Polygon(locations=[(y4, x4), (y3, x3), (y5, x5)],
                     color='green', weight=2.0,
              fill=True, fill_color='green', fill_opacity=0.8).add_to(grid_layer)
    

# add a line between HVB and LVB1 as PyPSA doesn't create a line between the buses if there is a transformer in between
folium.PolyLine(locations=[(network.buses.loc['HVB'].y, network.buses.loc['HVB'].x), 
                            (network.buses.loc['LVB1'].y, network.buses.loc['LVB1'].x)],
                        color = 'black').add_to(grid_layer)

# save the geomap of the network in an html file
map.save(MAP_PATH)




