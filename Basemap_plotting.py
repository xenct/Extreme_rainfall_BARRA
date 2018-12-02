# Basemap mapping


def map_AWAP(data, lats, lons, lon_min = 135, lon_max = 155, lat_min = -45, lat_max = -30, titles_on = True, title = "AWAP Precipitation", levels = levels["year"], colormap = prcp_colormap, cmap_label = "Precipitation (mm)"):
    """
    This function takes a 2D data set of a variable from AWAP and maps the data on miller projection. 
    The map default span is longitude between 135E and 155E, and the span for latitudes is -45 to -30, this is SE Australia. 
    The colour scale is YlGnBu at 11 levels. 
    The levels specifed are suitable for annual rainfall totals for SE Australia. 
    From the AWAP netCDF, the mean rainfall data should be multiplied by 365.
"""
    # order the lats and lons
    lats.sort()
    lats = np.flip(lats,0) # this is the important sorting for AWAP, otherwise the map is flipped thru the horizontal axis.
    lons.sort()
    # specify map projection, bounds, and resolution
    map = Basemap(projection = "mill", llcrnrlon = lon_min, llcrnrlat = lat_min, urcrnrlon = lon_max, urcrnrlat = lat_max, resolution = 'l')
    map.drawcoastlines()
    map.drawmapboundary()
    # draw lats and lon grid for every 5 degrees
    map.drawparallels(np.arange(-90., 120., 5.),labels=[1,0,0,0])
    map.drawmeridians(np.arange(-180.,180., 5.),labels=[0,0,0,1])
    # create a grid for the data to be plotted on 
    llons, llats = np.meshgrid(lons, lats)
    x,y = map(llons,llats)
    norm = BoundaryNorm(levels, len(levels)-1)
    # Plot the data by colour over the meshgrid
    cs = map.pcolormesh(x, y, data=data, norm=norm, cmap = colormap) 
    if titles_on:
        # label with title, latitude, longitude, and colormap
        plt.title(title)
        plt.xlabel("\nLongitude")
        plt.ylabel("Latitude\n\n")
        cbar = plt.colorbar(ticks = levels[:-1], shrink = 0.6, extend = "max")
        cbar.ax.set_ylabel(cmap_label)
        cbar.ax.set_xticklabels(levels)
    return

def map_BARRA(data, lats, lons, lon_min = 135, lon_max = 155, lat_min = -45, lat_max = -30, titles_on = True, title = "BARRA-R precipitation", levels = levels["year"], colormap = prcp_colormap, cmap_label = "Precipitation (mm)"):
    """
This function takes a 2D data set of a variable from BARRA and maps the data on miller projection. 
The map default span is longitude between 135E and 155E, and the span for latitudes is -45 to -30, this is SE Australia. 
The colour scale is YlGnBu at 11 levels. 
The levels specifed are suitable for annual rainfall totals for SE Australia. 
From the BARRA average netCDF, the mean prcp should be multiplied by 24*365
"""
#    lats.sort() #this doesn't do anything for BARRA
#    lons.sort() #this doesn't do anything for BARRA
    map = Basemap(projection = "mill", llcrnrlon = lon_min, llcrnrlat = lat_min, urcrnrlon = lon_max, urcrnrlat = lat_max, resolution = 'l')
    map.drawcoastlines()
    map.drawmapboundary()
    map.drawparallels(np.arange(-90., 120., 5.),labels=[1,0,0,0])
    map.drawmeridians(np.arange(-180.,180., 5.),labels=[0,0,0,1])
    llons, llats = np.meshgrid(lons, lats)
    x,y = map(llons,llats)
    norm = BoundaryNorm(levels, len(levels)-1)
    cs = map.pcolormesh(x, y, data, norm = norm, cmap = colormap) 
    if titles_on:
        # label with title, latitude, longitude, and colormap
        plt.title(title)
        plt.xlabel("\n\nLongitude")
        plt.ylabel("Latitude\n\n")
        cbar = plt.colorbar(ticks = levels[:-1], shrink = 0.8, extend = "max")
        cbar.ax.set_ylabel(cmap_label)
        cbar.ax.set_xticklabels(levels)
    #plt.savefig(f"/home/563/gt3409/Documents/images/BARRA_day/BARRA_day_{rain_date.strftime('%Y%m%d')}")
    return


def map_AWAP_above_BARRA(AWAP_data, AWAP_lats, AWAP_lons, BARRA_data, BARRA_lats, BARRA_lons, AWAP_multiplier = 1, BARRA_multiplier = 1, levels = levels["year"], colormap = prcp_colormap, cmap_label = "Precipitation (mm)"):
    """
This function takes AWAP data and coordinates and BARRA data and coordinates, and maps AWAP on top of the map of BARRA. The plots are labeled "AWAP" and "BARRA-R" respectively. They share a common colorbar for scale.
This function requires: 
 load_2D_netCDF()
 map_AWAP()
 map_BARRA()
"""
    # Create a new figure
    fig = plt.figure(figsize=(6, 8))
    # Map AWAP on the top plot
    ax = fig.add_subplot(211)
    ax.set_title("AWAP", fontsize = 16)
    map_AWAP(AWAP_data*AWAP_multiplier, AWAP_lats, AWAP_lons, titles_on = False, colormap= colormap, levels= levels)
    # Map BARRA on the bottom plot
    ax = fig.add_subplot(212)
    ax.set_title("BARRA-R", fontsize = 16)
    map_BARRA(BARRA_data*BARRA_multiplier, BARRA_lats, BARRA_lons, titles_on = False, colormap= colormap, levels= levels)
    # Add a common colour bar
    ax = fig.add_axes([0.87,0.2,0.02,0.6])
    cbar = plt.colorbar(cax = ax, ticks = levels[:-1], extend = "max")
    cbar.ax.set_ylabel(cmap_label)
    cbar.ax.set_xticklabels(levels)
    #save
    plt.tight_layout(pad=2)
    return

