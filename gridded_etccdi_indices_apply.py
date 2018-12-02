## Script to apply all extreme rainfall indices and map
from pylab import cm
custom_RdBu = cm.get_cmap("RdBu",20)(np.arange(20))
custom_RdBu[9] = [1,1,1,1]
custom_RdBu[10] = [1,1,1,1]

cmap_custom_RdBu = LinearSegmentedColormap.from_list("RdWtBu", custom_RdBu, 20) 

single_input_functions = [rr, rr1, sdii, cwd, r10mm, r20mm, rx1day, rx5day]
double_input_functions = [r75p, r75ptot, r95p, r95ptot, r99p, r99ptot]

# Mask for AWAP land:
land_mask = [np.nansum(prcp_data['AWAP_ann'],0) > 1]

# calculated indices
indices = {}
keys = list(prcp_data.keys())
for key in keys:
    data = prcp_data[key]*land_mask
    for fn in single_input_functions:
        indices[f'{key}_{fn.__name__}'] = fn(data)
    for fn in double_input_functions:
        indices[f'{key}_{fn.__name__}'] = fn(data, data)



AWAP_indices = {}
data = AWAP_data
for fn in single_input_functions:
    AWAP_indices[f'AWAP_{fn.__name__}'] = fn(data)
for fn in double_input_functions:
    AWAP_indices[f'AWAP_{fn.__name__}'] = fn(data, data)

BARRA_indices = {}
data = BARRA_masked
for fn in single_input_functions:
    BARRA_indices[f'BARRA_{fn.__name__}'] = fn(data)
for fn in double_input_functions:
    BARRA_indices[f'BARRA_{fn.__name__}'] = fn(data, data)
for index in list(BARRA_indices.keys()):
    BARRA_indices[index] = (BARRA_indices[index]*[AWAP_ann > 1])[0] # mask to land

list_of_levels = [levels['year'],	#rr
                  freq_levels['high'],	#rr1
                  levels['hour'],	#sdii
                  freq_levels['low'],	#cwd
                  freq_levels['med'],	#r10mm
                  freq_levels['med'],	#r20mm
                  levels['day'],	#rx1day
                  levels['week'],	#rx5day
                  levels['year'],	#prcptot
                  freq_levels['med'],	#r75p
                  np.arange(0,101,10),	#r75ptot
                  freq_levels['low'],	#r95p
                  np.arange(0,101,10),	#r95ptot
                  freq_levels['very low'],	#r99p
                  np.arange(0,101,10)]	#r99ptot

list_of_cmap = [prcp_colormap, #rr
                freq_colormap, #rr1
                prcp_colormap, #sdii
                freq_colormap, #cwd
                freq_colormap,
                freq_colormap,
                prcp_colormap,
                prcp_colormap,
                prcp_colormap,
                freq_colormap,
                prcp_colormap,
                freq_colormap,
                prcp_colormap,
                freq_colormap,
                prcp_colormap]

keys = list(BARRA_indices.keys())
for index, lvl, cmap in zip(keys, list_of_levels, list_of_cmap):
    map_data = BARRA_indices[index]
    if index in [f'BARRA_{i.__name__}' for i in [rr, rr1, r10mm, r20mm, prcptot, r75p, r95p, r99p]]:
        map_data = map_data/6
    map_prcp(map_data, AWAP_lats, AWAP_lons, title = index, levels = lvl, cmap_label = '', cmap = cmap)
    plt.savefig(f'Documents/images/{index}_SEA_2010-2015.png')
    #plt.close('all')
    plt.show()

keys = list(AWAP_indices.keys())
for index, lvl , cmap in zip(keys, list_of_levels, list_of_cmap):
    map_data = AWAP_indices[index]
    if index in [f'AWAP_{i.__name__}' for i in [rr, rr1, r10mm, r20mm, prcptot, r75p, r95p, r99p]]:
        map_data = map_data/6
    map_prcp(map_data, AWAP_lats, AWAP_lons, title = index, levels = lvl, cmap_label = '', cmap=cmap)
    plt.savefig(f'Documents/images/{index}_SEA_2010-2015.png')
    plt.show()
    plt.close('all')

AWAP_season_data = {'AWAP_DJF' : AWAP_DJF, 'AWAP_MAM': AWAP_MAM, 'AWAP_JJA' : AWAP_JJA, 'AWAP_SON' : AWAP_SON}
BARRA_season_data = {'BARRA_DJF' : BARRA_DJF, 'BARRA_MAM': BARRA_MAM, 'BARRA_JJA' : BARRA_JJA, 'BARRA_SON' : BARRA_SON}

AWAP_season_indices = {}
for season in ['DJF', 'MAM', 'JJA', 'SON']:
    data = AWAP_season_data[f'AWAP_{season}']
    for fn in single_input_functions:
        AWAP_season_indices[f'AWAP_{season}_{fn.__name__}'] = fn(data)
    for fn in double_input_functions:
        AWAP_season_indices[f'AWAP_{season}_{fn.__name__}'] = fn(data, data)

BARRA_season_indices = {}
for season in ['DJF', 'MAM', 'JJA', 'SON']:
    data = BARRA_season_data[f'BARRA_{season}']
    for fn in single_input_functions:
        unmasked_data = fn(data)
        BARRA_season_indices[f'BARRA_{season}_{fn.__name__}'] = fn(data)
    for fn in double_input_functions:
        unmasked_data = fn(data, data)
        BARRA_season_indices[f'BARRA_{season}_{fn.__name__}'] = fn(data, data)

list_of_levels_season = [levels['month'],	#rr
                        freq_levels['med'],	#rr1
                        levels['hour'], 	#sdii
                        freq_levels['very low'],#cwd
                        freq_levels['low'],	#r10mm
                        freq_levels['low'],	#r20mm
                        levels['day'],  	#rx1day
                        levels['day'],  	#rx5day
                        levels['month'],  	#prcptot
                        freq_levels['med'],	#r75p
                        np.arange(0,101,10),	#r75ptot
                        freq_levels['low'],	#r95p
                        np.arange(0,101,10),	#r95ptot
                        freq_levels['very low'],#r99p
                        np.arange(0,101,10)]	#r99ptot



index_names = [fn.__name__ for fn in single_input_functions + double_input_functions]


# need to get the ocean masking neater

for dataset in ['AWAP', 'BARRA']:
    for name, lvl in zip(index_names, list_of_levels_season):
        DJF = (season_indices[f'{dataset}_DJF_{name}']*[AWAP_ann > 1])[0]
        MAM = (season_indices[f'{dataset}_MAM_{name}']*[AWAP_ann > 1])[0]
        JJA = (season_indices[f'{dataset}_JJA_{name}']*[AWAP_ann > 1])[0]
        SON = (season_indices[f'{dataset}_SON_{name}']*[AWAP_ann > 1])[0]
        if name in ['rr', 'rr1', 'r10mm', 'r20mm', 'prcptot']:
            DJF = DJF/6
            MAM = MAM/6
            JJA = JJA/6
            SON = SON/6      
        map_season_prcp(DJF, MAM, JJA, SON, AWAP_lats, AWAP_lons, title = f'{dataset} {name}', cmap_label = '', levels = lvl, norm = BoundaryNorm(lvl, len(lvl)-1)) 
        plt.savefig(f'Documents/images/season_{dataset}_{name}_2010-2015.png')
        plt.close('all')


for index in index_names:
    A = AWAP_indices[f'AWAP_{index}']
    B = BARRA_indices[f'BARRA_{index}']
    map_prcp( 2*(B - A)/(A+B) *(AWAP_ann>1), AWAP_lats, AWAP_lons, title = f"BARRA - AWAP bias {index}", cmap = cm.get_cmap(cmap_custom_RdBu), levels = np.arange(-1, 1.1, 0.2), cmap_extend = 'both', norm = BoundaryNorm( np.arange(-1, 1.1, 0.1), 20), cmap_label = "BARRA - AWAP proportion bias")
    plt.savefig(f"Documents/images/BARRA-AWAP_ratio_bias_{index}_2010-2015.png") 
    plt.show()







for index in index_names:
    A = AWAP_indices[f'AWAP_{index}']
    B = BARRA_indices[f'BARRA_{index}']
    if index in ['rr', 'rr1', 'r10mm', 'r20mm', 'prcptot', 'r75p', 'r95p', 'r99p']:
        A = A/6
        B = B/6
    maximum = np.nanmax(np.abs(B-A))
    result = maximum
    multiplier = 1
    while result >10:
        result //= 10
        multiplier *= 10
    edge = (result + 1 )*multiplier
    if maximum < 10:
        edge = 10
        if maximum < 5:
            edge = 5
    print(f"max = {maximum}, edge = {edge}")
    map_prcp( (B - A) *(AWAP_ann>1), AWAP_lats, AWAP_lons, title = f"BARRA - AWAP difference {index}\n2010-2015", cmap = cm.get_cmap(cmap_custom_RdBu), levels = np.arange(-1*edge, edge * 1.1, 2*edge/10), cmap_extend = 'both', norm = colors.Normalize(vmin=-1*edge, vmax=edge), cmap_label = "BARRA - AWAP difference")
#    plt.savefig(f"Documents/images/BARRA-AWAP_difference_{index}_2010-2015.png") 
    plt.show()










seasons = ['DJF', "MAM", "JJA", "SON"]
for index in index_names:
    diff={}
    for season in seasons:
        A = season_indices[f'AWAP_{season}_{index}']
        B = season_indices[f'BARRA_{season}_{index}']
        diff[season] = (B-A)*(AWAP_ann>1)
    maximum = np.nanmax([np.abs(diff[season]) for season in seasons])
    result = maximum
    multiplier = 1
    while result >10:
        result //= 10
        multiplier *= 10
    edge = (result + 1 )*multiplier
    print(f"Max = {maximum}, edge = {edge}")
    map_season_prcp(diff['DJF'],
                    diff['MAM'],
                    diff['JJA'],
                    diff['SON'],
                    AWAP_lats,
                    AWAP_lons,
                    cmap = cm.get_cmap(cmap_custom_RdBu),
                    norm = colors.Normalize(vmin=-1*edge, vmax=edge),
                    cmap_extend = "both",
                    levels = np.arange(-1*edge, edge * 1.1, 2*edge/10),
                    title = f"BARRA-AWAP {index}\n2010-2015", 
                    cmap_label = "Difference of BARRA from AWAP")
    plt.savefig(f'Documents/images/BARRA-AWAP_season_diff_{index}_2010-2015.png')
    plt.show()



seasons = ['DJF', "MAM", "JJA", "SON"]
for index in index_names:
    ratio={}
    for season in seasons:
        A = season_indices[f'AWAP_{season}_{index}']
        B = season_indices[f'BARRA_{season}_{index}']
        ratio[season] = 2*(B-A)/(B+A)*(AWAP_ann>1)
    maximum = np.nanmax([np.abs(ratio[season]) for season in seasons])
    print(f"Max prop error = {maximum}")
    map_season_prcp(ratio['DJF'],
                    ratio['MAM'],
                    ratio['JJA'],
                    ratio['SON'],
                    AWAP_lats,
                    AWAP_lons,
                    cmap = cm.get_cmap(cmap_custom_RdBu),
                    norm = colors.Normalize(vmin=-1, vmax=1),
                    cmap_extend = "both",
                    levels = np.arange(-1, 1.1, 0.2),
                    title = f"Ratio BARRA-AWAP {index}\n2010-2015", 
                    cmap_label = "Ratio difference of BARRA from AWAP")
    plt.savefig(f'Documents/images/BARRA-AWAP_season_ratio_{index}_2010-2015.png')
    plt.show()



