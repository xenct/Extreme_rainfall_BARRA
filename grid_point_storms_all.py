import matplotlib.pyplot as plt
import numpy as np

BARRA_raw = prcp_data['BARRA_ann']

   
def map_prcp_subplot(data, lats, lons, nrows, ncols, index, title = "Title", projection = ccrs.PlateCarree(), latlonbox = [135,155,-45,-30], cmap = prcp_colormap, levels = levels['year'], cmap_label = "cmap label", cmap_extend = 'max', show_n = False):
    norm = BoundaryNorm(levels, len(levels)-1)
    ax = plt.subplot(nrows, ncols, index, projection=projection)
    ax.set_extent(latlonbox) 
    im = plt.pcolormesh(lons, lats, data, transform = projection, cmap = cmap, norm = norm)
    ax.coastlines('10m')
    plt.title(title)
    if show_n:
        ax.set_title(f"n = {np.sum(gps_detection[gps_filter])}",pad = -10, fontsize = 10 )
    return

def map_ratio_subplot(data1, data2, lats, lons, nrows, ncols, index, levels=np.arange(-1,1.1, 0.1),title = "data1 / data2", projection = ccrs.PlateCarree(), latlonbox = [135,155,-45,-30], cmap = cmap_custom_RdBu):
    norm = BoundaryNorm(levels, len(levels)-1)
    ax = plt.subplot(nrows, ncols, index, projection=projection)
    ax.set_extent(latlonbox) 
    map_data = 2*(data1 - data2)/(data1+data2)*(AWAPmax>1)
    im = plt.pcolormesh(lons, lats, map_data, transform = projection, cmap = cmap, norm = norm)                     
    ax.coastlines('10m')
    return

def timeseries_subplot(data, nrows, ncols, index, title = 'filter'):
    plt.subplot(nrows, ncols, index)
    plt.plot(np.sum(data, (1,2)))
    plt.ylim((0,400))   
    plt.title(title,pad = -10, fontsize = 10)
    return

BARRA_raw_1d_prcp = np.reshape(BARRA_raw, BARRA_raw.size)
def hist_subplot(data, nrows, ncols, index):
    plt.subplot(nrows, ncols, index)
    plt.hist(BARRA_raw_1d_prcp, bins = np.arange(0, 500, 25), log = True, color = 'royalblue', alpha = 0.3)
    data_1d = np.reshape(data, data.size)
    data_1d = data_1d[~np.isnan(data_1d)] # remove the nans
    plt.hist(data_1d, bins = np.arange(0, 500, 25), log = True, color = 'r', alpha= 0.3)
    plt.ylim((1, 10**8))
    plt.xlim((0,500))
    return



gps_detection = {}

gps_detection['AWAP_12km'] = np.zeros(prcp_data['AWAP_ann'].shape)
AWAP_12km        = prcp_data['AWAP_ann']
print('AWAP_12km written')

gps_detection['BARRA_raw'] = np.zeros(prcp_data['BARRA_ann'].shape)
BARRA_raw        = prcp_data['BARRA_ann']
print('BARRA_raw written')

gps_detection['threshold_200mm'] = (BARRA_raw > 200)
threshold_200mm  = BARRA_raw * (1 - gps_detection['threshold_200mm'])
print('threshold_200mm written')

gps_detection['threshold_300mm'] = (BARRA_raw > 300)
threshold_300mm  = BARRA_raw * (1 - gps_detection['threshold_300mm'])
print('threshold_300mm written')

AWAPmax          = np.nanmax(prcp_data['AWAP_ann'],0)
print('AWAPmax written')

gps_detection['AWAPmax_times_15'] = ((BARRA_raw > (AWAPmax * 1.5))*
                                     (np.sum(AWAP_12km, 0) > 0)
                                     )
AWAPmax_times_15 = BARRA_raw * (1 - gps_detection['AWAPmax_times_15'])
print('AWAPmax_times_15 written')

gps_detection['AWAPmax_times_2'] = ((BARRA_raw > (AWAPmax * 2))*
                                    (np.sum(AWAP_12km, 0) > 0)
                                    )
AWAPmax_times_2  = BARRA_raw * (1 - gps_detection['AWAPmax_times_2'])
print('AWAPmax_times_2 written')

gps_detection['AWAPmax_plus_100'] = (BARRA_raw > (AWAPmax + 100))
AWAPmax_plus_100 = BARRA_raw * (1 - gps_detection['AWAPmax_plus_100'])
print('AWAPmax_plus_100 written')

# Filter out the values which are 100 over the record AND more than double the record:
gps_detection['AWAPmax_x2_plus100']= (((BARRA_raw > (AWAPmax + 100))&
                                      (BARRA_raw > (AWAPmax * 2. ))
                                       ) *
                                       (AWAPmax > 1)
                                      )
AWAPmax_x2_plus100=BARRA_raw * (1 - gps_detection['AWAPmax_x2_plus100'])
print('AWAPmax_x2_plus100 written')

# Filter out the values which are 100 over the record AND more than 150% the record:
gps_detection['AWAPmax_x15_plus100']= (((BARRA_raw > (AWAPmax + 100))&
                                      (BARRA_raw > (AWAPmax * 1.5 ))
                                       ) *
                                       (AWAPmax > 1)
                                      )
AWAPmax_x15_plus100=BARRA_raw * (1 - gps_detection['AWAPmax_x15_plus100']) * (AWAPmax > 1)
print('AWAPmax_x15_plus100 written')

# use the filter decsribe in Green et al 2012:
#data_set = BARRA_raw
#BARRA_Green_2012_filter = np.empty(data_set.shape)
#for i, data in enumerate(data_set):
#    print(f'day {i} calculating ...')
#    BARRA_Green_2012_filter[i] = ndimage.generic_filter(data, 
#                                                        filter_green,
#                                                        size = (3,3),
#                                                        mode = 'constant',
#                                                        cval = np.NaN)
#gps_detection['BARRA_Green_2012'] = BARRA_Green_2012_filter
#BARRA_Green_2012 = BARRA_raw * (1 - gps_detection['BARRA_Green_2012'])
#print('BARRA_Green_2012 written')

# use the filter decsribe in Green et al 2012 modified for more extremes:
#data_set = BARRA_raw
#BARRA_Green_modified_filter = np.empty(data_set.shape)
#for i, data in enumerate(data_set):
#    print(f'day {i} calculating ...')
#    BARRA_Green_modified_filter[i] = ndimage.generic_filter(data, 
#                                                        filter_green_modified,
#                                                        size = (3,3),
#                                                        mode = 'constant')
#gps_detection['BARRA_Green_modified'] = BARRA_Green_modified_filter
#BARRA_Green_modified = BARRA_raw * (1 - gps_detection['BARRA_Green_modified'])
#print('BARRA_Green_2012 written')

# matrix of plots
grid_point_filters = [AWAP_12km,
                      BARRA_raw,
                      threshold_200mm,
                      threshold_300mm,
                      AWAPmax_times_15,
                      AWAPmax_times_2,
                      AWAPmax_plus_100,
                      AWAPmax_x2_plus100,
                      AWAPmax_x15_plus100,
#                      BARRA_Green_2012,
#                      BARRA_Green_modified,
                      ]

list_of_plots = ['timeseries',
                 'map_grid_point_storms',
                 'hist_distribution',
                 'map_annual',
                 'map_rx1day',
                 'map_rx1day_ratio_to_AWAP',
                 'map_rx5day',
                 'map_r99ptot',
                 ]
list_of_filters = ['AWAP_12km',
                   'BARRA_raw',
                   'threshold_200mm',
                   'threshold_300mm',
                   'AWAPmax_times_15',
                   'AWAPmax_times_2',
                   'AWAPmax_plus_100',
                   'AWAPmax_x2_plus100',
                   'AWAPmax_x15_plus100',
#                   'BARRA_Green_2012',
#                   'BARRA_Green_modified',
                      ]


nrow = len(grid_point_filters)
ncol = len(list_of_plots)

plt.figure(figsize=(25, 20))
for i in range(len(list_of_filters)): 
    print(f'Now mapping filter: {list_of_filters[i]}...')
    gps_filter = list_of_filters[i]
    #timeseries plot of the number of detections over time
    timeseries_subplot(data = gps_detection[gps_filter], 
                       nrows = nrow, 
                       ncols = ncol,
                       index = ncol*i+1,
                       title = f'{list_of_filters[i]}',
                       )
    # map of the detections over SE Aust for the total duration
    map_prcp_subplot(np.nansum(gps_detection[gps_filter],0), 
                     BARRA_lats,
                     BARRA_lons, 
                     nrows = nrow, 
                     ncols = ncol,
                     index = ncol*i+2,
                     levels=freq_levels['low'],
                     title = '',
                     cmap  = freq_colormap,
                     show_n = True
                     )
    # Histogram of rainfall amounts
    hist_subplot(grid_point_filters[i], 
                       nrows = nrow, 
                       ncols = ncol,
                       index = ncol*i+3,
                       )
    # Map of total prcp after removing applying filter
    map_prcp_subplot(np.nansum(grid_point_filters[i],0)/6, 
                     BARRA_lats,
                     BARRA_lons, 
                     nrows = nrow, 
                     ncols = ncol,
                     index = ncol*i+4,
                     levels=levels['year'],
                     title = '')
    # Map of rx1day after applying filter
    map_prcp_subplot(np.nanmax(grid_point_filters[i],0), 
                     BARRA_lats,
                     BARRA_lons, 
                     nrows = nrow, 
                     ncols = ncol,
                     index = ncol*i+5,
                     levels=levels['week'],
                     title = '')   
    # Map of rx1day BARRA/AWAP ratio after applying filter
    map_ratio_subplot(data1 = np.nanmax(grid_point_filters[i],0), 
                      data2 = AWAPmax, 
                      lats  = BARRA_lats,
                      lons  = BARRA_lons, 
                      nrows = nrow, 
                      ncols = ncol,
                      index = ncol*i+6,
                      title = '')
    # Map of rx5day after applying filter
    map_prcp_subplot(rx5day(grid_point_filters[i]), 
                     BARRA_lats,
                     BARRA_lons, 
                     nrows = nrow, 
                     ncols = ncol,
                     index = ncol*i+7,
                     levels=levels['week'],
                     title = '')   
    # Map of r99ptot after applying filter
    map_prcp_subplot(r99ptot(grid_point_filters[i], AWAP_12km), 
                     BARRA_lats,
                     BARRA_lons, 
                     nrows = nrow, 
                     ncols = ncol,
                     index = ncol*i+8,
                     levels=np.arange(0,25, 5), # change this color scale
                     title = '')   

