import streamlit as st



#Import other modules in this Streamlit script
import geometry
import wind
from enum_vals import Regions, Cases

def main():
    Wind = wind.Wind()
    Wind.st_wind_speed_inputs(Cases.ULS)
    Wind.regional_wind_speed()

if __name__ == '__main__':
    main()