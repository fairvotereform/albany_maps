"""
Contains function used to generate a series of gerrychain maps and work with the output.
"""
from typing import (List, Optional, Dict)

import functools
import pathlib
import os

import pandas as pd

import gerrychain as gc
import geopandas as gpd
import gerrychain.tree as gc_tree
import gerrychain.accept as accept
import gerrychain.constraints as constraints
import gerrychain.proposals as proposals

import plot

def filter_unique_partitions(chain: List) -> List:
    """
    Return only unique partitions from the chain.
    """

    partition_dict = {}
    for partition in chain:

        district_pop = partition['cvap_total']
        district1_is_small = district_pop[1] < district_pop[2]

        small_district_id = 1 if district1_is_small else 2
        small_district_node_ids = [k for k, v in dict(partition.assignment).items() if v == small_district_id]
        sorted_small_district_node_ids = tuple(sorted(small_district_node_ids))

        if sorted_small_district_node_ids not in partition_dict:
            partition_dict.update({sorted_small_district_node_ids: partition})

    return list(partition_dict.values())

def unequal_size_constraint_template(partition: gc.Partition, lower_bound_prop: float, upper_bound_prop: float) -> bool:
    """
    Check that smallest district is between proportion bounds. Only makes sense with two districts.

    partition - a gerrychain partition
    lower_bound_prop - float between 0 and 1
    upper_bound_prop - float between 0 and 1
    """
    
    total = sum(partition['cvap_total'].values())

    min_district_size = min(partition['cvap_total'].values())
    min_district_proportion = min_district_size / total

    lower_bound_bool = min_district_proportion >= lower_bound_prop
    upper_bound_bool = min_district_proportion <= upper_bound_prop

    if lower_bound_bool and upper_bound_bool:
        return True
    else:
        return False

def reorganize_partition_info(partition: gc.Partition, n_district_electeds: Optional[List[int]] = None) -> Dict:
    """
    Extract and reorder information from parition so that large district has ID 1 and small district has ID 2.
    """

    partition_info = {}

    d1_pop = partition['cvap_total'][1]
    d2_pop = partition['cvap_total'][2]

    district1_is_small = d1_pop < d2_pop

    if district1_is_small:
        partition_info = {
            'assignment': {partition.graph.nodes[k]['GEOID']: 1 if v == 2 else 2 
                           for k, v in dict(partition.assignment).items()},
            'updaters': {k: {1: partition[k][2], 2: partition[k][1]} 
                         for k in partition.updaters.keys() 
                         if 'cvap' in k or 'house' in k or 'income' in k}
        }
    else:
        partition_info = {
            'assignment': {partition.graph.nodes[k]['GEOID']: v
                           for k, v in dict(partition.assignment).items()},
            'updaters': {k: partition[k] for k in partition.updaters.keys() 
                         if 'cvap' in k or 'house' in k or 'income' in k}
        }

    partition_info.update({'n_district_electeds': n_district_electeds})

    return partition_info

def calc_partition_stats(partition_idx: int, partition_info: Dict, geodataframe: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Calculate various statistics from the partition and geodataframe.
    """

    updaters = partition_info['updaters']

    df = pd.Series()
    df['map_id'] = partition_idx

    # cvap info
    cvap_updaters = {k: v for k, v in updaters.items() if 'cvap' in k and 'total' not in k}
    LD_cvap_total = sum(v[1] for k, v in cvap_updaters.items() if k != 'cvap_not_L')
    SD_cvap_total = sum(v[2] for k, v in cvap_updaters.items() if k != 'cvap_not_L')

    df['jurisdiction_cvap_total_count'] = LD_cvap_total + SD_cvap_total

    df['LD_cvap_total_count'] = LD_cvap_total
    df['SD_cvap_total_count'] = SD_cvap_total

    df['LD_cvap_total_perc'] = 100 * LD_cvap_total / df['jurisdiction_cvap_total_count']
    df['SD_cvap_total_perc'] = 100 * SD_cvap_total / df['jurisdiction_cvap_total_count']

    # large district alone percent 
    df['LD_cvap_White_Alone_perc'] = 100 * updaters['cvap_W'][1] / LD_cvap_total
    df['LD_cvap_Black_or_African_American_Alone_perc'] = 100 * updaters['cvap_AA'][1] / LD_cvap_total
    df['LD_cvap_Asian_Alone_perc'] = 100 * updaters['cvap_A'][1] / LD_cvap_total
    df['LD_cvap_Hispanic_or_Latino_Alone_perc'] = 100 * updaters['cvap_L'][1] / LD_cvap_total
    df['LD_cvap_American_Indian_or_Alaska_Native_Alone_perc'] = 100 * updaters['cvap_NA'][1] / LD_cvap_total
    df['LD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Alone_perc'] = 100 * updaters['cvap_NH'][1] / LD_cvap_total

    LD_cvap_Alone_Remaining_perc = updaters['cvap_NA+AA'][1] 
    LD_cvap_Alone_Remaining_perc += updaters['cvap_NA+W'][1]
    LD_cvap_Alone_Remaining_perc += updaters['cvap_A+W'][1]
    LD_cvap_Alone_Remaining_perc += updaters['cvap_AA+W'][1]
    LD_cvap_Alone_Remaining_perc += updaters['cvap_rest'][1]
    df['LD_cvap_Alone_Remaining_perc'] = 100 * LD_cvap_Alone_Remaining_perc / LD_cvap_total

    # small district alone percent
    df['SD_cvap_White_Alone_perc'] = 100 * updaters['cvap_W'][2] / SD_cvap_total
    df['SD_cvap_Black_or_African_American_Alone_perc'] = 100 * updaters['cvap_AA'][2] / SD_cvap_total
    df['SD_cvap_Asian_Alone_perc'] = 100 * updaters['cvap_A'][2] / SD_cvap_total
    df['SD_cvap_Hispanic_or_Latino_Alone_perc'] = 100 * updaters['cvap_L'][2] / SD_cvap_total
    df['SD_cvap_American_Indian_or_Alaska_Native_Alone_perc'] = 100 * updaters['cvap_NA'][2] / SD_cvap_total
    df['SD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Alone_perc'] = 100 * updaters['cvap_NH'][2] / SD_cvap_total

    SD_cvap_Alone_Remaining_perc = updaters['cvap_NA+AA'][2]
    SD_cvap_Alone_Remaining_perc += updaters['cvap_NA+W'][2]
    SD_cvap_Alone_Remaining_perc += updaters['cvap_A+W'][2]
    SD_cvap_Alone_Remaining_perc += updaters['cvap_AA+W'][2]
    SD_cvap_Alone_Remaining_perc += updaters['cvap_rest'][2]
    df['SD_cvap_Alone_Remaining_perc'] = 100 * SD_cvap_Alone_Remaining_perc / SD_cvap_total

    # large district combined perc
    df['LD_cvap_White_Combined_perc'] = 100 * updaters['cvap_W'][1] / LD_cvap_total
    df['LD_cvap_Black_or_African_American_Combined_perc'] = 100 * (
        updaters['cvap_AA'][1] + updaters['cvap_AA+W'][1]) / LD_cvap_total
    df['LD_cvap_Asian_Combined_perc'] = 100 * (updaters['cvap_A'][1] + updaters['cvap_A+W'][1]) / LD_cvap_total
    df['LD_cvap_Hispanic_or_Latino_Combined_perc'] = 100 * updaters['cvap_L'][1] / LD_cvap_total
    df['LD_cvap_American_Indian_or_Alaska_Native_Combined_perc'] = 100 * (
        updaters['cvap_NA'][1] + updaters['cvap_NA+W'][1]) / LD_cvap_total
    df['LD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Combined_perc'] = 100 * updaters['cvap_NH'][1] / LD_cvap_total
    df['LD_cvap_Combined_Remaining_perc'] = 100 * (updaters['cvap_NA+AA'][1] + updaters['cvap_rest'][1]) / LD_cvap_total

    # small district combined perc
    df['SD_cvap_White_Combined_perc'] = 100 * updaters['cvap_W'][2] / SD_cvap_total
    df['SD_cvap_Black_or_African_American_Combined_perc'] = 100 * (
        updaters['cvap_AA'][2] + updaters['cvap_AA+W'][2]) / SD_cvap_total
    df['SD_cvap_Asian_Combined_perc'] = 100 * (updaters['cvap_A'][2] + updaters['cvap_A+W'][2]) / SD_cvap_total
    df['SD_cvap_Hispanic_or_Latino_Combined_perc'] = 100 * updaters['cvap_L'][2] / SD_cvap_total
    df['SD_cvap_American_Indian_or_Alaska_Native_Combined_perc'] = 100 * (
        updaters['cvap_NA'][2] + updaters['cvap_NA+W'][2]) / SD_cvap_total
    df['SD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Combined_perc'] = 100 * updaters['cvap_NH'][2] / SD_cvap_total
    df['SD_cvap_Combined_Remaining_perc'] = 100 * (updaters['cvap_NA+AA'][2] + updaters['cvap_rest'][2]) / SD_cvap_total

    # rent and ownership
    LD_house_total = updaters['house_own'][1] + updaters['house_rent'][1]
    df['LD_housing_own_perc'] = 100 * updaters['house_own'][1] / LD_house_total
    df['LD_housing_rent_perc'] = 100 * updaters['house_rent'][1] / LD_house_total

    SD_house_total = updaters['house_own'][2] + updaters['house_rent'][2]
    df['SD_housing_own_perc'] = 100 * updaters['house_own'][2] / SD_house_total
    df['SD_housing_rent_perc'] = 100 * updaters['house_rent'][2] / SD_house_total

    # income percentile
    LD_electeds = sorted(partition_info['n_district_electeds'])[1]
    SD_electeds = sorted(partition_info['n_district_electeds'])[0]
    LD_quota = 1 / (LD_electeds + 1)
    SD_quota = 1 / (SD_electeds + 1)

    income_updaters = {k: v for k, v in updaters.items() if 'income' in k}

    LD_income_total_count = sum(v[1] for v in income_updaters.values()) 
    SD_income_total_count = sum(v[2] for v in income_updaters.values()) 

    LD_accumulated_income = 0
    LD_bucket_reached = None
    for income_k, income_v in sorted(income_updaters.items()):
        LD_accumulated_income += income_v[1]
        if LD_accumulated_income / LD_income_total_count > LD_quota:
            LD_bucket_reached = income_k
            break

    SD_accumulated_income = 0
    SD_bucket_reached = None
    for income_k, income_v in sorted(income_updaters.items()):
        SD_accumulated_income += income_v[2]
        if SD_accumulated_income / SD_income_total_count > SD_quota:
            SD_bucket_reached = income_k
            break

    df['LD_income_bucket_at_quota'] = LD_bucket_reached
    df['SD_income_bucket_at_quota'] = SD_bucket_reached

    # add quadrant
    assigned_gdf = geodataframe.copy()
    assigned_gdf['assignment'] = [partition_info['assignment'][geoid] for geoid in assigned_gdf['GEOID']]
    
    # get small district centroid
    district_gdf = assigned_gdf.dissolve(by='assignment').reset_index()
    SD_x = district_gdf.loc[district_gdf['assignment'] == 2, 'geometry'].centroid.x.item()
    SD_y = district_gdf.loc[district_gdf['assignment'] == 2, 'geometry'].centroid.y.item()

    # get centroid for all of albany
    whole_albany_gdf = assigned_gdf.dissolve()
    whole_albany_x = whole_albany_gdf.geometry.centroid.x.item()
    whole_albany_y = whole_albany_gdf.geometry.centroid.y.item()

    if SD_x < whole_albany_x and SD_y > whole_albany_y:
        df['SD_quadrant'] = 'NW'
    elif SD_x < whole_albany_x and SD_y < whole_albany_y:
        df['SD_quadrant'] = 'SW'
    elif SD_x > whole_albany_x and SD_y > whole_albany_y:
        df['SD_quadrant'] = 'NE'
    elif SD_x > whole_albany_x and SD_y < whole_albany_y:
        df['SD_quadrant'] = 'SE'

    # add geoid
    df['LD_geoids'] = ";".join(sorted(k for k, v in partition_info['assignment'].items() if v == 1))
    df['SD_geoids'] = ";".join(sorted(k for k, v in partition_info['assignment'].items() if v == 2))

    return df.to_frame().transpose()
    
def run_recom(small_district_lower_bound_prop: float, 
              small_district_upper_bound_prop: float, 
              n_district_electeds: List[int], 
              n_iter: int, 
              output_dir: str) -> None:
    """
    Read in shapefiles, create updaters, run chain, calculate statistics, and plot.
    """

    # paths
    file_path = pathlib.Path(os.path.realpath(__file__))
    dir_path = file_path.parent

    albany_bg_shapefile_path = dir_path / '../../data/albany/2019_bg/bg.shp'
    acs_incomedist_col_path = dir_path / '../../data/inputs/ACS2019_IncomeDistBG/renamed_cols.csv'

    output_dir.mkdir(exist_ok=True)

    map_output_dir = output_dir / 'maps'
    map_output_dir.mkdir(exist_ok=True)

    map_stats_path = output_dir / 'map_stats.csv'
    map_summary_plot_path = output_dir / 'map_summary.png'

    # read in albany block groups
    g = gc.Graph.from_file(filename=albany_bg_shapefile_path)
    gdf = gpd.read_file(filename=albany_bg_shapefile_path)
    
    # make updaters
    updaters = {col_name: gc.updaters.Tally(col_name) for col_name in gdf.columns if 'cvap' in col_name}

    updaters.update({col_name: gc.updaters.Tally(col_name) for col_name in gdf.columns if 'house' in col_name and 'tot' not in col_name})

    updaters.update({col_name: gc.updaters.Tally(col_name) for col_name in gdf.columns if 'income' in col_name and 'tot' not in col_name})

    # make constraints
    unequal_size_constraint = functools.partial(unequal_size_constraint_template,
                                                lower_bound_prop=small_district_lower_bound_prop, 
                                                upper_bound_prop=small_district_upper_bound_prop)
    unequal_size_constraint.__name__ = 'unequal_size_constraint'

    # make initial assignment
    total_pop = sum(gdf['cvap_total'])
    equal_proportions_size = total_pop/2

    good_initial_partition = False
    while not good_initial_partition:
        
        initial_assignment = gc_tree.recursive_tree_part(g, parts=[1, 2], pop_target=equal_proportions_size, pop_col='cvap_total', epsilon=50)
        
        initial_partition = gc.GeographicPartition(g, assignment=initial_assignment, updaters=updaters)

        if unequal_size_constraint(initial_partition):
            good_initial_partition = True

    percs = {k: 100*v/total_pop for k, v in initial_partition['cvap_total'].items()}
    print(f'initial partition {percs}')

    # make chain
    proposal = functools.partial(proposals.recom, pop_col="cvap_total", pop_target=equal_proportions_size, epsilon=50, node_repeats=10)

    chain = gc.MarkovChain(
        proposal=proposal,
        constraints=[unequal_size_constraint, constraints.contiguous],
        accept=accept.always_accept,
        initial_state=initial_partition,
        total_steps=n_iter
    )

    # get unique partitions
    unique_partitions = filter_unique_partitions(chain)
    print(f'{len(unique_partitions)} unique partitions')

    # rename income groups dict
    acs_income_col = pd.read_csv(acs_incomedist_col_path)
    acs_income_col_dict = {row['renamed']: row['original'] for _, row in acs_income_col.iterrows()}

    # plot chain test
    all_partition_stats = []
    for partition_idx, partition in enumerate(unique_partitions):
        
        partition_info = reorganize_partition_info(partition, n_district_electeds=n_district_electeds)
        partition_stats = calc_partition_stats(partition_idx, partition_info, gdf)

        tmp = partition_stats['LD_income_bucket_at_quota'].item()
        partition_stats['LD_income_bucket_at_quota'] = acs_income_col_dict[tmp]

        tmp = partition_stats['SD_income_bucket_at_quota'].item()
        partition_stats['SD_income_bucket_at_quota'] = acs_income_col_dict[tmp]

        plot.plot_partition(partition_info, gdf, map_output_dir / f'{partition_idx}_map.png')
        plot.plot_partition_stats(partition_info, partition_stats, gdf, map_output_dir / f'{partition_idx}_map_stats.png')

        all_partition_stats.append(partition_stats)

    all_stats_df = pd.concat(all_partition_stats).round()
    all_stats_df.to_csv(map_stats_path, index=False)

    plot.plot_chain_summary(all_stats_df, map_summary_plot_path)