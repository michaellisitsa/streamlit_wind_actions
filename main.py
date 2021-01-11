import streamlit as st



#Import other modules in this Streamlit script
import geometry
import wind
import wind_multipliers
from enum_vals import Regions, Cases, Directions, Significance, Wind_angle, Structure_type

render_hc = st.sidebar.checkbox("Render hand calcs", value=True)

def main():
    Wind_mult = wind_multipliers.Wind_multipliers()
    Wind_mult.st_region_inputs()
    Wind_mult.st_terrain_inputs()
    Wind_mult.terrain_multiplier()
    Wind_mult.st_wind_multipliers_input()
    Wind_mult.st_wind_direction_inputs()
    Wind_mult.calc_wind_direction_multiplier()
    Wind_mult.render_multipliers()

    Wind_ULS = wind.Wind(render_hc,Wind_mult,Cases.ULS)
    Wind_ULS.st_wind_speed_inputs()
    Wind_ULS.calc_regional_wind_speed()
    Wind_ULS.st_display_regional_wind_speed()
    Wind_ULS.calc_site_wind_speed()

    Wind_SLS = wind.Wind(render_hc,Wind_mult,Cases.SLS)
    Wind_SLS.st_wind_speed_inputs()
    Wind_SLS.calc_regional_wind_speed()
    Wind_SLS.calc_site_wind_speed()

    Geom = geometry.Geometry(Wind_ULS)
    Geom.st_geom_picker()
    if Geom.structure_type is Structure_type.RHS:
        Geom.exposed_RHS_AS1170()
        plot_RHS = Geom.st_RHS_plotting()
        st.bokeh_chart(plot_RHS,False)
    elif Geom.structure_type is Structure_type.CHS:
        Geom.exposed_CHS_AS1170()
    elif Geom.structure_type is Structure_type.SIGN:
        Geom.calc_sign_AS1170()
        Geom.calc_wind_pressure()
        plot_sign = Geom.st_plot_wind_pressure()
        st.bokeh_chart(plot_sign,False)

if __name__ == '__main__':
    main()