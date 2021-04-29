# %%
import gerrychain as gc
import gerrychain.tree as gc_tree
import geopandas as gpd
from datetime import datetime

import os 
import pathlib

from plot_partition import plot_partition

now = datetime.now()
date_string = now.strftime("%d-%m-%Y %H-%M-%S")

#######################################################
# paths

file_path = pathlib.Path(os.path.realpath(__file__))
file_name = file_path.stem
dir_path = file_path.parent

albany_bg_shapefile_path = dir_path / '../../data/albany/2019_bg/bg.shp'

output_dir = dir_path / '../../data/albany/district_maps' / file_name
output_dir.mkdir(exist_ok=True)

output_path = output_dir / f'{date_string}.png'

#######################################################
# sample and plot

g = gc.Graph.from_file(filename=albany_bg_shapefile_path)
gdf = gpd.read_file(filename=albany_bg_shapefile_path)

cvap_total_sum = sum(gdf['cvap_total'])

updaters = {
    'cvap_total': gc.updaters.Tally('cvap_total'),
    'cvap_W': gc.updaters.Tally('cvap_W'),
    'cvap_NA': gc.updaters.Tally('cvap_NA'),
    'cvap_A': gc.updaters.Tally('cvap_A'),
    'cvap_AA': gc.updaters.Tally('cvap_AA'),
    'cvap_L': gc.updaters.Tally('cvap_L'),
}

assignment = gc_tree.recursive_tree_part(g, parts=[1, 2], pop_target=cvap_total_sum/2, pop_col='cvap_total', epsilon=0.5)

part = gc.Partition(g, assignment, updaters)
plot_partition(part, gdf, output_path)

# %%
