"""
Functions for plotting paritions from gerrychain
"""

from typing import (Dict, Optional)

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import contextily as cx

def plot_partition(partition_info: Dict, geodataframe: gpd.GeoDataFrame, save_path: Optional[str] = None) -> None:
    """
    Plot just the parition on the map.
    """

    assignment = partition_info['assignment']

    plot_gdf = geodataframe.copy()
    plot_gdf['assignment'] = [assignment[geoid] for geoid in plot_gdf['GEOID']]

    dpi = 200
    fig_hw = (12, 10)

    # set up axes
    fig, ax = plt.subplots()
    fig.set_size_inches(fig_hw)

    # plot map
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)

    district_colors = ['g', 'b']
    for assign_idx, assign in enumerate(sorted(plot_gdf['assignment'].unique())):
        sub_gdf = plot_gdf.loc[plot_gdf['assignment'] == assign, :]
        sub_gdf.plot(ax=ax, color=district_colors[assign_idx], alpha=0.15)
        sub_gdf.plot(ax=ax, edgecolor=district_colors[assign_idx], linewidth=2, facecolor='none')
    cx.add_basemap(ax, crs=geodataframe.crs.to_string())

    if save_path:
        fig.savefig(save_path, dpi=dpi, format='png', transparent=False)

    plt.close(fig)

def plot_partition_stats(partition_info: Dict, 
                         partition_stats: pd.DataFrame, 
                         geodataframe: gpd.GeoDataFrame, 
                         save_path: Optional[str] = None) -> None:
    """
    Plot partition map and stats for single partition.
    """

    # reorganize data
    assignment = partition_info['assignment']

    plot_gdf = geodataframe.copy()
    plot_gdf['assignment'] = [assignment[geoid] for geoid in plot_gdf['GEOID']]

    total_pop_df = pd.DataFrame({
        'labels': ['total', 'Large\nDistrict', 'Small\nDistrict'],
        'values': [
            partition_stats['jurisdiction_cvap_total_count'].item(), 
            partition_stats['LD_cvap_total_count'].item(), 
            partition_stats['SD_cvap_total_count'].item()
        ]
    })

    ld_eth_alone_df = pd.DataFrame({
        'Large District': [
            partition_stats['LD_cvap_Alone_Remaining_perc'].item(),
            partition_stats['LD_cvap_White_Alone_perc'].item(),
            partition_stats['LD_cvap_Asian_Alone_perc'].item(),
            partition_stats['LD_cvap_Hispanic_or_Latino_Alone_perc'].item(),
            partition_stats['LD_cvap_Black_or_African_American_Alone_perc'].item(),
            partition_stats['LD_cvap_American_Indian_or_Alaska_Native_Alone_perc'].item(),
            partition_stats['LD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Alone_perc'].item()
        ]
    }, index=[
        'Remaining',
        'White',
        'Asian',  
        'Hispanic or\nLatino', 
        'Black or African\nAmerican', 
        'American Indian\nor Alaska Native',
        'Native Hawaiian\nor Other\nPacific Islander',
        ]
    )

    sd_eth_alone_df = pd.DataFrame({
        'Small District': [ 
            partition_stats['SD_cvap_Alone_Remaining_perc'].item(),
            partition_stats['SD_cvap_White_Alone_perc'].item(),
            partition_stats['SD_cvap_Asian_Alone_perc'].item(),
            partition_stats['SD_cvap_Hispanic_or_Latino_Alone_perc'].item(),
            partition_stats['SD_cvap_Black_or_African_American_Alone_perc'].item(),
            partition_stats['SD_cvap_American_Indian_or_Alaska_Native_Alone_perc'].item(),
            partition_stats['SD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Alone_perc'].item()
        ]
    }, index=[
        'Remaining',
        'White',
        'Asian',  
        'Hispanic or\nLatino', 
        'Black or African\nAmerican', 
        'American Indian\nor Alaska Native',
        'Native Hawaiian\nor Other\nPacific Islander',
        ])

    ld_eth_combo_df = pd.DataFrame({
        'Large District': [
            partition_stats['LD_cvap_Combined_Remaining_perc'].item(),
            partition_stats['LD_cvap_White_Combined_perc'].item(),
            partition_stats['LD_cvap_Asian_Combined_perc'].item(),
            partition_stats['LD_cvap_Hispanic_or_Latino_Combined_perc'].item(),
            partition_stats['LD_cvap_Black_or_African_American_Combined_perc'].item(),
            partition_stats['LD_cvap_American_Indian_or_Alaska_Native_Combined_perc'].item(),
            partition_stats['LD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Combined_perc'].item()
        ]
    }, index=[
        'Remaining',
        'White',
        'Asian',  
        'Hispanic or\nLatino', 
        'Black or African\nAmerican', 
        'American Indian\nor Alaska Native',
        'Native Hawaiian\nor Other\nPacific Islander',
        ]
    )

    sd_eth_combo_df = pd.DataFrame({
        'Small District': [ 
            partition_stats['SD_cvap_Combined_Remaining_perc'].item(),
            partition_stats['SD_cvap_White_Combined_perc'].item(),
            partition_stats['SD_cvap_Asian_Combined_perc'].item(),
            partition_stats['SD_cvap_Hispanic_or_Latino_Combined_perc'].item(),
            partition_stats['SD_cvap_Black_or_African_American_Combined_perc'].item(),
            partition_stats['SD_cvap_American_Indian_or_Alaska_Native_Combined_perc'].item(),
            partition_stats['SD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Combined_perc'].item()
        ]
    }, index=[
        'Remaining',
        'White',
        'Asian',  
        'Hispanic or\nLatino', 
        'Black or African\nAmerican', 
        'American Indian\nor Alaska Native',
        'Native Hawaiian\nor Other\nPacific Islander',
        ])


    renter_df = pd.DataFrame({
        'labels': ['Large\nDistrict', 'Small\nDistrict'],
        'values': [
            partition_stats['LD_housing_rent_perc'].item(), 
            partition_stats['SD_housing_rent_perc'].item()
        ]
    }, index=['Large\nDistrict', 'Small\nDistrict'])

    
    income_updaters = {k: v for k, v in partition_info['updaters'].items() if 'income' in k}

    ld_income_pdf_df = pd.DataFrame({
        'Large District': [v[1] for _, v in sorted(income_updaters.items())]
        }, index=[
            '<$10,000',
            '$15,000',
            '$20,000',
            '$25,000',
            '$30,000',
            '$35,000',
            '$40,000',
            '$45,000',
            '$50,000',
            '$60,000 ',
            '$75,000',
            '$100,000',
            '$125,000',
            '$150,000',
            '$200,000 ',
            '>$200,000'
        ])

    sd_income_pdf_df = pd.DataFrame({
        'Small District': [v[2] for _, v in sorted(income_updaters.items())]
    }, index=[
            '<$10,000',
            '$15,000',
            '$20,000',
            '$25,000',
            '$30,000',
            '$35,000',
            '$40,000',
            '$45,000',
            '$50,000',
            '$60,000 ',
            '$75,000',
            '$100,000',
            '$125,000',
            '$150,000',
            '$200,000 ',
            '>$200,000'
        ])
 
    dpi = 200
    fig_hw = (12, 10)

    # set up axes
    fig = plt.figure()
    fig.set_size_inches(fig_hw)

    gs = fig.add_gridspec(11, 9)
    
    map_ax = fig.add_subplot(gs[:3, 3:6])
    total_pop_ax = fig.add_subplot(gs[:3, 0:3])
    renters_ax = fig.add_subplot(gs[:3, 6:])

    income_pdf_ax = fig.add_subplot(gs[4:7, 6:])
    income_invcdf_ax = fig.add_subplot(gs[8:, 6:])

    ld_eth_alone_ax = fig.add_subplot(gs[4:7, 0:3])
    sd_eth_alone_ax = fig.add_subplot(gs[8:, 0:3])

    ld_eth_combined_ax = fig.add_subplot(gs[4:7, 3:6])
    sd_eth_combined_ax = fig.add_subplot(gs[8:, 3:6])

    # plot map
    map_ax.axes.xaxis.set_visible(False)
    map_ax.axes.yaxis.set_visible(False)

    district_colors = ['g', 'b']
    for assign_idx, assign in enumerate(sorted(plot_gdf['assignment'].unique())):
        sub_gdf = plot_gdf.loc[plot_gdf['assignment'] == assign, :]
        sub_gdf.plot(ax=map_ax, color=district_colors[assign_idx], alpha=0.15)
        sub_gdf.plot(ax=map_ax, edgecolor=district_colors[assign_idx], linewidth=2, facecolor='none')
    cx.add_basemap(map_ax, crs=geodataframe.crs.to_string())

    map_ax.set_title(f'district sizes {sorted(partition_info["n_district_electeds"])}', fontsize=10)

    
    # plot total pop
    total_pop_ax.set_title('District CVAP Total Pop.', fontsize=10)
    bars = total_pop_df.plot.bar(ax=total_pop_ax, x='labels', y='values', rot=0, legend=False, color=['k'] + district_colors, alpha=0.5)

    for bar in bars.patches[1:]:
        perc = bar.get_height() * 100 / bars.patches[0].get_height()
        bars.annotate(format(perc, '.2f') + "%", 
                (bar.get_x() + bar.get_width() / 2, 
                bar.get_height()), ha='center', va='center',
                size=10, xytext=(0, 8),
                textcoords='offset points')

    total_pop_ax.set_xlabel('')

    # plot district demographics alone
    bars = ld_eth_alone_df.plot.bar(ax=ld_eth_alone_ax, rot=0, legend=False, color=district_colors[0], alpha=0.5)

    ld_eth_alone_ax.set_xlabel('')
    ld_eth_alone_ax.set_title('Large District CVAP Ethnicity (Alone)', fontsize=10)
    ld_eth_alone_ax.set_ylim(bottom=0, top=100)
    ld_eth_alone_ax.set_ylabel('percent')
    ld_eth_alone_ax.set_xticklabels([])
    ld_eth_alone_ax.tick_params(axis='x', which='major', labelsize=8)


    for bar in bars.patches:
        bars.annotate(format(bar.get_height(), '.2f') + "%", 
                (bar.get_x() + bar.get_width() / 2, 
                bar.get_height()), ha='center', va='center',
                size=8, xytext=(0, 8),
                textcoords='offset points')

    bars = sd_eth_alone_df.plot.bar(ax=sd_eth_alone_ax, rot=0, legend=False, color=district_colors[1], alpha=0.5)

    sd_eth_alone_ax.set_xlabel('')
    sd_eth_alone_ax.set_title('Small District CVAP Ethnicity (Alone)', fontsize=10)
    sd_eth_alone_ax.set_ylim(bottom=0, top=100)
    sd_eth_alone_ax.set_ylabel('percent')
    sd_eth_alone_ax.set_xticklabels(
        sd_eth_alone_ax.get_xticklabels(),
        rotation = 60)
    sd_eth_alone_ax.tick_params(axis='x', which='major', labelsize=7)

    for bar in bars.patches:
        bars.annotate(format(bar.get_height(), '.2f') + "%", 
                (bar.get_x() + bar.get_width() / 2, 
                bar.get_height()), ha='center', va='center',
                size=8, xytext=(0, 8),
                textcoords='offset points')

    # plot district demographics combined
    bars = ld_eth_combo_df.plot.bar(ax=ld_eth_combined_ax, rot=0, legend=False, color=district_colors[0], alpha=0.5)

    ld_eth_combined_ax.set_xlabel('')
    ld_eth_combined_ax.set_title('Large District CVAP Ethnicity (Combined)', fontsize=10)
    ld_eth_combined_ax.set_ylim(bottom=0, top=100)
    ld_eth_combined_ax.set_ylabel('')
    ld_eth_combined_ax.set_yticks([])
    ld_eth_combined_ax.set_yticks([], minor=True)
    ld_eth_combined_ax.set_xticklabels([])
    ld_eth_combined_ax.tick_params(axis='x', which='major', labelsize=8)

    for bar in bars.patches:
        bars.annotate(format(bar.get_height(), '.2f') + "%", 
                (bar.get_x() + bar.get_width() / 2, 
                bar.get_height()), ha='center', va='center',
                size=8, xytext=(0, 8),
                textcoords='offset points')

    bars = sd_eth_combo_df.plot.bar(ax=sd_eth_combined_ax, rot=0, legend=False, color=district_colors[1], alpha=0.5)

    sd_eth_combined_ax.set_xlabel('')
    sd_eth_combined_ax.set_title('Small District CVAP Ethnicity (Combined)', fontsize=10)
    sd_eth_combined_ax.set_ylim(bottom=0, top=100)
    sd_eth_combined_ax.set_ylabel('')
    sd_eth_combined_ax.set_yticks([])
    sd_eth_combined_ax.set_yticks([], minor=True)
    sd_eth_combined_ax.set_xticklabels(
        sd_eth_combined_ax.get_xticklabels(),
        rotation = 60)
    sd_eth_combined_ax.tick_params(axis='x', which='major', labelsize=7)

    for bar in bars.patches:
        bars.annotate(format(bar.get_height(), '.2f') + "%", 
                (bar.get_x() + bar.get_width() / 2, 
                bar.get_height()), ha='center', va='center',
                size=8, xytext=(0, 8),
                textcoords='offset points')

    # plot renter breakdown
    bars = renter_df.plot.bar(ax=renters_ax, x='labels', y='values', legend=False, color=district_colors, alpha=0.5, rot=0)

    renters_ax.set_title('District Renters', fontsize=10)
    renters_ax.set_xlabel('')
    renters_ax.tick_params(axis='x', which='major', labelsize=10)
    renters_ax.set_xticklabels(
        renters_ax.get_xticklabels(),
        rotation = 0)
    renters_ax.tick_params(axis='y', which='major', labelsize=10)
    renters_ax.yaxis.set_label_position("right")
    renters_ax.yaxis.tick_right()
    renters_ax.set_ylabel('percent')
    renters_ax.set_ylim([0, 100])

    for bar in bars.patches[:2]:
        bars.annotate(format(bar.get_height(), '.2f') + "%", 
                (bar.get_x() + bar.get_width() / 2, 
                bar.get_height()), ha='center', va='center',
                size=8, xytext=(0, 8),
                textcoords='offset points')

    # plot income distributions

    ld_income_pdf_df.plot.bar(ax=income_pdf_ax, legend=False, color=district_colors[0], alpha=0.5)

    sd_income_pdf_df.plot.bar(ax=income_pdf_ax, legend=False, color=district_colors[1], alpha=0.5)

    income_pdf_ax.set_title('District Income Distribution', fontsize=10)
    income_pdf_ax.yaxis.tick_right()
    income_pdf_ax.set_ylabel('count')
    income_pdf_ax.yaxis.set_label_position("right")
    income_pdf_ax.set_xticklabels([])


    ld_income_pdf_df['cum_percent'] = 100*(ld_income_pdf_df['Large District'].cumsum() / ld_income_pdf_df['Large District'].sum())

    sd_income_pdf_df['cum_percent'] = 100*(sd_income_pdf_df['Small District'].cumsum() / sd_income_pdf_df['Small District'].sum())


    income_invcdf_ax.plot(ld_income_pdf_df.index, ld_income_pdf_df['cum_percent'], color=district_colors[0])

    income_invcdf_ax.plot(ld_income_pdf_df.index, sd_income_pdf_df['cum_percent'], color=district_colors[1])

    extraticks = []
    for idx, n in enumerate(sorted(partition_info['n_district_electeds'], reverse=True)):
        quota = 100/(n+1)
        extraticks.append(quota)
        income_invcdf_ax.axhline(y=quota, ls='--', color=district_colors[idx], alpha=0.3)

    income_invcdf_ax.set_title('District Income Cumulative Dist', fontsize=10)
    income_invcdf_ax.yaxis.tick_right()
    income_invcdf_ax.set_ylabel('percent')
    income_invcdf_ax.yaxis.set_label_position("right")
    income_invcdf_ax.set_yticks(list(income_invcdf_ax.get_yticks()) + extraticks)
    income_invcdf_ax.set_ylim([0, 100])
    income_invcdf_ax.set_xlabel('income range')
    income_invcdf_ax.set_xticklabels(
        ld_income_pdf_df.index.tolist(),
        rotation = 60)
    income_invcdf_ax.tick_params(axis='x', which='major', labelsize=7)

    if save_path:
        fig.savefig(save_path, dpi=dpi, format='png', transparent=False)

    plt.close(fig)

def plot_chain_summary(df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """
    Plot distribution of stats across all maps.
    """

    # reorganize data
    total_pop_df = df.loc[:, ['map_id', 'LD_cvap_total_perc', 'SD_cvap_total_perc']]
    total_pop_df = pd.melt(total_pop_df, id_vars=['map_id'], value_vars=['LD_cvap_total_perc', 'SD_cvap_total_perc'])

    quadrant_df = df.loc[:, ['SD_quadrant']].value_counts().to_frame().reset_index()
    quadrant_df.columns = ['SD_quadrant', 'count']

    renter_df = df.loc[:, ['map_id', 'LD_housing_rent_perc', 'SD_housing_rent_perc']]
    renter_df = pd.melt(renter_df, id_vars=['map_id'], value_vars=['LD_housing_rent_perc', 'SD_housing_rent_perc'])

    income_buckets = pd.DataFrame({
        'full_name': [
            'Less than $10,000',
            '$10,000 to $14,999',
            '$15,000 to $19,999',
            '$20,000 to $24,999',
            '$25,000 to $29,999',
            '$30,000 to $34,999',
            '$35,000 to $39,999',
            '$40,000 to $44,999',
            '$45,000 to $49,999',
            '$50,000 to $59,999',
            '$60,000 to $74,999',
            '$75,000 to $99,999',
            '$100,000 to $124,999',
            '$125,000 to $149,999',
            '$150,000 to $199,999',
            '$200,000 or more'],
        'short_name': [
            '<$10,000',
            '$15,000',
            '$20,000',
            '$25,000',
            '$30,000',
            '$35,000',
            '$40,000',
            '$45,000',
            '$50,000',
            '$60,000',
            '$75,000',
            '$100,000',
            '$125,000',
            '$150,000',
            '$200,000',
            '>$200,000']
    })

    ld_income_buckets_count = df.loc[:, ['LD_income_bucket_at_quota']].value_counts().to_frame().reset_index()
    ld_income_buckets_count.columns = ['LD_income_bucket_at_quota', 'count']

    for k in income_buckets['full_name']:
        if k not in ld_income_buckets_count['LD_income_bucket_at_quota'].tolist():
            ld_income_buckets_count = ld_income_buckets_count.append({'LD_income_bucket_at_quota': k, 'count': 0}, ignore_index=True)

    ld_income_buckets_count.index = ld_income_buckets_count['LD_income_bucket_at_quota']
    ld_income_buckets_count = ld_income_buckets_count.loc[income_buckets['full_name'], :]
    ld_income_buckets_count = ld_income_buckets_count.reset_index(drop=True)
    ld_income_buckets_count['LD_income_bucket_at_quota'] = income_buckets['short_name']
    ld_income_buckets_count.columns = ['income_bucket', 'count']

    sd_income_buckets_count = df.loc[:, ['SD_income_bucket_at_quota']].value_counts().to_frame().reset_index()
    sd_income_buckets_count.columns = ['SD_income_bucket_at_quota', 'count']

    for k in income_buckets['full_name']:
        if k not in sd_income_buckets_count['SD_income_bucket_at_quota'].tolist():
            sd_income_buckets_count = sd_income_buckets_count.append({'SD_income_bucket_at_quota': k, 'count': 0}, ignore_index=True)

    sd_income_buckets_count.index = sd_income_buckets_count['SD_income_bucket_at_quota']
    sd_income_buckets_count = sd_income_buckets_count.loc[income_buckets['full_name'], :]
    sd_income_buckets_count = sd_income_buckets_count.reset_index(drop=True)
    sd_income_buckets_count['SD_income_bucket_at_quota'] = income_buckets['short_name']
    sd_income_buckets_count.columns = ['income_bucket', 'count']

    eth_col_rename = [
        'Remaining',
        'White',
        'Asian',  
        'Hispanic or\nLatino', 
        'Black or African\nAmerican', 
        'American Indian\nor Alaska Native',
        'Native Hawaiian\nor Other\nPacific Islander'
    ]

    ld_eth_alone_df = df.loc[:, [
        'map_id', 
        'LD_cvap_Alone_Remaining_perc',
        'LD_cvap_White_Alone_perc',
        'LD_cvap_Asian_Alone_perc',
        'LD_cvap_Hispanic_or_Latino_Alone_perc',
        'LD_cvap_Black_or_African_American_Alone_perc',
        'LD_cvap_American_Indian_or_Alaska_Native_Alone_perc',
        'LD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Alone_perc']]
    ld_eth_alone_df.columns = ['map_id'] + eth_col_rename
    ld_eth_alone_df = pd.melt(ld_eth_alone_df, 
                              id_vars=['map_id'], 
                              value_vars=eth_col_rename)

    sd_eth_alone_df = df.loc[:, [
        'map_id', 
        'SD_cvap_Alone_Remaining_perc',
        'SD_cvap_White_Alone_perc',
        'SD_cvap_Asian_Alone_perc',
        'SD_cvap_Hispanic_or_Latino_Alone_perc',
        'SD_cvap_Black_or_African_American_Alone_perc',
        'SD_cvap_American_Indian_or_Alaska_Native_Alone_perc',
        'SD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Alone_perc']]
    sd_eth_alone_df.columns = ['map_id'] + eth_col_rename
    sd_eth_alone_df = pd.melt(sd_eth_alone_df, 
                              id_vars=['map_id'], 
                              value_vars=eth_col_rename)
                

    ld_eth_combined_df = df.loc[:, [
        'map_id', 
        'LD_cvap_Combined_Remaining_perc',
        'LD_cvap_White_Combined_perc',
        'LD_cvap_Asian_Combined_perc',
        'LD_cvap_Hispanic_or_Latino_Combined_perc',
        'LD_cvap_Black_or_African_American_Combined_perc',
        'LD_cvap_American_Indian_or_Alaska_Native_Combined_perc',
        'LD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Combined_perc']]
    ld_eth_combined_df.columns = ['map_id'] + eth_col_rename
    ld_eth_combined_df = pd.melt(ld_eth_combined_df, 
                              id_vars=['map_id'], 
                              value_vars=eth_col_rename)

    sd_eth_combined_df = df.loc[:, [
        'map_id', 
        'SD_cvap_Combined_Remaining_perc',
        'SD_cvap_White_Combined_perc',
        'SD_cvap_Asian_Combined_perc',
        'SD_cvap_Hispanic_or_Latino_Combined_perc',
        'SD_cvap_Black_or_African_American_Combined_perc',
        'SD_cvap_American_Indian_or_Alaska_Native_Combined_perc',
        'SD_cvap_Native_Hawaiian_or_Other_Pacific_Islander_Combined_perc']]
    sd_eth_combined_df.columns = ['map_id'] + eth_col_rename
    sd_eth_combined_df = pd.melt(sd_eth_combined_df, 
                              id_vars=['map_id'], 
                              value_vars=eth_col_rename)

    dpi = 200
    fig_hw = (12, 10)

    # set up axes
    fig = plt.figure()
    fig.set_size_inches(fig_hw)

    gs = fig.add_gridspec(11, 11)
    
    total_pop_ax = fig.add_subplot(gs[:3, 0:3])
    quadrant_ax = fig.add_subplot(gs[:3, 4:7])
    renters_ax = fig.add_subplot(gs[:3, 8:11])

    ld_income_ax = fig.add_subplot(gs[4:7, 8:])
    sd_income_ax = fig.add_subplot(gs[8:, 8:])

    ld_eth_alone_ax = fig.add_subplot(gs[4:7, 0:3])
    sd_eth_alone_ax = fig.add_subplot(gs[8:, 0:3])

    ld_eth_combined_ax = fig.add_subplot(gs[4:7, 4:7])
    sd_eth_combined_ax = fig.add_subplot(gs[8:, 4:7])
    
    # Create an array with the colors 
    colors = ["#7fbf7f", "#7f7fff"]

    # total pop
    sns_plot = sns.stripplot(ax=total_pop_ax, x="variable", y="value", data=total_pop_df, jitter=0.05, hue='variable', palette=colors)
    sns_plot.get_legend().remove()

    total_pop_ax.set_xlabel('')
    total_pop_ax.set_ylabel('percent')
    total_pop_ax.set_xticklabels(['Large District', 'Small District'])
    total_pop_ax.set_title(f'Distribution of District Sizes (Percent) ({df.shape[0]} maps)', fontsize=10)

    # quandrant distribution
    quadrant_df.plot.bar(ax=quadrant_ax, x='SD_quadrant', y='count', legend=False, alpha=0.5, rot=0)

    quadrant_ax.set_title('Distribution of Small District Quadrants', fontsize=10)
    quadrant_ax.set_ylabel('count')
    quadrant_ax.set_xlabel('Small District Quadrant')

    # renter 
    sns_plot = sns.stripplot(ax=renters_ax, x="variable", y="value", data=renter_df, jitter=0.5, hue='variable', palette=colors)
    sns_plot.get_legend().remove()

    renters_ax.set_xlabel('')
    renters_ax.set_ylabel('percent')
    renters_ax.set_xticklabels(['Large District', 'Small District'])
    renters_ax.set_title('Distribution of District Renter Composition', fontsize=10)

    # ld eth alone
    sns.stripplot(ax=ld_eth_alone_ax, x="variable", y="value", data=ld_eth_alone_df, jitter=0.5, color=colors[0])

    ld_eth_alone_ax.set_xlabel('')
    ld_eth_alone_ax.set_title('Large District\nDistribution of CVAP Ethnicity (Alone)', fontsize=10)
    ld_eth_alone_ax.set_ylim(bottom=0, top=100)
    ld_eth_alone_ax.set_ylabel('percent')
    ld_eth_alone_ax.set_xticklabels([])
    ld_eth_alone_ax.tick_params(axis='x', which='major', labelsize=8)

    # sd eth alone
    sns.stripplot(ax=sd_eth_alone_ax, x="variable", y="value", data=sd_eth_alone_df, jitter=0.5, color=colors[1])

    sd_eth_alone_ax.set_xlabel('')
    sd_eth_alone_ax.set_title('Small District\nDistribution of CVAP Ethnicity (Alone)', fontsize=10)
    sd_eth_alone_ax.set_ylim(bottom=0, top=100)
    sd_eth_alone_ax.set_ylabel('percent')
    sd_eth_alone_ax.set_xticklabels(
        sd_eth_alone_ax.get_xticklabels(),
        rotation = 60)
    sd_eth_alone_ax.tick_params(axis='x', which='major', labelsize=7)

    # ld eth combined
    sns.stripplot(ax=ld_eth_combined_ax, x="variable", y="value", data=ld_eth_combined_df, jitter=0.05, color=colors[0])

    ld_eth_combined_ax.set_xlabel('')
    ld_eth_combined_ax.set_title('Large District\nDistribution of CVAP Ethnicity (Combined)', fontsize=10)
    ld_eth_combined_ax.set_ylim(bottom=0, top=100)
    ld_eth_combined_ax.set_ylabel('')
    ld_eth_combined_ax.set_xticklabels([])
    ld_eth_combined_ax.tick_params(axis='x', which='major', labelsize=8)

    # sd eth combined
    sns.stripplot(ax=sd_eth_combined_ax, x="variable", y="value", data=sd_eth_combined_df, jitter=0.05, color=colors[1])

    sd_eth_combined_ax.set_xlabel('')
    sd_eth_combined_ax.set_title('Small District\nDistribution of CVAP Ethnicity (Combined)', fontsize=10)
    sd_eth_combined_ax.set_ylim(bottom=0, top=100)
    sd_eth_combined_ax.set_ylabel('')
    sd_eth_combined_ax.set_xticklabels(
        sd_eth_combined_ax.get_xticklabels(),
        rotation = 60)
    sd_eth_combined_ax.tick_params(axis='x', which='major', labelsize=7)

    # income
    ld_income_buckets_count.plot.bar(ax=ld_income_ax, x='income_bucket', y='count', legend=False, color=colors[0], alpha=0.5, rot=0)

    ld_income_ax.set_title('Large District\nDist of Income Range Needed to Reach Quota',  fontsize=10)
    ld_income_ax.set_ylabel('count')
    ld_income_ax.set_xlabel('')
    ld_income_ax.set_xticklabels([])

    sd_income_buckets_count.plot.bar(ax=sd_income_ax, x='income_bucket', y='count', legend=False, color=colors[1], alpha=0.5, rot=0)

    sd_income_ax.set_title('Small District\nDist of Income Range Needed to Reach Quota',  fontsize=10)
    sd_income_ax.set_ylabel('count')
    sd_income_ax.set_xlabel('income range')
    sd_income_ax.set_xticklabels(
        sd_income_ax.get_xticklabels(),
        rotation = 60)
    sd_income_ax.tick_params(axis='x', which='major', labelsize=7)

    if save_path:
        fig.savefig(save_path, dpi=dpi, format='png', transparent=False)

    plt.close(fig)