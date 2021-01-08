import streamlit as st

import pandas as pd
import numpy as np
from scipy.interpolate import griddata

from enum_vals import Regions, Cases, Directions, Significance
import helper_funcs

from handcalcs import handcalc
import forallpeople as u
u.environment('structural')

class Wind_multipliers:
    def __init__(self):
        pass

    def st_region_inputs(self):
        st.sidebar.subheader("Select Wind Region (used for $V_r$ calculation):")
        self.region = Regions[st.sidebar.selectbox("Select Wind Region",[r.name for r in Regions])]

    def st_wind_direction_inputs(self):
        st.sidebar.subheader("Select Wind Direction Parameters (used for $M_d$ calculation):")
        self.wind_direc = Directions[st.sidebar.selectbox("Select Wind Direction Cl 3.3",[r.name for r in Directions])]
        self.significance = Significance[st.sidebar.selectbox("Select structure significance Cl 3.3.2",[s.name for s in Significance])]

    def st_terrain_inputs(self):
        st.sidebar.subheader("Inputs for $M_{z,cat}$ - Terrain Multiplier")
        self.height = st.sidebar.number_input("Height of Wind Loading centre: (m)",min_value = 0., max_value = 200., value=0.)
        self.terrain_category = st.sidebar.number_input("Terrain Category (halves allowed): (T4.2 AS1170.2)",min_value = 1., max_value = 4., value=1.,step=0.5)

    def terrain_multiplier(self):
        """Calculate regional wind speed based on region and ARI"""
        #Hardcode table of terrain multipliers
        self.terrain_table = pd.DataFrame({
                      'height': [0.00, 3.00, 5.00, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 75.0, 100., 150., 200.],
                      '1':      [0.99, 0.99, 1.05, 1.12, 1.16, 1.19, 1.22, 1.24, 1.25, 1.27, 1.29, 1.31, 1.32],
                      '2':      [0.91, 0.91, 0.91, 1.00, 1.05, 1.08, 1.12, 1.16, 1.18, 1.22, 1.24, 1.27, 1.29],
                      '3':      [0.83, 0.83, 0.83, 0.83, 0.89, 0.94, 1.00, 1.04, 1.07, 1.12, 1.16, 1.21, 1.24],
                      '4':      [0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.80, 0.85, 0.90, 0.98, 1.03, 1.11, 1.16]}) #T4.1 AS1170.2
        self.terrain_table.set_index('height',inplace=True)

        terrain_stacked = self.terrain_table.stack().reset_index().values

        #2d interpolation of Table 4.1 AS1170.2.
        #Terrain Categories may be halves (e.g Category 1.5)
        #Heights may be any value
        #https://stackoverflow.com/questions/56291133/interpolation-of-a-pandas-dataframe
        self.M_z_cat = griddata(terrain_stacked[:,0:2],
                                terrain_stacked[:,2],
                                [(self.height, self.terrain_category)],
                                method='linear')[0]
        
    def st_wind_multipliers_input(self):
        """Custom values to be calculated separately"""
        st.sidebar.subheader("Wind Speed Multipliers (manual entry)")
        self.M_s = st.sidebar.number_input("Shielding Multiplier (M_s)",min_value=0.7,max_value=1.0,value=1.0,step=0.05)
        self.M_t = st.sidebar.number_input("Topographic Multiplier (M_t)",min_value=1.0,max_value=2.0,value=1.0,step=0.05)

    def calc_wind_direction_multiplier(self):
            """Calculate regional wind speed based on region and ARI"""
            #Hardcode table of regional wind speeds
            self.directions_table = pd.DataFrame({
                        'Direction':['ANY','N', 'NE',  'E',  'SE', 'S',  'SW', 'W',  'NW'],
                        'A1':       [1.00, 0.90, 0.80, 0.80, 0.80, 0.85, 0.95, 1.00, 0.95],
                        'A2':       [1.00, 0.80, 0.80, 0.80, 0.95, 0.90, 0.95, 1.00, 0.95],
                        'A3':       [1.00, 0.85, 0.80, 0.80, 0.80, 0.80, 0.85, 0.90, 1.00],
                        'A4':       [1.00, 0.90, 0.85, 0.90, 0.90, 0.95, 0.95, 0.95, 0.90],
                        'A5':       [1.00, 1.00, 0.85, 0.80, 0.80, 0.85, 0.90, 1.00, 0.95],
                        'A6':       [1.00, 0.85, 0.95, 1.00, 0.95, 0.85, 0.95, 1.00, 0.95],
                        'A7':       [1.00, 0.90, 0.90, 0.80, 0.90, 0.90, 0.90, 1.00, 1.00],
                        'W':        [1.00, 1.00, 0.95, 0.80, 0.90, 1.00, 1.00, 0.90, 0.95]})
            self.directions_table.set_index('Direction',inplace=True)

            for i in ['B','C','D']:
                self.directions_table[i] = np.where((self.significance is Significance.MAJOR),
                                                0.95,
                                                1.0)

            #Check if ARI inputted is within wind_regional table.
            #If ARI in list get the value by region and ARI, else use equations
            self.M_d = self.directions_table.loc[self.wind_direc.name,self.region.name]

    def render_multipliers(self):
        args = {'height':self.height * u.m,
                'terrain_category':self.terrain_category,
                'M_z_cat':self.M_z_cat,
                'significance':self.significance.name,
                'wind_direction':self.wind_direc.name,
                'M_s':self.M_s,
                'M_t':self.M_t,
                'M_d':self.M_d}

        @handcalc()
        def render_multipliers_func(height,terrain_category,M_z_cat,M_s,M_t,M_d,significance,wind_direction):
            height #Height at which M\_z\_cat taken in T4.2
            terrain_category #Terrain type used in T4.2
            M_z_cat #Refer details in M\_z\_cat Interpolation note below
            M_s
            M_t
            significance
            wind_direction
            M_d

        with st.beta_expander("Expand for Terrain Multiplier Table T4.2"):
            st.table(self.terrain_table)

        with st.beta_expander("Expand for Wind Direction Multiplier Table T3.2"):        
            st.table(self.directions_table)


        st.subheader("Site Wind Speed multipliers:")
        multipliers_latex = render_multipliers_func(**args)
        st.latex(multipliers_latex[0])
        st.markdown("""
        #### $M_{z,cat}$ Interpolation:
        M_z_cat is calculated from T4.2. Interpolation using scipy.interpolate.griddata
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html
        Interpolation is linear, and values are rounded to the nearest integer as required in code
        """)
