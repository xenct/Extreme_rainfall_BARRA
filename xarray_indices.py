import xarray as xr  

season_data = {'AWAP_DJF': AWAP_DJF,
               'AWAP_MAM': AWAP_MAM,
               'AWAP_JJA': AWAP_JJA,
               'AWAP_SON': AWAP_SON,
               'BARRA_DJF': BARRA_DJF,
               'BARRA_MAM': BARRA_MAM,
               'BARRA_JJA': BARRA_JJA,
               'BARRA_SON': BARRA_SON}


season_arrays = {}
for data_name in list(season_data.keys()):
    season_arrays[f'{data_name}_array'] = xr.DataArray(season_data[data_name], dims = ['time', 'lat', 'lon'])

season_mean = {}
season_R99p = {}
season_max  = {}
for key in list(season_arrays.keys()):
    season_mean[key] = season_arrays[key].sum('time')/6
    season_R99p[key] = season_arrays[key].quantile(.99,'time')
    season_max[key]  = season_arrays[key].max('time')


# mask out all the non land/ AWAP areas
for key in ['BARRA_DJF_array', 'BARRA_MAM_array', 'BARRA_JJA_array', 'BARRA_SON_array']:
    season_max[key] = np.array(season_max[key])
    season_max[key][AWAP_ann<1] = 0
    season_mean[key] = np.array(season_mean[key])
    season_mean[key][AWAP_ann<1] = 0
    season_R99p[key] = np.array(season_R99p[key])
    season_R99p[key][AWAP_ann<1] = 0

lvls=[0,1,10,20,30,40,50, 60, 80, 100, 150, 200]
norm = BoundaryNorm(lvls, len(lvls)-1)
map_season_prcp(season_max['AWAP_DJF_array'],season_max['AWAP_MAM_array'], season_max['AWAP_JJA_array'], season_max['AWAP_SON_array'], AWAP_lats, AWAP_lons, levels= lvls, norm = norm, title = "Season Max 2010-2015")


# cdo has been used to make netCDFs of each daily rainfall indices
# name the array by dataset_index_season
# make a list of all the combinations of dataset, season, index
seasons = ['DJF', 'MAM', 'JJA', 'SON']
indices = ['cdd', 'cwd', 'r10mm', 'r20mm', 'r90p', 'r90ptot', 'r95p', 'r95ptot', 'r99p', 'r99ptot', 'rx1day', 'rx5day', 'sdii']
datasets = ['BARRA', 'AWAP']

seasonal_indices_data = {}
for dataset in datasets:
    for index in indices:
        for season in seasons:
            if dataset == "AWAP":
                filename = f'/g/data/w42/gt3409/AWAP/AWAP_PRCP_2010-2015_0.11deg_small_{season}_{index}.nc'
            elif dataset == "BARRA":
                filename = f'/g/data/w42/gt3409/BARRA_R/BARRA_R_daily_prcp_2010-2015_small_{season}_{index}.nc'
            else:
                print(f"{dataset} dataset does not exist.")
            data = Dataset(filename, 'r')
            var_name = list(data.variables.keys())[3]
            var = data[var_name][:]
            seasonal_indices_data[f'{dataset}_{index}_{season}'] = var
            



sid = seasonal_indices_data
for dataset in datasets:
    for index in indices:
        map_season_prcp(sid[f'{dataset}_{index}_DJF'], sid[f'{dataset}_{index}_MAM'], sid[f'{dataset}_{index}_JJA'], sid[f'{dataset}_{index}_SON'], lats, lons, title = f'{dataset} {index}', levels = levels['hour'], norm = BoundaryNorm(levels['hour'], len(levels['hour'])-1))
        plt.savefig(f'Documents/images/seasonal_{dataset}_{index}_2010-2015.png')





