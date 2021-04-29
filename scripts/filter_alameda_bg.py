
import geopandas as gpd

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

# filter all california shape file to just alameda block groups
p = f'{dir_path}/../data/inputs/tl_2019_06_bg/tl_2019_06_bg.shp'
cb2020 = gpd.read_file(p)
alameda2020 = cb2020.loc[cb2020['COUNTYFP'] == '001', :]
alameda2020.to_file(f'{dir_path}/../data/alameda/2019_bg/bg.shp')