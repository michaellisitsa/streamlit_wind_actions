import streamlit as st



#Import other modules in this Streamlit script
import geometry
import wind
import wind_multipliers
from enum_vals import Regions, Cases

render_hc = st.sidebar.checkbox("Render hand calcs", value=True)

def main():
    Wind_mult = wind_multipliers.Wind_multipliers()
    Wind_mult.st_wind_speed_inputs()
    Wind_mult.st_terrain_inputs()
    Wind_mult.terrain_multiplier()
    Wind_mult.st_wind_multipliers_input()

    Wind_ULS = wind.Wind(render_hc,Wind_mult,'ULS')
    Wind_ULS.st_wind_speed_inputs()
    Wind_ULS.regional_wind_speed()
    Wind_ULS.calc_site_wind_speed()
    if Wind_ULS.render_hc: st.latex(Wind_ULS.V_sit_latex)

    Wind_SLS = wind.Wind(render_hc,Wind_mult,'SLS')
    Wind_SLS.st_wind_speed_inputs()
    Wind_SLS.regional_wind_speed()
    Wind_SLS.calc_site_wind_speed()
    if Wind_SLS.render_hc: st.latex(Wind_SLS.V_sit_latex)

if __name__ == '__main__':
    main()