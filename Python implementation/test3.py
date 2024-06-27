import folium

# Create a map centered at a location
mymap = folium.Map(location=[51.5074, -0.1278], zoom_start=12)

# Example custom icon image URL
icon_url = 'G:\\My Drive\\D-VA\\Main Project\\Python implementation\\images\\flash2.png'

# Coordinates for the marker (example coordinates)
marker_coords = [51.5074, -0.1278]

# Create a custom icon using the image URL
icon = folium.CustomIcon(
    icon_url,
    icon_size=(50, 50),  # Size of the icon
    icon_anchor=(25, 50),  # Position of the icon anchor relative to the icon center
    popup_anchor=(0, -20)  # Position of the popup relative to the icon
)

# Add a marker with the custom icon to the map
folium.Marker(
    location=marker_coords,
    icon=icon,
    popup='Custom Icon Marker'
).add_to(mymap)

# Display the map
mymap.save('map_with_custom_icon.html')
