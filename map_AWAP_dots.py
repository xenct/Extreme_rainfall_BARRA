
def map_AWAP_dots(data, lats, lons, dot_color, lon_min = 135, lon_max = 155, lat_min = -45, lat_max = -30, titles_on = True, title = "AWAP Precipitation", levels = levels["year"], colormap = prcp_colormap, cmap_label = "Precipitation (mm)"):
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
    
    x,y = map(list(AWS_info['lon']), list(AWS_info['lat']))   
    map.scatter(x, y, c=dot_color, s= 50, norm=norm, cmap = colormap, edgecolors='k')


    if titles_on:
        # label with title, latitude, longitude, and colormap
        plt.title(title)
        plt.xlabel("\n\nLongitude")
        plt.ylabel("Latitude\n\n")
        cbar = plt.colorbar(ticks = levels[:-1], shrink = 0.8, extend = "max")
        cbar.ax.set_ylabel(cmap_label)
        cbar.ax.set_xticklabels(levels)
    return
