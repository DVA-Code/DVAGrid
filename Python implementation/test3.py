import folium


# Example custom icon image URL
icon_url = 'G:\\My Drive\\D-VA\\Main Project\\Python implementation\\images\\flash2.png'

# Coordinates for the marker (example coordinates)
dhulikhel_coords = [27.620688626572516, 85.5400761719249]
ratnapark_coords = [27.70701844032609, 85.31576914113714]
melamchi_coords = [27.84410843281709, 85.58663254173096]

y = (dhulikhel_coords[0] + ratnapark_coords[0])/2
x = (dhulikhel_coords[1] + ratnapark_coords[1])/2
marker_coords = [y, x]

html = '<div style="transform: rotate(45deg);"><img src="{}" style="width: 50px; height: 50px;"></div>'.format(icon_url)

# Create a map centered at a location
mymap = folium.Map(location=marker_coords, zoom_start=12)

# add a line
folium.PolyLine(locations=[dhulikhel_coords, ratnapark_coords],color = 'red').add_to(mymap)

# Create a custom icon using the image URL
icon = folium.CustomIcon(
    icon_url,
    icon_size=(50, 50),  # Size of the icon
    icon_anchor=(25, 25),  # Position of the icon anchor relative to the icon center
    popup_anchor=(0, -20)  # Position of the popup relative to the icon
)

# Add a marker with the custom icon to the map
folium.Marker(
    location=marker_coords,
    icon=folium.DivIcon(html=html),
    popup='Custom Icon Marker'
).add_to(mymap)

# Display the map
mymap.save('map_with_custom_icon.html')
