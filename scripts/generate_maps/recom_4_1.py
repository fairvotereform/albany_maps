
import pathlib
import os

import common

# paths
file_path = pathlib.Path(os.path.realpath(__file__))
file_name = file_path.stem
dir_path = file_path.parent

output_dir = dir_path / '../../data/albany/district_maps' / file_name

small_district_lower_bound_prop = 0.15
small_district_upper_bound_prop = 0.25
n_iter = 10_000
n_district_electeds = [1, 4]

common.run_recom(small_district_lower_bound_prop, small_district_upper_bound_prop, n_district_electeds, n_iter, output_dir)
