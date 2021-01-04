import streamlit as st



#Import other modules in this Streamlit script
import geometry
import wind
import wind_multipliers
from enum_vals import Regions, Cases, Directions, Significance

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

    Wind_ULS = wind.Wind(render_hc,Wind_mult,'ULS')
    Wind_ULS.st_wind_speed_inputs()
    Wind_ULS.calc_regional_wind_speed()
    Wind_ULS.st_display_regional_wind_speed()
    Wind_ULS.calc_site_wind_speed()

    Wind_SLS = wind.Wind(render_hc,Wind_mult,'SLS')
    Wind_SLS.st_wind_speed_inputs()
    Wind_SLS.calc_regional_wind_speed()
    Wind_SLS.calc_site_wind_speed()

if __name__ == '__main__':
    main()