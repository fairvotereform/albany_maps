# %%
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os 
import math

from mpl_toolkits.axes_grid1 import make_axes_locatable

dir_path = os.path.dirname(os.path.realpath(__file__))

###########################################################
# filenames

acs_renter_path = f'{dir_path}/../data/inputs/ACS2019_RenterBG/data_renamed.csv'
acs_incomedist_path = f'{dir_path}/../data/inputs/ACS2019_IncomeDistBG/data_renamed.csv'
acs_incomedist_col_path = f'{dir_path}/../data/inputs/ACS2019_IncomeDistBG/renamed_cols.csv'
acs_demog_path = f'{dir_path}/../data/inputs/ACS_2019_CVAP/BlockGr.csv'
california_bg_shapefile_path = f'{dir_path}/../data/inputs/tl_2019_06_bg/tl_2019_06_bg.shp'

albany_geoid_list_path = f'{dir_path}/../data/albany/2019_bg_geoids.txt'
albany_bg_shapefile_path = f'{dir_path}/../data/albany/2019_bg/bg.shp'
albany_cvap_rename_path = f'{dir_path}/../data/albany/2019_bg/cvap_col_dict.csv'
albany_cit_rename_path = f'{dir_path}/../data/albany/2019_bg/cit_col_dict.csv'
albany_demog_alone_plot_path = f'{dir_path}/../data/albany/2019_bg_demography_alone_categories.png'
albany_demog_combined_plot_path = f'{dir_path}/../data/albany/2019_bg_demography_combined_categories.png'
albany_renter_plot_path = f'{dir_path}/../data/albany/2019_bg_renters.png'
albany_income_plot_path = f'{dir_path}/../data/albany/2019_bg_income.png'
albany_bg_plot_path = f'{dir_path}/../data/albany/2019_bg.png'

###########################################################
# readin geoids and block group shapefile

geoids = []
acs_geoids = []
with open(albany_geoid_list_path) as bg_file:
    for line in bg_file:
        geoids.append(line.strip('\n'))
        acs_geoids.append('15000US' + line.strip('\n'))

# filter california block groups
california_bg = gpd.read_file(california_bg_shapefile_path)
albany_bg = california_bg.loc[california_bg['GEOID'].isin(geoids), :]

###########################################################

# column renamings
rename_col = {
    'American Indian or Alaska Native Alone': 'NA',
    'American Indian or Alaska Native and Black or African American': 'NA+AA',
    'American Indian or Alaska Native and White': 'NA+W',
    'Asian Alone': 'A',
    'Asian and White': 'A+W',
    'Black or African American Alone': 'AA',
    'Black or African American and White': 'AA+W',
    'Hispanic or Latino': 'L',
    'Native Hawaiian or Other Pacific Islander Alone': 'NH',
    'Not Hispanic or Latino': 'not_L',
    'Remainder of Two or More Race Responses': 'rest',
    'Total': 'total',
    'White Alone': 'W'
}

cvap_rename_col = {k: 'cvap_'+v for k, v in rename_col.items()}
pd.DataFrame.from_dict({
    'original': list(cvap_rename_col.keys()),
    'renamed': list(cvap_rename_col.values())
    }).to_csv(albany_cvap_rename_path, index=False)

cit_rename_col = {k: 'cit_'+v for k, v in rename_col.items()}
pd.DataFrame.from_dict({
    'original': list(cit_rename_col.keys()),
    'renamed': list(cit_rename_col.values())
    }).to_csv(albany_cit_rename_path, index=False)

# filter acs data
acs_demog = pd.read_csv(acs_demog_path)

# cvap
albany_acs_cvap = acs_demog.loc[acs_demog['geoid'].isin(acs_geoids), ['geoid', 'lntitle', 'cvap_est']]

albany_acs_cvap = albany_acs_cvap.pivot(index='geoid', columns='lntitle', values='cvap_est')

albany_acs_cvap.columns = albany_acs_cvap.columns.tolist()
albany_acs_cvap = albany_acs_cvap.reset_index()

albany_acs_cvap['GEOID'] = [i.split('15000US')[1] for i in albany_acs_cvap['geoid'].tolist()]

albany_acs_cvap = albany_acs_cvap.rename(columns=cvap_rename_col)
albany_acs_cvap = albany_acs_cvap.drop(columns=['geoid'])

# cit
albany_acs_cit = acs_demog.loc[acs_demog['geoid'].isin(acs_geoids), ['geoid', 'lntitle', 'cit_est']]

albany_acs_cit = albany_acs_cit.pivot(index='geoid', columns='lntitle', values='cit_est')

albany_acs_cit.columns = albany_acs_cit.columns.tolist()
albany_acs_cit = albany_acs_cit.reset_index()

albany_acs_cit['GEOID'] = [i.split('15000US')[1] for i in albany_acs_cit['geoid'].tolist()]

albany_acs_cit = albany_acs_cit.rename(columns=cit_rename_col)
albany_acs_cit = albany_acs_cit.drop(columns=['geoid'])

# merge
merged_acs = albany_acs_cvap.merge(albany_acs_cit, on='GEOID')
albany_bg_merged = albany_bg.merge(merged_acs, on='GEOID')

# renter
acs_renter = pd.read_csv(acs_renter_path)

acs_renter['GEOID'] = [i.split('US')[1] for i in acs_renter['GEOID'].tolist()]

albany_acs_renter = acs_renter.loc[acs_renter['GEOID'].isin(i.split('US')[1] for i in acs_geoids), :]

albany_bg_merged = albany_bg_merged.merge(albany_acs_renter, on='GEOID')

# income

acs_income_col = pd.read_csv(acs_incomedist_col_path)
acs_income_col_dict = {row['renamed']: row['original'] for idx, row in acs_income_col.iterrows()}

acs_income = pd.read_csv(acs_incomedist_path)

acs_income['GEOID'] = [i.split('US')[1] for i in acs_income['GEOID'].tolist()]

albany_acs_income = acs_income.loc[acs_income['GEOID'].isin(i.split('US')[1] for i in acs_geoids), :]

albany_bg_merged = albany_bg_merged.merge(albany_acs_income, on='GEOID')

# write
albany_bg_merged.to_crs("EPSG:4326").to_file(albany_bg_shapefile_path)

# %%
############################################################
# plots

# demographics

plot_categories = ['total', 'A', 'W', 'L', 'AA', 'NA', 'NH']
plot_categories_dict = {v: k for k, v in rename_col.items() 
                        if v in plot_categories}

unit_types = ['cvap', 'cit']

fig, axs = plt.subplots(len(plot_categories), 2)
fig.set_size_inches((12, 11))

for unit_idx, unit in enumerate(unit_types):
    for demog_idx, demog in enumerate(plot_categories):
        
        ax = axs[demog_idx, unit_idx]

        long_title = plot_categories_dict[demog]
        ax.set_title(f'{unit.upper()} -- {long_title}')

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)

        albany_bg_merged.plot(column=f'{unit}_{demog}', ax=ax, cax=cax, legend=True, cmap='Reds')

fig.savefig(albany_demog_alone_plot_path, dpi=200, format='png', transparent=False)


plot_categories = ['NA+AA', 'NA+W',  'A+W', 'AA+W', 'rest']
plot_categories_dict = {v: k for k, v in rename_col.items() 
                        if v in plot_categories}

unit_types = ['cvap', 'cit']

fig, axs = plt.subplots(len(plot_categories), 2)
fig.set_size_inches((12, 11))

for unit_idx, unit in enumerate(unit_types):
    for demog_idx, demog in enumerate(plot_categories):
        
        ax = axs[demog_idx, unit_idx]

        long_title = plot_categories_dict[demog]
        ax.set_title(f'{unit.upper()} -- {long_title}')

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.1)
        
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)

        albany_bg_merged.plot(column=f'{unit}_{demog}', ax=ax, cax=cax, legend=True, cmap='Reds')

fig.savefig(albany_demog_combined_plot_path, dpi=200, format='png', transparent=False)

# renters

plot_categories = ['house_tot', 'house_own', 'house_rent']

fig, axs = plt.subplots(len(plot_categories), 1)
fig.set_size_inches((12, 11))

for house_type_idx, house_type in enumerate(plot_categories):
        
    ax = axs[house_type_idx]

    ax.set_title(house_type)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)

    albany_bg_merged.plot(column=house_type, ax=ax, cax=cax, legend=True, cmap='Reds')

fig.savefig(albany_renter_plot_path, dpi=200, format='png', transparent=False)

# income

plot_categories = [i for i in albany_bg_merged.columns if 'income' in i]

rows = math.ceil(len(plot_categories)/2)
fig, axs = plt.subplots(rows, 2)
fig.set_size_inches((12, 11))

for income_group_idx, income_group in enumerate(plot_categories):

    ax = axs[income_group_idx % rows, int(income_group_idx/rows)]

    plot_title = income_group 
    if income_group in acs_income_col_dict:
        plot_title = acs_income_col_dict[income_group] 
    ax.set_title(plot_title)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)

    albany_bg_merged.plot(column=income_group, ax=ax, cax=cax, legend=True, cmap='Reds')

fig.savefig(albany_income_plot_path, dpi=200, format='png', transparent=False)


# block groups

albany_bg_merged_crs = albany_bg_merged.to_crs(epsg=3395)

fig, ax = plt.subplots(1, 1)
fig.set_size_inches((20, 20))

ax.axes.xaxis.set_visible(False)
ax.axes.yaxis.set_visible(False)

ax.set_title(f'Albany 2019 Census Block Groups')

albany_bg_merged_crs.boundary.plot(ax=ax)

for x, y, label in zip(albany_bg_merged_crs.geometry.centroid.x,
                       albany_bg_merged_crs.geometry.centroid.y, albany_bg_merged_crs.GEOID):
    ax.annotate(label, xy=(x-150, y))

fig.savefig(albany_bg_plot_path, dpi=200, format='png', transparent=False)

# %%
