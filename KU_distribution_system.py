"""
**main python file to run the power flow of KU distribution system 

**External Grid: A generator has been modelled as an external grid, its control is set to PV

**Nomenclature
-----------------
-----------------
HVB -> High voltage Bus
LVB01 -> Low voltage Bus number 01
Line12 -> Line connected between LVB01(low voltage bus number 01) and LVB02(bus number 02) 
Load03 -> Load connected to LVB03(low voltage bus number 03)

"""

import pypsa
import pandas as pd
import matplotlib.pyplot as plt
import numpy  as np
import cartopy.crs as ccrs

grid = pypsa.Network()

# add high voltage bus
grid.add("Bus", "HVB", v_nom = 11.0)

# add low voltage buses
grid.add("Bus", "LVB01", v_nom = 0.4)
grid.add("Bus", "LVB02", v_nom = 0.4)
grid.add("Bus", "LVB03", v_nom = 0.4)

# add an external grid to the high voltage bus
# grid.add("Generator", "External Grid", bus = "HVB", control = "PV", p_set =40.0)
grid.add("Generator", "External Grid", bus = "HVB", control = "Slack")

# add a transformer between HVB and LVB1
grid.add("Transformer", "Transformer", bus0 = "HVB", bus1 = "LVB01", model = "t", x = 0.5, r = 0.5,
         s_nom = 0.25*1.25)

# add the remaining lines
grid.add("Line", "Line12", bus0 = "LVB01", bus1 = "LVB02")
grid.add("Line", "Line23", bus0 = "LVB02", bus1 = "LVB03")

# add a load to LVB03 -> Multipurpose Hall
grid.add("Load", "Load03", bus = "LVB03", p_set = 0.0621, q_set = 0.0621)

grid.pf()