import streamlit as st

from enum_vals import Regions, Cases, Directions, Significance, Wind_angle, Structure_type
import helper_funcs

from math import log10

import numpy as np
from handcalcs import handcalc
import forallpeople as u
u.environment('structural')

from typing import List, Optional, Union
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from wind import Wind

from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, Grid, LinearAxis, Plot, Rect, Arrow, NormalHead, Line, Range1d, Band, Span
from bokeh.models.glyphs import Text
from bokeh.plotting import figure, output_file, show

class Geometry:
    def __init__(self,wind: 'Wind'):
        '''
        Inherit Wind (where site wind speed is stored)
        Set up some other values to be used below
        '''
        self.wind = wind
        self.psf_to_kPa = 0.04788 #Conversion factor to kPa pressure
        self.I_f = 1.0 #Importance factor assumed as 1
        #Dynamic factor assumed as 1.0 until further dynamic analysis is completed
        #Further assessment is required in accordance with Sec 6 AS1170.2-2011
        #to determine the C_dyn value to be used for gantries where <1Hz nat freq.
        self.C_dyn = 1.0 

    def st_geom_picker(self):
        st.sidebar.subheader("Structure Type")
        self.structure_type = Structure_type[st.sidebar.selectbox("Type of Structure:",[s.name for s in Structure_type])]
        if self.structure_type is Structure_type.RHS:
            self.d = st.sidebar.number_input("Alongwind Distance of RHS",min_value=25,max_value=3000,value=300) / 1000
            self.b = st.sidebar.number_input("Crosswind Distance of RHS",min_value=25,max_value=3000,value=300) / 1000
        elif self.structure_type is Structure_type.CHS:
            self.d = st.sidebar.number_input("Alongwind Distance of RHS",min_value=25,max_value=3000,value=300) / 1000
            self.b = st.sidebar.number_input("Crosswind Distance of RHS",min_value=25,max_value=3000,value=300) / 1000
        elif self.structure_type is Structure_type.SIGN:
            st.sidebar.subheader("Sign Size and Direction")
            self.sign_h = st.sidebar.number_input("Height of Signboard (mm)",min_value=100,max_value=10000,value=2000) / 1000
            self.sign_w = st.sidebar.number_input("Width of Signboard (mm)",min_value=100,max_value=20000,value=2000) / 1000
            self.wind_angle = Wind_angle[st.sidebar.selectbox("Wind Angle to Structure",[a.name for a in Wind_angle])]
            self.solidity = st.sidebar.number_input("Solidity Ratio of the structure (Ratio solid area to total area):",min_value = 0.1, max_value=1.0,value = 1.0)

    def exposed_RHS_AS1170(self):
        """Crosswind coefficient - Figure E2(B)AS1170.2-2011"""
        aspect_Cfy_box = np.array([0.5, 1.5, 2.5, 4, 20, 50]) 
        Cfy_box = np.array([1.2, 0.8, 0.6, 0.8, 1, 1]) #C_fy values in Fig E2B

        '''Aerodynamic Drag Factor'''
        #Get values from Figure E2(A) AS1170.2-2011 and linearly interpolate
        aspect_Cfx_box = np.array([0.1, 0.65, 1, 2, 4, 10]) 
        Cfx_box = np.array([2.2, 3, 2.2, 1.6, 1.3, 1.1]) #C_fx values in Fig E2A

        # d (alongwind distance) / b (crosswind distance)
        #Get the C_fy_vals intercept for d/b ratio provided
        self.Cf_x = np.interp(self.d/self.b,aspect_Cfx_box,Cfx_box)
        self.Cf_y = np.interp(self.d/self.b,aspect_Cfy_box,Cfy_box)
        st.text(f'Alongwind drag factor is: {self.Cf_x:.2f}\n'
                 f'Crosswind drag factor is: {self.Cf_y:.2f}')

    def exposed_CHS_AS1170(self):
        if self.b * self.wind.V_sit_beta < 4:
            C_d = 1.2
        elif 4 < self.b * self.wind.V_sit_beta.value < 10:
            gradient = (1.2-0.6)/(10-4)
            C_d = 1.2 - gradient * (self.b * self.wind.V_sit_beta.value - 4)
        elif self.b * self.wind.V_sit_beta > 10:
            h_r = 30e-6
            C_d = max(0.6, 1.0 + 0.033 * log10(self.wind.V_sit_beta.value * h_r) - 0.025 * (log10(self.wind.V_sit_beta.value * h_r))**2)
        else:
            C_d = 1.2
        self.C_fig = C_d

    def st_RHS_plotting(self):
        """
        Plot the drag factors on a sharp cornered rectanglar exposed member
        """
        plot = Plot(title=None,match_aspect=True)
        glyph = Rect(x=0,y=0,width=self.d, height = self.b, fill_color = "#cab2d6")
        plot.add_glyph(glyph)
        plot.add_layout(Arrow(end=NormalHead(fill_color="orange"),
                        x_start=0, y_start=self.b/4, x_end=0, y_end=self.b/2))
        plot.add_layout(Arrow(end=NormalHead(fill_color="orange"),
                        x_start=-self.d/2,y_start=0, x_end=-self.d/4, y_end=0))
        plot.add_layout(LinearAxis(),'below')
        plot.add_layout(LinearAxis(),'left')
        plot.add_glyph(Text(x=0,y=self.b/2,text=[f"Cf_y = {self.Cf_y:.2f}"],text_align="left"))
        plot.add_glyph(Text(x=-self.d/4,y=0,text=[f"Cf_x = {self.Cf_x:.2f}"],text_align="left"))
        return plot
 
    def calc_sign_AS1170(self):
        """
        Calculate the drag factor C_pn for a sign in accordance with AS1170 hoardings App D2
        """
        b = self.sign_w
        c = self.sign_h
        h = self.wind.Wind_mult.height
        if self.wind_angle is Wind_angle.NORMAL:
            e = 0
            if c/h < 0.2:
                def C_pn_func(b,c,h,dist):
                    C_pn = 1.4 + 0.3 * log10(b/c)
                    return C_pn
            elif c/h > 1.0:
                raise RuntimeError("Sign cannot be taller than top of sign height")
            elif b/c < 0.5:
                raise RuntimeError("Standard does not cover sign more than twice as tall as it is wide")
            elif 0.5 <= b/c <= 5:
                def C_pn_func(b,c,h,dist):
                    C_pn = 1.3 + 0.5 * ( 0.3 + log10(b/c)) * (0.8 - c/h)
                    return C_pn
            elif b/c > 5:
                def C_pn_func(b,c,h,dist):
                    C_pn = 1.7 - 0.5 * c/h
                    return C_pn
        elif self.wind_angle is Wind_angle.ANGLE_45:
            if b/c < 0.5:
                raise RuntimeError("Standard does not cover sign more than twice as tall as it is wide")
            elif 0.5 <= b/c <= 5:
                e = 0.2 * b
                if c/h < 0.2:
                    def C_pn_func(b,c,h,dist):
                        C_pn = 1.4 + 0.3 * log10(b/c)
                        return C_pn
                elif 0.2 <= c/h <= 1.0:
                    def C_pn_func(b,c,h,dist):
                        C_pn = 1.3 + 0.5 * ( 0.3 + log10(b/c)) * (0.8 - c/h)
                        return C_pn
                    e = 0.2 * b
            elif b/c > 5:
                e = 0
                if c/h <= 0.7:
                    def C_pn_func(b,c,h,dist):
                        if dist <= 2 * c: C_pn = 3.0
                        elif b - dist <= 2 * c: C_pn = 3.0
                        elif 2 * c < dist <= 4 * c: C_pn = 1.5
                        elif 2 * c < b - dist <= 4 * c: C_pn = 1.5
                        elif dist > 4 * c: C_pn = 0.75
                        elif b - dist > 4 * c: C_pn = 0.75
                        return C_pn
                elif c/h > 0.7:
                    def C_pn_func(b,c,h,dist):
                        if dist <= 2 * h:C_pn = 2.4
                        elif b - dist <= 2 * h:C_pn = 2.4
                        elif 2 * h < dist <= 4 * h:C_pn = 1.2
                        elif 2 * h < b - dist <= 4 * h:C_pn = 1.2
                        elif dist > 4 * h:C_pn = 0.6
                        elif b - dist > 4 * h:C_pn = 0.6                        
                        return C_pn
        elif self.wind_angle is Wind_angle.PARALLEL:
            e = 0
            if c/h <= 0.7:
                def C_pn_func(b,c,h,dist):
                    if dist <= 2 * c: C_pn = 1.2
                    elif b - dist <= 2 * c: C_pn = 1.2
                    elif 2 * c < dist <= 4 * c: C_pn = 0.6
                    elif 2 * c < b - dist <= 4 * c: C_pn = 0.6
                    elif dist > 4 * c: C_pn = 0.3
                    elif b - dist > 4 * c: C_pn = 0.3
                    return C_pn
            elif c/h > 0.7:
                def C_pn_func(b,c,h,dist):
                    if dist <= 2 * h:C_pn = 1.0
                    elif b - dist <= 2 * h:C_pn = 1.0
                    elif dist >= 2 * h:C_pn = 0.25
                    elif b - dist >= 2 * h:C_pn = 0.25                  
                    return C_pn
        # len = st.slider("dist along sign",0.0,b,b/2.0,step=b/10.0)
        self.C_pn_func = C_pn_func

        dist = (st.slider("dist along sign",0.0,b,b/2.0,step=b/10.0) if self.wind.Wind_mult.render_hc else 0)

        args = {'b':self.sign_w,
                'c':self.sign_h,
                'h':self.wind.Wind_mult.height,
                'dist':dist}

        C_pn_latex, self.C_pn = helper_funcs.func_by_run_type(self.wind.Wind_mult.render_hc, args, C_pn_func)

        if self.wind.Wind_mult.render_hc:
            st.subheader(f"Wind angle = {self.wind_angle.name}")
            st.subheader(f"b/c = {b/c:.2f}, c/h = {c/h:.2f}")
            st.subheader(f"e = {e:.2f}")
            st.latex(C_pn_latex)
        else:
            st.subheader("")

    def calc_wind_pressure_sign(self):
        """
        Calculate wind pressure for a single point along the sign.
        Where 45 deg and large aspect ratio, a slider will be used to show the values at a particular dist along the sign
        """
        args = {'C_pn':self.C_pn,
                'delta':self.solidity,
                'V_des_theta':self.wind.V_sit_beta.value,
                'C_dyn':self.C_dyn}

        def calc_C_fig_func(C_pn,delta,V_des_theta,C_dyn):
            K_p = 1 - (1 - delta)**2
            C_fig = C_pn * K_p
            gamma_air = 1.2 #kg per m3 as per Cl 2.4.1
            sigma_wind = 0.5 * gamma_air * V_des_theta**2 * C_fig * C_dyn #Pa
            return C_fig, K_p, sigma_wind

        C_fig_latex, (self.C_fig, self.K_p, self.sigma_wind) = helper_funcs.func_by_run_type(self.wind.Wind_mult.render_hc, args, calc_C_fig_func)
        if self.wind.Wind_mult.render_hc: st.latex(C_fig_latex)

    def calc_wind_pressure_HS(self):
        """
        Calculate wind pressure for a single point along the sign.
        Where 45 deg and large aspect ratio, a slider will be used to show the values at a particular dist along the sign
        """
        args = {'C_fig':self.C_fig,
                'V_des_theta':self.wind.V_sit_beta.value,
                'C_dyn':self.C_dyn}

        def calc_C_fig_func(C_fig,V_des_theta,C_dyn):
            gamma_air = 1.2 #kg per m3 as per Cl 2.4.1
            sigma_wind = 0.5 * gamma_air * V_des_theta**2 * C_fig * C_dyn #Pa
            return sigma_wind

        C_fig_latex, self.sigma_wind = helper_funcs.func_by_run_type(self.wind.Wind_mult.render_hc, args, calc_C_fig_func)
        if self.wind.Wind_mult.render_hc: st.latex(C_fig_latex)

    def st_plot_wind_pressure(self):
        """
        Plot wind pressure along the sign face.
        The value may change for 45 degrees and a large aspect ratio.
        """
        #Set up plot
        plot = Plot()

        #Graph of Drag Factors along sign
        x = np.linspace(0,self.sign_w,num=50)
        y = [0.5 * 1.2 * self.wind.V_sit_beta.value**2 * self.C_dyn * self.K_p / 1000 * self.C_pn_func(self.sign_w, self.sign_h,self.wind.Wind_mult.height,ix) for ix in x ]
        source = ColumnDataSource(dict(x=x, y=y))
        drag_factor = Line(x='x',y='y',line_color = "#f46d43", line_width=3)
        plot.add_glyph(source, drag_factor)

        #Fille area under line
        fill_under = Band(base='x',upper='y',source=source, level='underlay',fill_color = '#55FF88')
        plot.add_layout(fill_under)

        #Plot setup
        plot.add_layout(LinearAxis(),'below')
        plot.add_layout(LinearAxis(),'left')
        plot.xaxis.axis_label = "Distance along sign (m)"
        plot.yaxis.axis_label = "Wind Pressure (kPa)"
        plot.y_range = Range1d(0, max(y)*1.3)

        return plot