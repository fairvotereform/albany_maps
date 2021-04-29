
import geopandas as gpd

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

albany_blocks = gpd.read_file(f'{dir_path}/../data/inputs/from_pedro/Files/Albany CA Census Blocks.shp')
albany_blocks.to_file(f'{dir_path}/../data/albany/pedro_census_blocks.geojson', driver='GeoJSON')