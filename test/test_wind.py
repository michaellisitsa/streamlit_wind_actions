"""
Testing Dimensions Class
"""

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 

import wind
import pytest
import pandas as pd
#from pandas._testing import assert_frame_equal
from enum_vals import Regions, Cases

@pytest.fixture(name="Wind_new")
def instantiate_Wind_new():
    """This fixture instantiates Dimensions as an SHS chord under AS code"""
    return wind.Wind()

@pytest.mark.parametrize('region,ARI,Vr',
                          [(Regions.A1,50,39),
                           (Regions.B,50,44),
                           (Regions.C,50,1.05 * 52)])
def test_regional_wind_speed_50_ARI_multiple_regions(Wind_new,region,ARI,Vr):
    Wind_new.region = region
    Wind_new.ARI = ARI
    Wind_new.regional_wind_speed()
    assert Wind_new.Vr == pytest.approx(Vr)
