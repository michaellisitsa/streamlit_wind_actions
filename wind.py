import streamlit as st

import pandas as pd
import numpy as np
from scipy.interpolate import griddata
from handcalcs import handcalc
import forallpeople as u
u.environment('structural')

from enum_vals import Regions, Cases
import helper_funcs

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from wind_multipliers import Wind_multipliers

class Wind:
    def __init__(self,render_hc,Wind_mult: 'Wind_multipliers',loadcase):
        self.render_hc = render_hc
        self.Wind_mult = Wind_mult
        self.loadcase = loadcase

# self.V_r_uls = st.sidebar.number_input("V_r_uls (m/s) (T3.1 AS1170.2)",min_value=1,max_value=60,value=46)
# self.V_r_sls = st.sidebar.number_input("V_r_sls (m/s) (T3.1 AS1170.2)",min_value=1,max_value=60,value=37)

    def st_wind_speed_inputs(self):
        st.sidebar.subheader("Select Average Recurrence Interval:")
        self.ARI = st.sidebar.number_input(f"Select ARI for {self.loadcase} Wind:",min_value = 1, max_value = 10000, value=1000, key=self.loadcase)

    def calc_regional_wind_speed(self):
        """Calculate regional wind speed based on region and ARI"""
        #Hardcode table of regional wind speeds
        self.wind_regional = pd.DataFrame({
                      'ARI':[1,5,10,20,25,50,100,200,250,500,1000,2000,2500,5000,10000],
                      'A':[30,32,34,37,37,39,41,43,43,45,46,48,48,50,51],
                      'W':[34,39,41,43,43,45,47,49,49,51,53,54,55,56,58],
                      'B':[26,28,33,38,39,44,48,52,53,57,60,63,64,67,69],
                      'C':[23,33,39,45,47,52,56,61,62,66,70,73,74,78,81],
                      'D':[23,35,43,51,43,60,66,72,74,80,85,90,91,95,99]}) #T3.1 AS1170.2
        self.wind_regional.set_index('ARI',inplace=True)

        #Multiply FC and FD factors, where >= 50 yr criteria is satisfied
        FC_C = (1.05 if self.ARI >= 50 else 1.0)
        FC_D = (1.10 if self.ARI >= 50 else 1.0) 
        self.wind_regional['C'] = np.where((self.wind_regional.index >= 50),
                                        1.05 * self.wind_regional.C,
                                        self.wind_regional.C)
        self.wind_regional['D'] = np.where((self.wind_regional.index >= 50),
                                        1.1 * self.wind_regional.D,
                                        self.wind_regional.D)
        
        #Check if ARI inputted is within wind_regional table.
        #If ARI in list get the value by region and ARI, else use equations
        if self.ARI in self.wind_regional.index:
            self.Vr = self.wind_regional.loc[self.ARI,str(self.Wind_mult.region.name)[0]]
        elif self.ARI >= 5:
            regions_A_combined = (Regions.A1, Regions.A2, Regions.A3, Regions.A4, Regions.A5, Regions.A6, Regions.A7)
            if self.Wind_mult.region in regions_A_combined:   self.Vr = round(67  - 41 * self.ARI**-0.1)
            elif self.Wind_mult.region is Regions.W:          self.Vr = round(104 - 70 * self.ARI**-0.045)
            elif self.Wind_mult.region is Regions.B:          self.Vr = round(106 - 92 * self.ARI**-0.1)
            elif self.Wind_mult.region is Regions.C:          self.Vr = round(FC_C*(122 - 104* self.ARI**-0.1))
            elif self.Wind_mult.region is Regions.D:          self.Vr = round(FC_D*(156 - 142 * self.ARI**-0.1))
            else:                                             self.Vr = None


    def st_display_regional_wind_speed(self):
        args = {'V_r':self.Vr * u.m / u.s,
                'ARI':self.ARI,
                'Category':self.Wind_mult.region.name}

        @handcalc()
        def st_display_regional_wind_speed_latex(V_r,ARI,Category):
            ARI
            Category
            V_r

        if self.render_hc: st.subheader("Regional Wind Speed:")
        st.latex(st_display_regional_wind_speed_latex(**args)[0])

        with st.beta_expander("Expand for regional wind T3.2"):
            st.table(self.wind_regional)
            st.markdown("**Category C and D have been multiplied by $F_C$ & $F_D$ where ARI >= 50")

    def calc_site_wind_speed(self):
        args = {'V_r':self.Vr * u.m / u.s,
                'M_d':self.Wind_mult.M_d,
                'M_z_cat':self.Wind_mult.M_z_cat,
                'M_s':self.Wind_mult.M_s,
                'M_t':self.Wind_mult.M_t}

        def calc_site_wind_speed_func(V_r, M_d, M_z_cat, M_s, M_t):
            V_sit_beta = V_r * M_d * (M_z_cat * M_s * M_t)
            return V_sit_beta

        #Render handcalcs (or just run equation)
        if self.render_hc: st.subheader(f"Site {self.loadcase} Wind Speed:")
        V_sit_latex, self.V_sit_beta = helper_funcs.func_by_run_type(self.render_hc, args, calc_site_wind_speed_func)
        if self.render_hc: st.latex(V_sit_latex)