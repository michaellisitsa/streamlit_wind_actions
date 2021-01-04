import streamlit as st

import pandas as pd
import numpy as np

from enum_vals import Regions, Cases

class Wind:
    def __init__(self):
        pass

# self.V_r_uls = st.sidebar.number_input("V_r_uls (m/s) (T3.1 AS1170.2)",min_value=1,max_value=60,value=46)
# self.V_r_sls = st.sidebar.number_input("V_r_sls (m/s) (T3.1 AS1170.2)",min_value=1,max_value=60,value=37)

    def st_wind_speed_inputs(self,case: Cases):
        self.region = Regions[st.sidebar.selectbox("Select Wind Region",[r.name for r in Regions])]
        self.ARI = st.sidebar.number_input("Select ARI for ULS Wind:",min_value = 1, max_value = 10000, value=1000)

    def regional_wind_speed(self):
        """Calculate regional wind speed based on region and ARI"""
        #Hardcode table of regional wind speeds
        wind_regional = pd.DataFrame({
                      'ARI':[1,5,10,20,25,50,100,200,250,500,1000,2000,2500,5000,10000],
                      'A':[30,32,34,37,37,39,41,43,43,45,46,48,48,50,51],
                      'W':[34,39,41,43,43,45,47,49,49,51,53,54,55,56,58],
                      'B':[26,28,33,38,39,44,48,52,53,57,60,63,64,67,69],
                      'C':[23,33,39,45,47,52,56,61,62,66,70,73,74,78,81],
                      'D':[23,35,43,51,43,60,66,72,74,80,85,90,91,95,99]}) #T3.1 AS1170.2
        wind_regional.set_index('ARI',inplace=True)

        #Multiply FC and FD factors, where >= 50 yr criteria is satisfied
        FC_C = (1.05 if self.ARI >= 50 else 1.0)
        FC_D = (1.10 if self.ARI >= 50 else 1.0) 
        wind_regional['C'] = np.where((wind_regional.index >= 50),
                                        1.05 * wind_regional.C,
                                        wind_regional.C)
        wind_regional['D'] = np.where((wind_regional.index >= 50),
                                        1.1 * wind_regional.D,
                                        wind_regional.D)
        
        #Check if ARI inputted is within wind_regional table.
        st.dataframe(wind_regional)
        #If ARI in list get the value by region and ARI, else use equations
        if self.ARI in wind_regional.index:
            self.Vr = wind_regional.loc[self.ARI,str(self.region.name)[0]]
            st.write(self.Vr)
        elif self.ARI >= 5:
            regions_A_combined = (Regions.A1, Regions.A2, Regions.A3, Regions.A4, Regions.A5, Regions.A6, Regions.A7)
            if self.region in regions_A_combined:   self.Vr = round(67  - 41 * self.ARI**-0.1)
            elif self.region is Regions.W:          self.Vr = round(104 - 70 * self.ARI**-0.045)
            elif self.region is Regions.B:          self.Vr = round(106 - 92 * self.ARI**-0.1)
            elif self.region is Regions.C:          self.Vr = round(FC_C*(122 - 104* self.ARI**-0.1))
            elif self.region is Regions.D:          self.Vr = round(FC_D*(156 - 142 * self.ARI**-0.1))
            else:                                   self.Vr = None
            st.write(self.Vr)
        
    def st_wind_multipliers_input(self):
        self.M_d = st.sidebar.number_input("M_d (T3.2 AS1170.2)",min_value=1,max_value=60,value=37)
        self.M_zcat = st.sidebar.number_input("M_z_cat (m/s)",min_value=1,max_value=60,value=37)
        self.M_zcat = st.sidebar.number_input("V_r_sls (m/s)",min_value=1,max_value=60,value=37)
        self.M_zcat = st.sidebar.number_input("V_r_sls (m/s)",min_value=1,max_value=60,value=37)