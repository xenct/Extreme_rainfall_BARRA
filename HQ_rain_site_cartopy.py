# this script reads in the locations of the 112 HQ rain gauges and plots them as dots for reference

import csv
HQ_info = {}
with open('Documents/ACORN_SAT_site_locations.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        row = list(row)
        try:
            HQ_info[row[0]] = (float(row[1]), float(row[2]))
        except:
            continue




#map_prcp(data=np.sum(AWAP_data,0)/6, lats=AWAP_lats, lons=AWAP_lons)
#map_prcp(data=np.sum(BARRA_data,0)/6, lats=BARRA_lats, lons=BARRA_lons)


# This next part is to select the points between -44 and -30 lats, and 135 and 155 lons
import matplotlib.colors as colors

#used cdos to make prcp data of the same size constrained between -44 and -30 lats, and 135 and 155 lons

def map_difference(data1, data2, lats, lons, title = "data1 - data2", projection = ccrs.PlateCarree(), latlonbox = [135,155,-45,-30], cmap = "RdBu", levels = np.arange(-500, 500, 20), cmap_label = "cmap label"):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection=projection)
    ax.set_extent(latlonbox) 
    norm = colors.Normalize(vmin=-500, vmax=500)
    im = plt.pcolormesh(lons, lats, (data1-data2), transform = projection, cmap = cmap, norm = norm)
#    ax.scatter(np.array(list(HQ_info.values()))[:,1], np.array(list(HQ_info.values()))[:,0], transform = projection, c = 'k', marker = '.')
    ax.coastlines('10m')
    cbar = plt.colorbar(im, shrink = 0.8, extend = "both")
    cbar.ax.set_ylabel(cmap_label)
    cbar.ax.set_xticklabels(levels)
    plt.title(title)
    plt.tight_layout()
    return

# Annual total rainfall over land

BARRA_data, BARRA_lats, BARRA_lons, BARRA_times = load_3D_netCDF('/g/data3/w42/gt3409/BARRA_R/BARRA_R_daily_prcp_2010-2015_small.nc', time_name='time')

AWAP_data, AWAP_lats, AWAP_lons, AWAP_times = load_3D_netCDF('/g/data3/w42/gt3409/AWAP/AWAP_PRCP_2010-2015_0.11deg_small.nc', 'pre', 'lat', 'lon', 'time')         

AWAP_ann = np.sum(AWAP_data, 0)/6
BARRA_ann = np.sum(BARRA_data, 0)/6
# make ocean precipitation totals in BARRA zero for comparison with AWAP
BARRA_ann[AWAP_ann<1]=0

map_difference(BARRA_ann, AWAP_ann, AWAP_lats, AWAP_lons, title = "BARRA annual minus AWAP annual totals\n2010-2015", cmap_label = "Precipitation difference (mm per year)")
plt.savefig("Documents/images/BARRA_sub_AWAP_ann_diff.png")
plt.show()


def map_ratio(data1, data2, lats, lons, title = "data1 - data2", projection = ccrs.PlateCarree(), latlonbox = [135,155,-45,-30], cmap = "RdBu", levels = np.arange(-1, 1, 0.2), cmap_label = "cmap label", norm = colors.Normalize(vmin=-1, vmax=1)):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection=projection)
    ax.set_extent(latlonbox) 
    map_data = (2*(data1-data2)/(data1+data2))*(AWAP_ann>1)
    im = plt.pcolormesh(lons, lats, map_data, transform = projection, cmap = cmap, norm = norm)
#    ax.scatter(np.array(list(HQ_info.values()))[:,1], np.array(list(HQ_info.values()))[:,0], transform = projection, c = 'k', marker = '.')
    ax.coastlines('10m')
    cbar = plt.colorbar(im, shrink = 0.8, extend = "both")
    cbar.ax.set_ylabel(cmap_label)
    cbar.ax.set_xticklabels(levels)
    plt.title(title)
    plt.tight_layout()
    return

map_ratio(BARRA_ann, AWAP_ann, AWAP_lats, AWAP_lons)
plt.savefig("Documents/images/prop_of_BARRA_to_AWAP_ann.png")


# Map seasons
projection = ccrs.PlateCarree()
cmap = "RdBu"
latlonbox = [135,155,-45,-30]
lats = BARRA_lats
lons = BARRA_lons
seasons = ['DJF', 'MAM', 'JJA', 'SON']

# load all seasonal data
BARRA_DJF, _, _, _ = load_3D_netCDF('/g/data/w42/gt3409/BARRA_R/BARRA_R_daily_prcp_2010-2015_small_DJF.nc', time_name = 'time')
BARRA_MAM, _, _, _ = load_3D_netCDF('/g/data/w42/gt3409/BARRA_R/BARRA_R_daily_prcp_2010-2015_small_MAM.nc', time_name = 'time')
BARRA_JJA, _, _, _ = load_3D_netCDF('/g/data/w42/gt3409/BARRA_R/BARRA_R_daily_prcp_2010-2015_small_JJA.nc', time_name = 'time')
BARRA_SON, _, _, _ = load_3D_netCDF('/g/data/w42/gt3409/BARRA_R/BARRA_R_daily_prcp_2010-2015_small_SON.nc', time_name = 'time')

AWAP_DJF, _, _, _ = load_3D_netCDF('/g/data/w42/gt3409/AWAP/AWAP_PRCP_2010-2015_0.11deg_small_DJF.nc', var_name='pre', lat_name = 'lat', lon_name= 'lon', time_name='time')
AWAP_MAM, _, _, _ = load_3D_netCDF('/g/data/w42/gt3409/AWAP/AWAP_PRCP_2010-2015_0.11deg_small_MAM.nc', var_name='pre', lat_name = 'lat', lon_name= 'lon', time_name='time')
AWAP_JJA, _, _, _ = load_3D_netCDF('/g/data/w42/gt3409/AWAP/AWAP_PRCP_2010-2015_0.11deg_small_JJA.nc', var_name='pre', lat_name = 'lat', lon_name= 'lon', time_name='time') 
AWAP_SON, _, _, _ = load_3D_netCDF('/g/data/w42/gt3409/AWAP/AWAP_PRCP_2010-2015_0.11deg_small_SON.nc', var_name='pre', lat_name = 'lat', lon_name= 'lon', time_name='time') 


fig = plt.figure()
ax = fig.add_subplot(2,2,1, projection=projection)
ax.set_extent(latlonbox)
plt.pcolormesh(lons, lats, np.sum(AWAP_DJF,0)/6, transform = projection, cmap = prcp_colormap)


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

map_season_prcp(np.sum(AWAP_DJF,0), np.sum(AWAP_MAM,0), np.sum(AWAP_JJA,0), np.sum(AWAP_SON,0), lats, lons)
map_season_prcp(np.sum(BARRA_DJF,0), np.sum(BARRA_MAM,0), np.sum(BARRA_JJA,0), np.sum(BARRA_SON,0), lats, lons)


map_season_prcp(season_mean['BARRA_DJF_array'] - season_mean['AWAP_DJF_array'],
                season_mean['BARRA_MAM_array'] - season_mean['AWAP_MAM_array'],
                season_mean['BARRA_JJA_array'] - season_mean['AWAP_JJA_array'],
                season_mean['BARRA_SON_array'] - season_mean['AWAP_SON_array'],
                lats,
                lons,
                cmap = "RdBu",
                norm = colors.Normalize(vmin=-200, vmax=200),
                cmap_extend = "both",
                levels = np.arange(-200, 210, 50),
                title = "BARRA - AWAP season average\n2010-2015", 
                cmap_label = "Precipitation difference (mm)")
     
map_season_prcp(season_mean['BARRA_DJF_array'] / season_mean['AWAP_DJF_array']-1,
                season_mean['BARRA_MAM_array'] / season_mean['AWAP_MAM_array']-1,
                season_mean['BARRA_JJA_array'] / season_mean['AWAP_JJA_array']-1,
                season_mean['BARRA_SON_array'] / season_mean['AWAP_SON_array']-1,
                lats,
                lons,
                cmap = "RdBu",
                norm = colors.Normalize(vmin=-1, vmax=1),
                cmap_extend = "both",
                levels = np.arange(-1, 1.1, .2),
                title = "(BARRA - AWAP)/AWAP season average\n2010-2015", 
                cmap_label = "Proportion difference of BARRA from AWAP")

map_season_prcp(season_max['BARRA_DJF_array'] - season_max['AWAP_DJF_array'],
                season_max['BARRA_MAM_array'] - season_max['AWAP_MAM_array'],
                season_max['BARRA_JJA_array'] - season_max['AWAP_JJA_array'],
                season_max['BARRA_SON_array'] - season_max['AWAP_SON_array'],
                lats,
                lons,
                cmap = "RdBu",
                norm = colors.Normalize(vmin=-100, vmax=100),
                cmap_extend = "both",
                levels = np.arange(-100, 101, 20),
                title = "BARRA - AWAP season max\n2010-2015", 
                cmap_label = "Difference of BARRA from AWAP (mm)")

map_season_prcp(season_max['BARRA_DJF_array'] / season_max['AWAP_DJF_array']-1,
                season_max['BARRA_MAM_array'] / season_max['AWAP_MAM_array']-1,
                season_max['BARRA_JJA_array'] / season_max['AWAP_JJA_array']-1,
                season_max['BARRA_SON_array'] / season_max['AWAP_SON_array']-1,
                lats,
                lons,
                cmap = "RdBu",
                norm = colors.Normalize(vmin=-1, vmax=1),
                cmap_extend = "both",
                levels = np.arange(-1, 1.1, .20),
                title = "BARRA - AWAP season max\n2010-2015", 
                cmap_label = "Proportion difference of BARRA from AWAP")

diff={}
for season in ['DJF', "MAM", "JJA", "SON"]:
    A = np.array(season_max[f'AWAP_{season}_array'])
    B = np.array(season_max[f'BARRA_{season}_array'])
    diff[season] = 2*(B-A)/(A+B)

map_season_prcp(diff['DJF'],
                diff['MAM'],
                diff['JJA'],
                diff['SON'],
                lats,
                lons,
                cmap = "RdBu",
                norm = colors.Normalize(vmin=-1, vmax=1),
                cmap_extend = "both",
                levels = np.arange(-1, 1.1, .20),
                title = "2(B-A)/(A+B) season max\n2010-2015", 
                cmap_label = "Proportion difference of BARRA")


diff={}
for season in ['DJF', "MAM", "JJA", "SON"]:
    A = np.array(season_R99p[f'AWAP_{season}_array'])
    B = np.array(season_R99p[f'BARRA_{season}_array'])
    diff[season] = 2*(B-A)/(A+B)

map_season_prcp(diff['DJF'],
                diff['MAM'],
                diff['JJA'],
                diff['SON'],
                lats,
                lons,
                cmap = "RdBu",
                norm = colors.Normalize(vmin=-1, vmax=1),
                cmap_extend = "both",
                levels = np.arange(-1, 1.1, .20),
                title = "2(B-A)/(A+B) season 99th percentile\n2010-2015", 
                cmap_label = "Proportion difference of BARRA")

map_season_prcp(season_R99p['BARRA_DJF_array'] -season_R99p['AWAP_DJF_array'],
                season_R99p['BARRA_MAM_array'] - season_R99p['AWAP_MAM_array'],
                season_R99p['BARRA_JJA_array'] - season_R99p['AWAP_JJA_array'],
                season_R99p['BARRA_SON_array'] - season_R99p['AWAP_SON_array'],
                lats,
                lons,
                cmap = "RdBu",
                norm = colors.Normalize(vmin=-30, vmax=30),
                cmap_extend = "both",
                levels = np.arange(-30, 31.1, 5),
                title = "BARRA - AWAP season 99th percentile\n2010-2015", 
                cmap_label = "Difference of BARRA from AWAP (mm)")


map_season_prcp(season_R99p['BARRA_DJF_array'],
                season_R99p['BARRA_MAM_array'],
                season_R99p['BARRA_JJA_array'],
                season_R99p['BARRA_SON_array'],
                lats,
                lons,
                cmap = prcp_colormap,
                norm = colors.Normalize(vmin=-30, vmax=30),
                cmap_extend = "both",
                levels = np.arange(-30, 31.1, 5),
                title = "BARRA - AWAP season 99th percentile\n2010-2015", 
                cmap_label = "Difference of BARRA from AWAP (mm)")














