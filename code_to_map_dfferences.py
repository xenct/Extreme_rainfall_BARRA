"""Code I need to map seasonal and annual indices"""

# packages for loading netCDFs
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats.mstats import mquantiles
from scipy.stats import spearmanr, linregress
from datetime import timedelta, date, datetime
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
import cartopy.crs as ccrs
import matplotlib.colors as colors

# Getting data from netCDF files

def load_2D_netCDF(filename, var_name = "mean_prcp", lat_name = "lats", lon_name = "lons"):
    """
    This function loads a two dimensional netCDF.
    Give filename as a string.
    Give name of measured variable.
    Give the names of the two spatial coordinates.
    The function returns the variable, and the two dimenstions
"""
    data = Dataset(filename, 'r')
    var = data[var_name][:]
    lats = data[lat_name][:]
    lons = data[lon_name][:]
    data.close()
    return var, lats, lons

def load_3D_netCDF(filename, var_name = "prcp", lat_name = "lats", lon_name = "lons", time_name = "times"):
    """
    This function loads a three dimensional netCDF.
    Give filename as a string.
    Give name of the measured variable.
    Give the names of the two spatial coordinates.
    Give the name of the time dimension.
    The function returns the variable, the two spatial dimensions, and the times.
"""
    data = Dataset(filename, 'r')
    var = data[var_name][:]
    lats = data[lat_name][:]
    lons = data[lon_name][:]
    times = data[time_name][:]
    data.close()
    return var, lats, lons, times

def lat_lon_mask(lons_full, lats_full, lon_min, lon_max, lat_min, lat_max):
    """Thie function takes a full list of latitudes and longitudes, and minimum and maximum values for lats and lons. The function returns a 2D mask which specifies True for every coordinate between (and including) the boundaries. the function also returns the shortened lats and lons"""
    # Mask lons
    lon_mask = (lons_full >= lon_min) & (lons_full <= lon_max)
    lons = lons_full[lon_mask]
    # Mask lats
    lat_mask = (lats_full >= lat_min) & (lats_full <= lat_max)
    lats = lats_full[lat_mask]
    # make 2D mask
    lat_lon_mask = lon_mask[np.newaxis, :] & lat_mask[:, np.newaxis]
    return lat_lon_mask, lats, lons

# Mapping AWAP and BARRA data

# specify the colours for the colours mapping for precipitation
prcp_colours = [
     "#FFFFFF", 
     '#ffffd9', 
     '#edf8b1',
     '#c7e9b4',
     '#7fcdbb',
     '#41b6c4',
     '#1d91c0',
     '#225ea8',
     '#253494',
     '#081d58',
     "#4B0082"]
prcp_colormap = ListedColormap(prcp_colours)

# Specify the levels for each colour segment. 
# These are suitable for Victoria annual rainfall totals for different periods
levels = {}
levels["hour"]  = [0., 0.2,   1,   5,  10,  20,  30,   40,   60,   80,  100,  150]
levels["day"]   = [0., 0.2,  5, 10,  20,  30,  40,  60,  100,  150,  200,  300]
levels["week"]  = [0., 0.2,  10,  20,  30,  50, 100,  150,  200,  300,  500, 1000]
levels["month"] = [0.,  10,  20,  30,  40,  50, 100,  200,  300,  500, 1000, 1500]
levels["year"]  = [0.,  50, 100, 200, 300, 400, 600, 1000, 1500, 2000, 3000, 5000]

# Specify colormaps for frequency plots
# Define a set of levels for annual frequency exceedences
freq_levels = {}
freq_levels['very low'] = [0, 1, 2, 3, 4, 5, 10, 20]
freq_levels['low'] = [0, 1, 2, 5, 10, 20, 30, 40]
freq_levels['med'] = [0, 1, 5, 10, 20, 30, 60, 100]
freq_levels['high'] = [0, 20, 45, 60, 90, 150, 200, 250]
freq_levels['very high'] = [0, 30, 60, 90, 150, 210, 270, 366]

# specify the colours for the frequency colours mapping, fewer than the precipitation
freq_colours = [
     "#FFFFFF", 
     '#edf8b1',
     '#7fcdbb',
     '#1d91c0',
     '#253494',
     '#081d58',
     "#4B0082"]
freq_colormap = ListedColormap(freq_colours)

def draw_cbar_prcp(levels = levels["year"]):
    """
This function draws a colour bar, extended at the max. 
It is  YlGnBu colourscale with 11 levels, appropriate for annual rainfall. 
The position of the color bar is centred and to the right of the existing plot.
"""
    cbar = plt.colorbar(ticks = levels[:-1], shrink = 0.6, extend = "max", anchor = (0,0.5))
    cbar.ax.set_ylabel(f"Precipitation (mm)")
    cbar.ax.set_xticklabels(levels)
    return

# load AWAP and BARRA data
prcp_data = {}
for seas in  ['', 'DJF', 'MAM', 'JJA', 'SON']:
    if len(seas)<3:
        AWAP_file = '/g/data3/w42/gt3409/AWAP/AWAP_PRCP_2010-2015_0.11deg_small.nc'
        prcp_data['AWAP_ann'], AWAP_lats, AWAP_lons = load_2D_netCDF( AWAP_file, 'pre', lat_name='lat', lon_name='lon')
        BARRA_file = '/g/data3/w42/gt3409/BARRA_R/BARRA_R_daily_prcp_2010-2015_small.nc'
        prcp_data['BARRA_ann'], BARRA_lats, BARRA_lons = load_2D_netCDF(BARRA_file, 'prcp')
    else:
        AWAP_file = f'/g/data3/w42/gt3409/AWAP/AWAP_PRCP_2010-2015_0.11deg_small_{seas}.nc'
        prcp_data[f'AWAP_{seas}'], _, _ = load_2D_netCDF( AWAP_file, 'pre', lat_name='lat', lon_name='lon')
        BARRA_file = f'/g/data3/w42/gt3409/BARRA_R/BARRA_R_daily_prcp_2010-2015_small_{seas}.nc'
        prcp_data[f'BARRA_{seas}'], _, _ = load_2D_netCDF(BARRA_file, 'prcp')

AWAP_ann = prcp_data['AWAP_ann']

def map_prcp(data, lats, lons, title = "Title", projection = ccrs.PlateCarree(), latlonbox = [135,155,-45,-30], cmap = prcp_colormap, levels = levels['year'], cmap_label = "cmap label", cmap_extend = 'max', norm = BoundaryNorm(levels['year'], len(levels['year'])-1)):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection=projection)
    ax.set_extent(latlonbox) 
    im = plt.pcolormesh(lons, lats, data, transform = projection, cmap = cmap, norm = norm)
#    ax.scatter(np.array(list(HQ_info.values()))[:,1], np.array(list(HQ_info.values()))[:,0], transform = projection, c = 'k', marker = '.')
    ax.coastlines('10m')
    if cmap_extend == "max":
        cbar_ticks = levels[:-1]
    else: # if cbar_ticks == "both"
        cbar_ticks = levels[:]
    cbar = plt.colorbar(im, ticks = cbar_ticks, shrink = 0.8, extend = cmap_extend)
    cbar.ax.set_ylabel(cmap_label)
    cbar.ax.set_xticklabels(levels)
    plt.title(title)
    plt.tight_layout()
    return

def map_season_prcp(DJF, MAM, JJA, SON, lats, lons, title = "Title", projection = ccrs.PlateCarree(), latlonbox = [135,155,-45,-30], cmap = prcp_colormap, levels = levels['year'], cmap_label = "cmap label", AWAP_ann = AWAP_ann, norm = BoundaryNorm(levels['year'], len(levels['year'])-1), cmap_extend = "max"):
    seasons = [DJF, MAM, JJA, SON]
    season_title = ['DJF', 'MAM', 'JJA', 'SON']
    fig = plt.figure()
    for i, data in zip(range(4), seasons):
        ax = fig.add_subplot(2,2,i+1, projection=projection)
        ax.set_extent(latlonbox) 
        #data[AWAP_ann<1]=0
        im = plt.pcolormesh(lons, lats, data, transform = projection, cmap = cmap, norm = norm)
#        ax.scatter(np.array(list(HQ_info.values()))[:,1], np.array(list(HQ_info.values()))[:,0], transform = projection, c = 'k', marker = '.')
        ax.coastlines('10m')
        plt.title(f"{season_title[i]}")
    ax = fig.add_axes([0,0,1.1,1], visible = False) #[left, bottom, width, height]
    plt.subplots_adjust(right = 0.85)
    if cmap_extend == "max":
        cbar_ticks = levels[:-1]
    else: # if cbar_ticks == "both"
        cbar_ticks = levels[:]
    cbar = plt.colorbar(im, ticks = cbar_ticks, shrink = 0.6, extend = cmap_extend, fraction = 0.2)
    cbar.ax.set_ylabel(cmap_label)
    cbar.ax.set_xticklabels(levels)
    plt.suptitle(title)
    return

single_input_functions = [rr, rr1, sdii, cwd, r10mm, r20mm, rx1day, rx5day]
double_input_functions = [r75p, r75ptot, r95p, r95ptot, r99p, r99ptot]
index_names = [fn.__name__ for fn in single_input_functions + double_input_functions]




#for every index plot the annual difference plot of BARRA form AWAP
for index in index_names:
    A = indices[f'AWAP_ann_{index}']
    B = indices[f'BARRA_ann_{index}']
    if index in ['rr', 'rr1', 'r10mm', 'r20mm', 'r75p', 'r95p', 'r99p']:
        A = A/6
        B = B/6
    # This part Auto adjusts the limits of the colour range
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
    # print(f"max = {maximum}, edge = {edge}")
    # map the outcome
    map_prcp( (B - A) *(AWAP_ann>1), AWAP_lats, AWAP_lons, title = f"BARRA - AWAP difference {index}\n2010-2015", cmap = cm.get_cmap(cmap_custom_RdBu), levels = np.arange(-1*edge, edge * 1.1, 2*edge/10), cmap_extend = 'both', cmap_label = "BARRA - AWAP difference", norm = colors.Normalize(vmin=-1*edge, vmax=edge))
#    plt.savefig(f"Documents/images/BARRA-AWAP_difference_{index}_2010-2015.png") 
    plt.show()

# for every seasonal plot, map the difference of BARRA from AWAP
seasons = ['DJF', "MAM", "JJA", "SON"]
edges = [1000, 100, 10, 20, 25, 25, 250, 250, 25, 30, 10, 30, 5, 30, ]
for index, edge in zip(index_names, edges):
    diff={}
    for season in seasons:
        A = indices[f'AWAP_{season}_{index}']
        B = indices[f'BARRA_{season}_{index}']
        diff[season] = (B-A)*(AWAP_ann>1)
#auto scale the cbar
#    maximum = np.nanmax([np.abs(diff[season]) for season in seasons])
#    result = maximum
#    multiplier = 1
#    while result >10:
#        result //= 10
#        multiplier *= 10
#    edge = (result + 1 )*multiplier
#    print(f"Max = {maximum}, edge = {edge}")
# map and plot
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
    plt.savefig(f'Documents/images/BARRA-AWAP_season_diff_{index}_manscale_2010-2015.png')
plt.show()



# for every seasonal plot, map the difference of BARRA from AWAP
seasons = ['DJF', "MAM", "JJA", "SON"]
edge = 30
for threshold in [1,2,3,4,5]:
    diff={}
    for season in seasons:
        A = rr1(prcp_data[f'AWAP_{season}'], threshold)
        B = rr1(prcp_data[f'BARRA_{season}'], threshold)
        diff[season] = (B-A)*(AWAP_ann>1)
#auto scale the cbar
#    maximum = np.nanmax([np.abs(diff[season]) for season in seasons])
#    result = maximum
#    multiplier = 1
#    while result >10:
#        result //= 10
#        multiplier *= 10
#    edge = (result + 1 )*multiplier
#    print(f"Max = {maximum}, edge = {edge}")
# map and plot
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
                    title = f"BARRA-AWAP R{threshold}mm\n2010-2015", 
                    cmap_label = "Difference of BARRA from AWAP")
#    plt.savefig(f'Documents/images/BARRA-AWAP_season_diff_{index}_manscale_2010-2015.png')
plt.show()


# For each season plot a line. The line represent the difference in 
# frequency of exceedence of each mm threshold comparing BARRA to AWAP
# at 0.11 deg resolution
diff = {}                               
for seas in seasons:       
   season = []                 
    for threshold in range(0, 50):
        A = rr1(prcp_data[f'AWAP_{seas}'], threshold)
        B = rr1(prcp_data[f'BARRA_{seas}'], threshold)
        season.append(np.nanmean((B-A)*(AWAP_ann >1)))
        diff[f'{seas}'] = season

#plot lines
for sss in seasons:
    plt.plot([np.nan]+diff[sss][:])
plt.plot([0 for i in range(51)], color = 'k')
plt.legend(diff.keys())
plt.title("BARRA - AWAP southeastern Australia\n2010 - 2015")
plt.xlim(0, 50)
plt.xlabel("daily rainfall threshold (mm)")
plt.ylabel("SE Australia annual frequency area mean difference")
plt.ylim(-3,3)
plt.show()





