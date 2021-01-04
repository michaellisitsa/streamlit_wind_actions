import streamlit as st

import pandas as pd
import numpy as np
from scipy.interpolate import griddata

from enum_vals import Regions, Cases
import helper_funcs

class Wind_multipliers:
    def __init__(self):
        pass

    def st_wind_speed_inputs(self):
        self.region = Regions[st.sidebar.selectbox("Select Wind Region",[r.name for r in Regions])]

    def st_terrain_inputs(self):
        self.height = st.sidebar.number_input("Height of Wind Loading centre: (m)",min_value = 0., max_value = 200., value=0.)
        self.terrain_category = st.sidebar.number_input("Terrain Category (halves allowed): (T4.2 AS1170.2)",min_value = 1., max_value = 4., value=1.,step=0.5)

    def terrain_multiplier(self):
        """Calculate regional wind speed based on region and ARI"""
        #Hardcode table of terrain multipliers
        terrain_table = pd.DataFrame({
                      'height':[0,3,5,10,15,20,30,40,50,75,100,150,200],
                      '1':[0.99, 0.99, 1.05, 1.12, 1.16, 1.19, 1.22, 1.24, 1.25, 1.27, 1.29, 1.31, 1.32],
                      '2':[0.91, 0.91, 0.91, 1.00, 1.05, 1.08, 1.12, 1.16, 1.18, 1.22, 1.24, 1.27, 1.29],
                      '3':[0.83, 0.83, 0.83, 0.83, 0.89, 0.94, 1.00, 1.04, 1.07, 1.12, 1.16, 1.21, 1.24],
                      '4':[0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.80, 0.85, 0.90, 0.98, 1.03, 1.11, 1.16]}) #T4.1 AS1170.2
        terrain_table.set_index('height',inplace=True)

        #2d interpolation of Table 4.1 AS1170.2.
        #Terrain Categories may be halves (e.g Category 1.5)
        #Heights may be any value
        #https://stackoverflow.com/questions/56291133/interpolation-of-a-pandas-dataframe
        terrain_stacked = terrain_table.stack().reset_index().values

        st.dataframe(terrain_table)
        self.M_z_cat = griddata(terrain_stacked[:,0:2],
                terrain_stacked[:,2],
                [(self.height, self.terrain_category)],
                method='linear')[0]
        st.write(f"The interpolated value is: {self.M_z_cat}")
        
    def st_wind_multipliers_input(self):
        """Custom values to be calculated separately"""
        self.M_s = st.sidebar.number_input("Shielding Multiplier (M_s)",min_value=0.7,max_value=1.0,value=1.0,step=0.05)
        self.M_t = st.sidebar.number_input("Topographic Multiplier (M_t)",min_value=1.0,max_value=2.0,value=1.0,step=0.05)
        self.M_d = st.sidebar.number_input("Wind Direction Multiplier (M_d)",min_value=0.80,max_value=1.0,value=1.0,step=0.05)