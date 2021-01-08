import streamlit as st

from shapely.geometry import Polygon, MultiPolygon, LinearRing, box
import shapely

import numpy as np

from typing import List, Optional, Union
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from wind import Wind

from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, Grid, LinearAxis, Plot, Rect, Arrow, NormalHead
from bokeh.models.glyphs import Text
from bokeh.plotting import figure, output_file, show

class Geometry:
    def __init__(self,wind: 'Wind'):
        self.wind = wind
        # def __init__(self, geom: Union[shapely.geometry.Polygon, shapely.geometry.MultiPolygon]):
        # """Inits the Geometry class.
        # Old args; control_points, shift
        # """
        # self.geom = geom
        # self.control_points = [] # Given upon instantiation
        # self.shift = [] # Given upon instantiation
        # self.points = [] # Previously empty list
        # self.facets = [] # Previously empty list
        # self.holes = [] # Previously empty list
        # self.perimeter = [] # Previously empty list
        # # self.mesh = None # Previously not a property

    def st_RHS_picker(self):
        self.d = st.sidebar.number_input("Alongwind Distance of RHS",min_value=25,max_value=3000,value=300) / 1000
        self.b = st.sidebar.number_input("Crosswind Distance of RHS",min_value=25,max_value=3000,value=300) / 1000

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

    def st_RHS_plotting(self):
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
    # def sign_AASHTO_fat(self):
        

    # def exposed_

# #Helper functions
# def rectangular_section(self,b, d):
#     """Constructs a rectangular section with the bottom left corner at the origin *(0, 0)*, with
#     depth *d* and width *b*.
#     """
#     min_x = 0 - b/2
#     min_y = 0 - d/2
#     max_x = b/2
#     max_y = d/2

#     self.rectangle = box(min_x, min_y, max_x, max_y)
#     return Geometry(rectangle)
