
# DVAGrid

DVAGrid is a platform for real-time geographical visualization of electricity distribution grids. It is created using the open source toolboxes of Python. 

This project is currently maintained by the Distribution Visualization and Automation [(D-VA)](https://dva.ku.edu.np/) group at the Department of Electrical and Electronics Engineering, [Kathmandu University](https://ku.edu.np/). 




## Workflow
1. ku_grid_model.py contains the model of the distribution system of Kathmandu University. 
2. Several smart meters installed at the premises of Kathmandu University continuously measure and send data to the cloud every minute.
3. The main python file extracts data from cloud using the MQTT protocol and converts it into JSON format. 
4. Every minute, the main program runs a power flow simulation of the model using new data and calculates voltage magnitude, phase angle, power flow through lines, and line percentage loadings.
5. The main program then generates a web file containing the geographic map of the distribution grid along with its near real-time status. 
## Screenshots

![complete map](https://github.com/DVA-Code/Distribution-System-Visualization/assets/95348489/d465653c-bc75-48da-b257-2263bba0c68a)
![line tool tip](https://github.com/DVA-Code/Distribution-System-Visualization/assets/95348489/bcb382cd-9cf3-47e1-9619-30d16e94c552)
![bus pop up](https://github.com/DVA-Code/Distribution-System-Visualization/assets/95348489/3c9779b9-45a0-42d0-926f-f30cfbe78967)



## Dependencies
DVAGrid relies on the following Python packages:
* [PyPSA](https://pypsa.org/) for network modelling and power flow calculations.
* [Folium](https://pypi.org/project/folium/) for creating static and dynamic visualizations.
* [paho-mqtt](https://pypi.org/project/paho-mqtt/) to retrieve smart meter data from the cloud.
