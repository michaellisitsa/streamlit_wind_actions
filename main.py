import streamlit as st



#Import other modules in this Streamlit script
import geometry
import wind
import wind_multipliers
from enum_vals import Regions, Cases, Directions, Significance, Wind_angle, Structure_type

render_hc = st.sidebar.checkbox("Render hand calcs", value=True)
loadcase = Cases[st.sidebar.selectbox("Select loadcase:",[l.name for l in Cases])]
def main():
    Wind_mult = wind_multipliers.Wind_multipliers(render_hc)
    Wind_mult.st_region_inputs()
    Wind_mult.st_terrain_inputs()
    Wind_mult.terrain_multiplier()
    Wind_mult.st_wind_multipliers_input()
    Wind_mult.st_wind_direction_inputs()
    Wind_mult.calc_wind_direction_multiplier()
    Wind_mult.render_multipliers()

    Wind = wind.Wind(Wind_mult,loadcase)
    Wind.st_wind_speed_inputs()
    Wind.calc_regional_wind_speed()
    Wind.st_display_regional_wind_speed()
    Wind.calc_site_wind_speed()

    Geom = geometry.Geometry(Wind)
    Geom.st_geom_picker()
    if Geom.structure_type is Structure_type.RHS:
        Geom.calc_drag_RHS_AS1170()
        Geom.calc_wind_pressure_RHS()
        plot_RHS = Geom.st_RHS_plotting()
        st.bokeh_chart(plot_RHS,False)
    elif Geom.structure_type is Structure_type.CHS:
        Geom.calc_drag_CHS_AS1170()
        Geom.calc_wind_pressure_CHS()
    elif Geom.structure_type is Structure_type.SIGN:
        Geom.calc_sign_AS1170()
        Geom.calc_wind_pressure_sign()
        plot_sign = Geom.st_plot_wind_pressure()
        st.bokeh_chart(plot_sign,False)

if __name__ == '__main__':
    main()